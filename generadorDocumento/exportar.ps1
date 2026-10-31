# Exporta el PUDS con Word real, conservando diagramas vectoriales y actualizando los índices.
# Los entregables se reemplazan solo después de generar ambos archivos en una carpeta temporal.
param([string]$Docx = (Join-Path $PSScriptRoot 'documento\P2-INF513-GRUPO05SA.docx'))
$ErrorActionPreference = 'Stop'
$Docx = (Resolve-Path -LiteralPath $Docx).Path
$destino = Split-Path -Parent $Docx
$nombre = [IO.Path]::GetFileNameWithoutExtension($Docx)
$temporal = Join-Path ([IO.Path]::GetTempPath()) ('p2-word-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $temporal | Out-Null
$base = Join-Path $temporal $nombre
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
$documento = $null
try {
    $documento = $word.Documents.Open($Docx)
    foreach ($figura in @($documento.InlineShapes)) {
        $ruta = $figura.AlternativeText
        if ($ruta -and $ruta.EndsWith('.png')) {
            $emf = [IO.Path]::ChangeExtension($ruta, '.emf')
            if (Test-Path -LiteralPath $emf) {
                $rango = $figura.Range
                $ancho = $figura.Width
                $alto = $figura.Height
                $figura.Delete()
                $nueva = $documento.InlineShapes.AddPicture($emf, $false, $true, $rango)
                $nueva.LockAspectRatio = -1
                $nueva.Width = $ancho
                if ($nueva.Height -gt $alto) { $nueva.Height = $alto }
                $nueva.AlternativeText = $emf
            }
        }
    }
    $documento.Fields.Update() | Out-Null
    $documento.SaveAs2("$base.doc", 0)
    # La conversión al formato .doc puede cambiar la paginación: actualizar después de convertir.
    for ($pasada = 0; $pasada -lt 3; $pasada++) {
        $documento.Repaginate()
        foreach ($indice in $documento.TablesOfContents) { $indice.Update() }
        foreach ($indice in $documento.TablesOfFigures) { $indice.Update() }
    }
    # Word vuelve a crear el párrafo final al actualizar números: reducirlo DESPUÉS de actualizar.
    for ($ajuste = 0; $ajuste -lt 2; $ajuste++) {
      $documento.Repaginate()
      foreach ($indice in $documento.TablesOfContents) { $indice.UpdatePageNumbers() }
      foreach ($indice in $documento.TablesOfFigures) { $indice.UpdatePageNumbers() }
      foreach ($indice in $documento.TablesOfContents) {
        $rango = $documento.Range($indice.Range.End - 1, $indice.Range.End)
        $parrafo = $rango.Paragraphs.Item(1)
        if ($parrafo.Range.Text.Trim().Length -eq 0) {
            $parrafo.Range.Font.Size = 1
            $parrafo.Format.SpaceBefore = 0
            $parrafo.Format.SpaceAfter = 0
            $parrafo.Format.LineSpacingRule = 4
            $parrafo.Format.LineSpacing = 1
        }
      }
      foreach ($titulo in @('ÍNDICE DE FIGURAS', 'ÍNDICE DE TABLAS')) {
        $buscar = $documento.Content
        if ($buscar.Find.Execute($titulo)) {
            $encabezado = $buscar.Paragraphs.Item(1)
            $anterior = $encabezado.Previous()
            if ($anterior.Range.Text.Trim().Length -eq 0) {
                # Conservar el fin del campo, pero unir su párrafo vacío al siguiente título.
                $anterior.Range.Font.Size = 1
                $anterior.Format.SpaceBefore = 0
                $anterior.Format.SpaceAfter = 0
                $anterior.Format.LineSpacingRule = 4
                $anterior.Format.LineSpacing = 1
                $anterior.Format.PageBreakBefore = -1
                $anterior.Format.KeepWithNext = -1
                $encabezado.Format.PageBreakBefore = 0
            }
        }
      }
    }
    $documento.Repaginate()
    $documento.Save()
    $documento.ExportAsFixedFormat("$base.pdf", 17)
    $paginas = $documento.ComputeStatistics(2)
    # Entregar también el DOCX con las figuras vectoriales y los campos ya actualizados.
    $documento.SaveAs2("$base.docx", 16)
    $documento.Close(0)
    $documento = $null
} finally {
    if ($null -ne $documento) { try { $documento.Close(0) } catch {} }
    $word.Quit()
}
foreach ($extension in @('doc', 'docx', 'pdf')) {
    if ((Get-Item -LiteralPath "$base.$extension").Length -eq 0) {
        throw "La exportación produjo un archivo vacío: $extension"
    }
}
foreach ($extension in @('doc', 'docx', 'pdf')) {
    Copy-Item -LiteralPath "$base.$extension" -Destination (Join-Path $destino "$nombre.$extension") -Force
}
Write-Output "paginas: $paginas"
Write-Output "Exportación temporal conservada: $temporal"
