$ErrorActionPreference='Stop'
$env:CODEX_DOCUMENT_NODE='C:/Program Files/WindowsApps/OpenAI.CodexPrimaryRuntime.v26-1123-915-0_26.1123.915.0_x64__3k8sg7r9htsxt/dependencies/node/bin/node.exe'
if (Get-Process -Id 20928 -ErrorAction SilentlyContinue) { Wait-Process -Id 20928 }
if ((Get-Content -LiteralPath 'tmp/actualizacion_documental/relaciones-final.log' -Raw) -match 'Traceback') { throw 'Relaciones incompletas; no continuar.' }
foreach ($mode in @('defaults-clases','capas')) {
    python generadorDocumento/ea/sincronizar_documentacion.py $mode *> "tmp/actualizacion_documental/$mode-final.log"
    if ($LASTEXITCODE -ne 0) { throw "Fallo en $mode" }
}
$complete=$false
for ($batch=1; $batch -le 30; $batch++) {
    $log="tmp/actualizacion_documental/interacciones-v3-lote-$batch.log"
    python generadorDocumento/ea/actualizar_interacciones.py reanudar 80 *> $log
    if ($LASTEXITCODE -ne 0) { throw "Fallo de interacciones, lote $batch. Revisar $log antes de reanudar." }
    if ((Get-Content -LiteralPath $log -Raw) -match 'INTERACCIONES_COMPLETAS') { $complete=$true; break }
}
if (-not $complete) { throw 'Interacciones sin terminar: revisar trazas.' }
foreach ($mode in @('conceptual','despliegue')) {
    python generadorDocumento/ea/actualizar_datos_despliegue.py $mode *> "tmp/actualizacion_documental/$mode-final.log"
    if ($LASTEXITCODE -ne 0) { throw "Fallo en $mode" }
}
foreach ($mode in @('navegacion','base')) {
    python generadorDocumento/ea/actualizar_navegacion.py $mode *> "tmp/actualizacion_documental/$mode-final.log"
    if ($LASTEXITCODE -ne 0) { throw "Fallo en $mode" }
}
Write-Output 'MODELO_EXPORTADO_REQUIERE_REVISION'
