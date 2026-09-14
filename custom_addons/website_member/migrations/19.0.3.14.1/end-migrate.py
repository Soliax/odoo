# -*- coding: utf-8 -*-
"""Align Club / Profession sections with UI: Club holds role + member since."""


def migrate(cr, version):
    from odoo import api, SUPERUSER_ID

    env = api.Environment(cr, SUPERUSER_ID, {})
    Section = env["member.section"].sudo()
    Field = env["member.field"].sudo()
    Imd = env["ir.model.data"].sudo()

    env["member.section"]._ensure_defaults()

    professional = Section.search([("code", "=", "professional")], limit=1)
    if professional:
        professional.write({"name": "Profession", "sequence": 40})

    club = Section.search([("code", "=", "club")], limit=1)
    if not club:
        club = Section.create({"code": "club", "name": "Club", "sequence": 45})
    else:
        club.write({"name": "Club", "sequence": 45})

    # Dedupe accidental double Club sections from UI + data load
    for dup in Section.search([("code", "=", "club")]) - club:
        Field.search([("section_id", "=", dup.id)]).write({"section_id": club.id})
        dup.unlink()

    # Bind xmlid for club section (may have been created from UI)
    existing = Imd.search([
        ("module", "=", "website_member"),
        ("name", "=", "section_club"),
    ], limit=1)
    if existing:
        if existing.model != "member.section" or existing.res_id != club.id:
            existing.write({
                "model": "member.section",
                "res_id": club.id,
                "noupdate": True,
            })
    else:
        Imd.create({
            "module": "website_member",
            "name": "section_club",
            "model": "member.section",
            "res_id": club.id,
            "noupdate": True,
        })

    for fname, label, sequence in (
        ("dive_member_since", "Membre depuis", 10),
        ("function", "Rôle", 20),
    ):
        rec = Field.search([
            ("field_name", "=", fname),
            ("source_model", "=", "res.partner"),
        ], limit=1)
        if rec:
            rec.write({
                "name": label,
                "section_id": club.id,
                "sequence": sequence,
            })
