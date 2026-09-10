param(
    [Parameter(Mandatory = $true)]
    [string]$Name,
    [string]$DisplayName = ""
)

function Write-Utf8NoBom {
    param([string]$Path, [string]$Content)
    $dir = Split-Path -Parent $Path
    if ($dir -and -not (Test-Path $dir)) {
        New-Item -ItemType Directory -Force -Path $dir | Out-Null
    }
    $utf8 = New-Object System.Text.UTF8Encoding $false
    [System.IO.File]::WriteAllText($Path, $Content.Replace("`r`n", "`n"), $utf8)
}

if ($Name -notmatch '^[a-z][a-z0-9_]*$') {
    Write-Error "Module technical name must be lowercase letters/digits/underscore, starting with a letter."
    exit 1
}

if (-not $DisplayName) {
    $DisplayName = ($Name -replace '_', ' ')
    $DisplayName = $DisplayName.Substring(0, 1).ToUpper() + $DisplayName.Substring(1)
}

$Root = Split-Path -Parent $PSScriptRoot
$Mod = Join-Path $Root "custom_addons\$Name"

if (Test-Path $Mod) {
    Write-Error "Module already exists: $Mod"
    exit 1
}

New-Item -ItemType Directory -Force -Path @(
    $Mod,
    "$Mod\models",
    "$Mod\views",
    "$Mod\security",
    "$Mod\static\description"
) | Out-Null

$className = ($Name -split '_' | ForEach-Object {
    if ($_.Length -gt 0) { $_.Substring(0, 1).ToUpper() + $_.Substring(1) }
}) -join ''

Write-Utf8NoBom "$Mod\__manifest__.py" @"
# -*- coding: utf-8 -*-
{
    'name': '$DisplayName',
    'version': '19.0.1.0.0',
    'category': 'Custom',
    'summary': 'Custom module for $DisplayName',
    'author': 'Independent Developer',
    'license': 'LGPL-3',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/menus.xml',
    ],
    'installable': True,
    'application': True,
}
"@

Write-Utf8NoBom "$Mod\__init__.py" @"
# -*- coding: utf-8 -*-
from . import models
"@

Write-Utf8NoBom "$Mod\models\__init__.py" @"
# -*- coding: utf-8 -*-
from . import models
"@

Write-Utf8NoBom "$Mod\models\models.py" @"
# -*- coding: utf-8 -*-
from odoo import fields, models


class $className(models.Model):
    _name = '$Name.$Name'
    _description = '$DisplayName'

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    notes = fields.Text()
"@

Write-Utf8NoBom "$Mod\security\ir.model.access.csv" @"
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_${Name}_${Name}_user,$Name.$Name.user,model_${Name}_${Name},base.group_user,1,1,1,1
"@

Write-Utf8NoBom "$Mod\views\menus.xml" @"
<?xml version=`"1.0`" encoding=`"utf-8`"?>
<odoo>
    <record id=`"view_${Name}_tree`" model=`"ir.ui.view`">
        <field name=`"name`">$Name.$Name.list</field>
        <field name=`"model`">$Name.$Name</field>
        <field name=`"arch`" type=`"xml`">
            <list>
                <field name=`"name`"/>
                <field name=`"active`"/>
            </list>
        </field>
    </record>

    <record id=`"view_${Name}_form`" model=`"ir.ui.view`">
        <field name=`"name`">$Name.$Name.form</field>
        <field name=`"model`">$Name.$Name</field>
        <field name=`"arch`" type=`"xml`">
            <form>
                <sheet>
                    <group>
                        <field name=`"name`"/>
                        <field name=`"active`"/>
                        <field name=`"notes`"/>
                    </group>
                </sheet>
            </form>
        </field>
    </record>

    <record id=`"action_${Name}`" model=`"ir.actions.act_window`">
        <field name=`"name`">$DisplayName</field>
        <field name=`"res_model`">$Name.$Name</field>
        <field name=`"view_mode`">list,form</field>
    </record>

    <menuitem id=`"menu_${Name}_root`" name=`"$DisplayName`" sequence=`"100`"/>
    <menuitem id=`"menu_${Name}`" name=`"$DisplayName`" parent=`"menu_${Name}_root`" action=`"action_${Name}`" sequence=`"10`"/>
</odoo>
"@

Write-Host "Created module skeleton: $Mod"
Write-Host "Install with: .\scripts\start-odoo.ps1 -ExtraArgs `"-i $Name`""
Write-Host "Or Apps -> Update Apps List -> install '$DisplayName' (developer mode)."
