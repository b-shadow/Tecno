<#
.SYNOPSIS
  Inicia localmente PostgreSQL, Laravel API (puerto 8001) y React/Vite (puerto 5173) para UNEXO CRM.
.DESCRIPTION
  Verifica herramientas y configuración (.env sin sobrescribir), levanta solo los servicios que no estén
  activos (evita procesos duplicados), comprueba /api/salud y muestra las URLs locales.
  No ejecuta migrate:fresh, db:wipe ni seeders destructivos.
#>
[CmdletBinding()]
param(
    [switch]$SinStripe
)

$ErrorActionPreference = 'Stop'
$Raiz = $PSScriptRoot
$NegocioDir = Join-Path $Raiz 'negocio'
$PresentacionDir = Join-Path $Raiz 'presentacion'
$EstadoDir = Join-Path $env:LOCALAPPDATA 'UNEXO-CRM'
$PgData = if ($env:UNEXO_PGDATA) { $env:UNEXO_PGDATA } else { Join-Path $EstadoDir 'pgdata' }
$LogsDir = Join-Path $EstadoDir 'logs'
$PidsArchivo = Join-Path $EstadoDir 'pids.json'

New-Item -ItemType Directory -Force -Path $EstadoDir, $LogsDir | Out-Null

function Leer-Env([string]$Archivo) {
    $mapa = @{}
    if (-not (Test-Path $Archivo)) { return $mapa }
    foreach ($linea in Get-Content $Archivo) {
        if ($linea -match '^\s*#' -or $linea -notmatch '^\s*([^=]+?)\s*=\s*(.*)$') { continue }
        $clave = $Matches[1].Trim()
        $valor = $Matches[2].Trim().Trim('"').Trim("'")
        $mapa[$clave] = $valor
    }
    return $mapa
}

function Puerto-EnUso([int]$Puerto) {
    try {
        $con = Get-NetTCPConnection -LocalPort $Puerto -State Listen -ErrorAction SilentlyContinue
        return [bool]$con
    } catch {
        $cliente = New-Object System.Net.Sockets.TcpClient
        try {
            $res = $cliente.BeginConnect('127.0.0.1', $Puerto, $null, $null)
            if ($res.AsyncWaitHandle.WaitOne(300)) { $cliente.EndConnect($res); return $true }
            return $false
        } catch { return $false } finally { $cliente.Close() }
    }
}

function Buscar-PgBin {
    $cmd = Get-Command psql -ErrorAction SilentlyContinue
    if ($cmd) { return Split-Path $cmd.Source }
    $base = 'C:\Program Files\PostgreSQL'
    if (Test-Path $base) {
        $ver = Get-ChildItem $base -Directory | Sort-Object Name -Descending | Select-Object -First 1
        if ($ver -and (Test-Path (Join-Path $ver.FullName 'bin\pg_ctl.exe'))) {
            return (Join-Path $ver.FullName 'bin')
        }
    }
    return $null
}

Write-Host '=== UNEXO CRM · Arranque local (3 capas) ===' -ForegroundColor Cyan

# 1. Verificar herramientas
foreach ($herr in @('php', 'composer', 'node', 'npm')) {
    if (-not (Get-Command $herr -ErrorAction SilentlyContinue)) {
        throw "Falta la herramienta requerida '$herr' en el PATH."
    }
}
$PgBin = Buscar-PgBin
if (-not $PgBin) {
    throw 'No se encontró PostgreSQL (psql / pg_ctl). Instálelo o agréguelo al PATH.'
}

# 2. Configuración local (.env sin sobrescribir existentes)
$EnvNegocio = Join-Path $NegocioDir '.env'
$EnvPresentacion = Join-Path $PresentacionDir '.env'
if (-not (Test-Path $EnvNegocio)) {
    Copy-Item (Join-Path $NegocioDir '.env.example') $EnvNegocio
    Write-Host '[OK] Creado negocio/.env desde .env.example'
}
if (-not (Test-Path $EnvPresentacion)) {
    Copy-Item (Join-Path $PresentacionDir '.env.example') $EnvPresentacion
    Write-Host '[OK] Creado presentacion/.env desde .env.example'
}

