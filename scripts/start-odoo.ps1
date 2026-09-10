param(
    [string]$Database = "odoo19-dev",
    [string]$ExtraArgs = ""
)

$Root = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $Root ".venv\Scripts\python.exe"
$OdooBin = Join-Path $Root "odoo\odoo-bin"
$Conf = Join-Path $Root "odoo.conf"

if (-not (Test-Path $Python)) {
    Write-Error "Missing venv at $Python — run scripts\bootstrap.ps1 first."
    exit 1
}

$env:Path = "C:\Program Files\PostgreSQL\16\bin;" + $env:Path
Set-Location (Join-Path $Root "odoo")

$argList = @(
    $OdooBin,
    "-c", $Conf,
    "-d", $Database,
    "--dev=all"
)
if ($ExtraArgs) {
    $argList += $ExtraArgs.Split(" ")
}

Write-Host "Starting Odoo → http://localhost:8069  (db=$Database)"
& $Python @argList
