# -*- coding: utf-8 -*-
"""Clean LIFRAS profile fields: drop legacy CFPS boolean / wrong placements."""


def migrate(cr, version):
    from odoo import api, SUPERUSER_ID

    env = api.Environment(cr, SUPERUSER_ID, {})
    Field = env["member.field"].sudo()
    specialties = env["member.section"].sudo().search([("code", "=", "specialties")], limit=1)

    # Legacy boolean CFPS + import leftovers must not pollute LIFRAS on the website.
    legacy = Field.search([
        ("field_name", "in", ["dive_cfps", "dive_cfps_start", "dive_nitrox_basic_date"]),
    ])
    if legacy:
        legacy.write({"active": False, "show_on_backend": False})

    # Canonical fin CFPS belongs with specialties (with dive_spec_cfps).
    fin = Field.search([("field_name", "=", "dive_cfps_end")], limit=1)
    if fin and specialties:
        fin.write({
            "section_id": specialties.id,
            "active": True,
            "name": "Fin validite CFPS",
        })

    Field._sync_backend_custom_view()