$envCfg = Leer-Env $EnvNegocio
if (-not $envCfg['APP_KEY']) {
    Push-Location $NegocioDir
    try { & php artisan key:generate --force | Out-Null } finally { Pop-Location }
    $envCfg = Leer-Env $EnvNegocio
    Write-Host '[OK] Generada APP_KEY en negocio/.env'
}

# 3. Dependencias (solo si faltan)
if (-not (Test-Path (Join-Path $NegocioDir 'vendor\autoload.php'))) {
    Write-Host '[..] Instalando dependencias PHP (composer install)...'
    Push-Location $NegocioDir
    try { & composer install --no-interaction } finally { Pop-Location }
}
if (-not (Test-Path (Join-Path $PresentacionDir 'node_modules'))) {
    Write-Host '[..] Instalando dependencias JS (npm ci)...'
    Push-Location $PresentacionDir
    try { & npm ci } finally { Pop-Location }
}

$DbHost = if ($envCfg['DB_HOST']) { $envCfg['DB_HOST'] } else { '127.0.0.1' }
$DbPort = if ($envCfg['DB_PORT']) { [int]$envCfg['DB_PORT'] } else { 5432 }
$DbName = if ($envCfg['DB_DATABASE']) { $envCfg['DB_DATABASE'] } else { 'crm_educativo' }
$DbUser = if ($envCfg['DB_USERNAME']) { $envCfg['DB_USERNAME'] } else { 'crm_user' }
$DbPass = $envCfg['DB_PASSWORD']

$pids = @{}
if (Test-Path $PidsArchivo) {
    try {
        $obj = Get-Content $PidsArchivo -Raw | ConvertFrom-Json
        if ($obj) {
            foreach ($prop in $obj.PSObject.Properties) { $pids[$prop.Name] = $prop.Value }
        }
    } catch { $pids = @{} }
}

# 4. PostgreSQL (Capa 3)
$pgReady = & (Join-Path $PgBin 'pg_isready.exe') -h $DbHost -p $DbPort 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] PostgreSQL ya está activo en ${DbHost}:${DbPort}" -ForegroundColor Green
} else {
    if ($DbHost -notin @('127.0.0.1', 'localhost')) {
        throw "PostgreSQL remoto ($DbHost`:$DbPort) no responde."
    }
    $svc = Get-Service 'postgresql*' -ErrorAction SilentlyContinue | Select-Object -First 1
    $iniciadoPorSvc = $false
    if ($svc) {
        try {
            Start-Service $svc.Name -ErrorAction Stop
            $iniciadoPorSvc = $true
            Write-Host "[OK] Servicio $($svc.Name) iniciado." -ForegroundColor Green
        } catch {
            Write-Host "[INFO] Servicio Windows requiere privilegios; usando instancia local en $PgData" -ForegroundColor Yellow
        }
    }
    if (-not $iniciadoPorSvc) {
        $clusterNuevo = -not (Test-Path (Join-Path $PgData 'PG_VERSION'))
        if ($clusterNuevo) {
            Write-Host "[..] Inicializando instancia PostgreSQL local en $PgData..."
            & (Join-Path $PgBin 'initdb.exe') -D $PgData -U postgres -A trust -E UTF8 --locale=C | Out-Null
            Add-Content -Path (Join-Path $PgData 'postgresql.conf') -Value "`nunix_socket_directories = ''"
        }
        $pgLog = Join-Path $LogsDir 'postgres.log'
        $pgProc = Start-Process -FilePath (Join-Path $PgBin 'postgres.exe') -ArgumentList "-D `"$PgData`" -p $DbPort" -RedirectStandardOutput $pgLog -RedirectStandardError (Join-Path $LogsDir 'postgres.err.log') -WindowStyle Hidden -PassThru
        $pids['postgres'] = $pgProc.Id
        $pids['pgdata'] = $PgData
        $espera = 0
        while ($espera -lt 20) {
            & (Join-Path $PgBin 'pg_isready.exe') -h 127.0.0.1 -p $DbPort 2>$null | Out-Null
            if ($LASTEXITCODE -eq 0) { break }
            Start-Sleep -Milliseconds 500
            $espera++
        }
        if ($LASTEXITCODE -ne 0) { throw "No se pudo iniciar PostgreSQL local en el puerto $DbPort. Revise $pgLog" }
        if ($clusterNuevo) {
            $safePass = $DbPass -replace "'", "''"
            & (Join-Path $PgBin 'psql.exe') -h 127.0.0.1 -p $DbPort -U postgres -c "CREATE USER `"$DbUser`" WITH PASSWORD '$safePass' SUPERUSER;" | Out-Null
            & (Join-Path $PgBin 'psql.exe') -h 127.0.0.1 -p $DbPort -U postgres -c "CREATE DATABASE `"$DbName`" OWNER `"$DbUser`";" | Out-Null
            Write-Host "[OK] Base vacía '$DbName' creada; ejecute 'php artisan crm:preparar-bd && php artisan migrate' en negocio/." -ForegroundColor Yellow
        }
        Write-Host "[OK] PostgreSQL local iniciado (PID $($pgProc.Id), puerto $DbPort)" -ForegroundColor Green
    }
}

