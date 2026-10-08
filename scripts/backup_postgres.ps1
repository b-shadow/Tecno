param(
  [string]$Database = "crm_educativo",
  [string]$User = "crm_user",
  [string]$HostName = "127.0.0.1",
  [string]$Port = "5432",
  [string]$OutputDir = ".\backups"
)

if (-not (Test-Path $OutputDir)) {
  New-Item -ItemType Directory -Path $OutputDir | Out-Null
}

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$file = Join-Path $OutputDir "$Database`_$timestamp.dump"

pg_dump -h $HostName -p $Port -U $User -F c -d $Database -f $file

Write-Output "Backup generado: $file"
