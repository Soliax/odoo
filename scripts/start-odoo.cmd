@echo off
REM Bypass ExecutionPolicy for this one script so double-click / cmd works.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0start-odoo.ps1" %*