# Verificar conectividad real a la base configurada
$env:PGPASSWORD = $DbPass
& (Join-Path $PgBin 'psql.exe') -h $DbHost -p $DbPort -U $DbUser -d $DbName -c 'SELECT 1;' 2>$null | Out-Null
$psqlOk = ($LASTEXITCODE -eq 0)
$env:PGPASSWORD = $null
if (-not $psqlOk) {
    throw "PostgreSQL responde en ${DbHost}:${DbPort}, pero no se pudo conectar a la base '$DbName' con el usuario '$DbUser'. Revise negocio/.env o inicialice la BD."
}

# 5. Backend Laravel (Capa 2)
if (Puerto-EnUso 8001) {
    Write-Host '[OK] Backend Laravel ya está escuchando en el puerto 8001' -ForegroundColor Green
} else {
    $beOut = Join-Path $LogsDir 'laravel.out.log'
    $beErr = Join-Path $LogsDir 'laravel.err.log'
    $beProc = Start-Process -FilePath 'php' -ArgumentList 'artisan serve --host=127.0.0.1 --port=8001' -WorkingDirectory $NegocioDir -RedirectStandardOutput $beOut -RedirectStandardError $beErr -WindowStyle Hidden -PassThru
    $pids['laravel'] = $beProc.Id
    Write-Host "[OK] Backend Laravel iniciado (PID $($beProc.Id), puerto 8001)" -ForegroundColor Green
}

# 6. Frontend Vite (Capa 1)
if (Puerto-EnUso 5173) {
    Write-Host '[OK] Frontend Vite ya está escuchando en el puerto 5173' -ForegroundColor Green
} else {
    $feOut = Join-Path $LogsDir 'vite.out.log'
    $feErr = Join-Path $LogsDir 'vite.err.log'
    $feProc = Start-Process -FilePath 'cmd.exe' -ArgumentList '/c npm run dev' -WorkingDirectory $PresentacionDir -RedirectStandardOutput $feOut -RedirectStandardError $feErr -WindowStyle Hidden -PassThru
    $pids['vite'] = $feProc.Id
    Write-Host "[OK] Frontend React/Vite iniciado (PID $($feProc.Id), puerto 5173)" -ForegroundColor Green
}

