# -*- coding: utf-8 -*-
"""Ensure Plongeur / HSA profile fields exist and Club Plongee placement is synced."""


def migrate(cr, version):
    from odoo import api, SUPERUSER_ID

    env = api.Environment(cr, SUPERUSER_ID, {})
    Field = env["member.field"].sudo()
    Widget = env["member.widget"].sudo()
    Section = env["member.section"].sudo()

    boolean = Widget.search([("code", "=", "boolean")], limit=1) or env.ref(
        "website_member.widget_boolean", raise_if_not_found=False
    )
    club = Section.search([("code", "=", "club")], limit=1) or env.ref(
        "website_member.section_club", raise_if_not_found=False
    )
    if boolean and club:
        specs = [
            ("dive_is_plongeur", "Plongeur", 20),
            ("dive_is_hsa", "HSA (Hockey subaquatique)", 30),
        ]
        for fname, label, seq in specs:
            existing = Field.search([
                ("field_name", "=", fname),
                ("source_model", "=", "res.partner"),
            ], limit=1)
            if existing:
                existing.write({
                    "section_id": club.id,
                    "show_on_backend": True,
                    "widget_id": boolean.id,
                    "active": True,
                })
            else:
                Field.create({
                    "name": label,
                    "source_model": "res.partner",
                    "field_name": fname,
                    "widget_id": boolean.id,
                    "section_id": club.id,
                    "show_on_backend": True,
                    "sequence": seq,
                    "is_custom": False,
                })

    Field._sync_backend_custom_view()
