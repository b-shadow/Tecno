param(
  [Parameter(Mandatory = $true)][string]$BackupFile,
  [string]$Database = "crm_educativo",
  [string]$User = "crm_user",
  [string]$HostName = "127.0.0.1",
  [string]$Port = "5432"
)

if (-not (Test-Path $BackupFile)) {
  throw "No existe el archivo de backup: $BackupFile"
}

pg_restore -h $HostName -p $Port -U $User -d $Database --clean --if-exists $BackupFile

Write-Output "Backup restaurado en base: $Database"