function Buscar-StripeExe {
    $cmd = Get-Command stripe -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }
    $wingetLink = Join-Path $env:LOCALAPPDATA 'Microsoft\WinGet\Links\stripe.exe'
    if (Test-Path $wingetLink) { return $wingetLink }
    return $null
}

$pids | ConvertTo-Json | Set-Content -Path $PidsArchivo -Encoding UTF8

# 6b. Stripe CLI (webhooks locales hacia Laravel)
$StripeExe = Buscar-StripeExe
$StripeActiva = $false
if (-not $SinStripe -and $StripeExe -and $envCfg['STRIPE_SECRET'] -and $envCfg['STRIPE_SECRET'] -match '^sk_test_') {
    $yaEscucha = Get-CimInstance Win32_Process -Filter "Name = 'stripe.exe'" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -match 'forward-to' }
    if ($yaEscucha) {
        $StripeActiva = $true
        Write-Host '[OK] Stripe CLI ya está escuchando webhooks locales -> http://127.0.0.1:8001/api/stripe/webhook' -ForegroundColor Green
    } else {
        $stOut = Join-Path $LogsDir 'stripe.out.log'
        $stErr = Join-Path $LogsDir 'stripe.err.log'
        $stProc = Start-Process -FilePath $StripeExe -ArgumentList "listen --api-key `"$($envCfg['STRIPE_SECRET'])`" --all-snapshot --forward-to http://127.0.0.1:8001/api/stripe/webhook" -WorkingDirectory $NegocioDir -RedirectStandardOutput $stOut -RedirectStandardError $stErr -WindowStyle Hidden -PassThru
        $pids['stripe'] = $stProc.Id
        $pids | ConvertTo-Json | Set-Content -Path $PidsArchivo -Encoding UTF8
        $StripeActiva = $true
        Write-Host "[OK] Stripe CLI iniciado (PID $($stProc.Id)) -> /api/stripe/webhook" -ForegroundColor Green
    }
}

# 7. Comprobar /api/salud y frontend
$saludOk = $false
for ($i = 0; $i -lt 20; $i++) {
    try {
        $salud = Invoke-RestMethod -Uri 'http://127.0.0.1:8001/api/salud' -TimeoutSec 2
        if ($salud.base_de_datos -eq 'conectada') { $saludOk = $true; break }
    } catch {}
    Start-Sleep -Milliseconds 500
}
if (-not $saludOk) { throw 'El backend en http://127.0.0.1:8001/api/salud no respondió conectado.' }

$feOk = $false
for ($i = 0; $i -lt 30; $i++) {
    try {
        $resp = Invoke-WebRequest -Uri 'http://127.0.0.1:5173/anuncios' -UseBasicParsing -TimeoutSec 2
        if ($resp.StatusCode -eq 200) { $feOk = $true; break }
    } catch {}
    Start-Sleep -Milliseconds 500
}
if (-not $feOk) { throw 'El frontend en http://127.0.0.1:5173 no respondió a tiempo.' }

Write-Host ''
Write-Host 'Sistema UNEXO activo:' -ForegroundColor Cyan
Write-Host '  Frontend (React + Vite): http://localhost:5173/anuncios'
Write-Host '  Login:                   http://localhost:5173/login'
Write-Host '  API Salud (Laravel):     http://127.0.0.1:8001/api/salud'
Write-Host "  PostgreSQL:              ${DbHost}:${DbPort} (base: $DbName)"
if ($StripeActiva) {
    Write-Host '  Stripe CLI Webhook:      http://127.0.0.1:8001/api/stripe/webhook (activo)' -ForegroundColor Green
} else {
    Write-Host '  Stripe CLI Webhook:      stripe listen --all-snapshot --forward-to http://127.0.0.1:8001/api/stripe/webhook' -ForegroundColor Yellow
}
Write-Host '  Para detener los procesos iniciados por este script: .\detener-proyecto.ps1'
