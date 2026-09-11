# -*- coding: utf-8 -*-
"""Reset COW event-card views so top-left category seals load."""

from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    View = env["ir.ui.view"].sudo()
    View.search([
        ("key", "in", [
            "website_member.md_event_card",
            "website_member.md_event_card_inner",
        ]),
        ("website_id", "!=", False),
    ]).unlink()
