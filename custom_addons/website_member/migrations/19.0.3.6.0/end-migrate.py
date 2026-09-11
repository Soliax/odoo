# -*- coding: utf-8 -*-
"""Reset COW copies of the member profile template so #wrap.oe_structure applies."""

from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    View = env["ir.ui.view"].sudo()
    View.search([
        ("key", "in", [
            "website_member.member_profile",
            "website_member.s_md_member_profile",
            "website_member.s_md_member_profile_content",
        ]),
        ("website_id", "!=", False),
    ]).unlink()

    base = View.search([
        ("key", "=", "website_member.member_profile"),
        ("website_id", "=", False),
    ], limit=1)
    if not base:
        base = View.search([("key", "=", "website_member.member_profile")], limit=1)
        if base:
            base.write({"website_id": False})
