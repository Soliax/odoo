# Odoo 19 — independent module development

Local workspace for custom Odoo 19 modules (Community source install).

## Layout

- `custom_addons/` — your modules (tracked)
- `scripts/` — start / scaffold helpers
- `odoo/` — clone [odoo/odoo](https://github.com/odoo/odoo) branch `19.0` locally (gitignored)
- `tutorials/` — optional clone of [odoo/tutorials](https://github.com/odoo/tutorials) (gitignored)
- `odoo.conf.example` — copy to `odoo.conf` and adapt paths / DB credentials

## Quick start

```powershell
git clone git@github.com:Soliax/odoo.git
cd odoo
git clone --branch 19.0 --single-branch --depth 1 https://github.com/odoo/odoo.git odoo
py -3.11 -m venv .venv
.\.venv\Scripts\pip install -r odoo\requirements.txt
Copy-Item odoo.conf.example odoo.conf
.\scripts\start-odoo.ps1
```

Login: `admin` / `admin` · http://127.0.0.1:8069
