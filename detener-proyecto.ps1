<#
.SYNOPSIS
  Detiene únicamente los procesos locales iniciados por iniciar-proyecto.ps1.
#>
[CmdletBinding()]
param()

$ErrorActionPreference = 'SilentlyContinue'
$EstadoDir = Join-Path $env:LOCALAPPDATA 'UNEXO-CRM'
$PidsArchivo = Join-Path $EstadoDir 'pids.json'

if (-not (Test-Path $PidsArchivo)) {
    Write-Host 'No hay procesos registrados por iniciar-proyecto.ps1.'
    exit 0
}

$pids = Get-Content $PidsArchivo -Raw | ConvertFrom-Json

function Buscar-PgBin {
    $base = 'C:\Program Files\PostgreSQL'
    if (Test-Path $base) {
        $ver = Get-ChildItem $base -Directory | Sort-Object Name -Descending | Select-Object -First 1
        if ($ver -and (Test-Path (Join-Path $ver.FullName 'bin\pg_ctl.exe'))) {
            return (Join-Path $ver.FullName 'bin')
        }
    }
    return $null
}

foreach ($clave in @('vite', 'laravel', 'stripe', 'scheduler')) {
    $procId = $pids.$clave
    if ($procId) {
        $p = Get-Process -Id $procId -ErrorAction SilentlyContinue
        if ($p) {
            # En Windows, npm run dev abre cmd.exe -> node.exe; taskkill /T cierra el árbol del proceso iniciado.
            & taskkill /PID $procId /T /F 2>$null | Out-Null
            Write-Host "[OK] Detenido $clave (PID $procId)"
        }
    }
}

if ($pids.postgres) {
    $pgBin = Buscar-PgBin
    $pgData = $pids.pgdata
    if ($pgBin -and $pgData -and (Test-Path (Join-Path $pgData 'postmaster.pid'))) {
        & (Join-Path $pgBin 'pg_ctl.exe') -D $pgData stop -m fast | Out-Null
        Write-Host "[OK] Detenido PostgreSQL local ($pgData)"
    } else {
        $p = Get-Process -Id $pids.postgres -ErrorAction SilentlyContinue
        if ($p) { Stop-Process -Id $pids.postgres; Write-Host "[OK] Detenido PostgreSQL (PID $($pids.postgres))" }
    }
}

Remove-Item $PidsArchivo -Force -ErrorAction SilentlyContinue
Write-Host 'Servicios del proyecto detenidos.'
