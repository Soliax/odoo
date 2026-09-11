# Upgrade website modules and force homepage reset (stop-after-init).
param(
    [string]$Database = "odoo19-dev"
)

$Root = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $Root ".venv\Scripts\python.exe"
$OdooBin = Join-Path $Root "odoo\odoo-bin"
$Conf = Join-Path $Root "odoo.conf"

$env:Path = "C:\Program Files\PostgreSQL\16\bin;" + $env:Path
Set-Location (Join-Path $Root "odoo")

Write-Host "Upgrading website_member + website_wdc on $Database ..."
& $Python $OdooBin -c $Conf -d $Database -i website_wdc -u website_member,website_wdc --stop-after-init
if ($LASTEXITCODE -ne 0) {
    Write-Error "Upgrade failed with exit $LASTEXITCODE"
    exit $LASTEXITCODE
}
Write-Host "Done. Restart Odoo (scripts\start-odoo.cmd) then hard-refresh http://localhost:8069/"
