# -*- coding: utf-8 -*-
"""Reset /membres layout: no Intro title, event cards default (TCG off)."""

from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    View = env["ir.ui.view"].sudo()

    View.search([
        ("key", "in", [
            "website_member.members_list",
            "website_member.s_md_members",
            "website_member.s_md_members_content",
            "website_member.s_md_members_filters",
            "website_member.md_event_card",
            "website_member.md_event_card_inner",
        ]),
        ("website_id", "!=", False),
    ]).unlink()

    for view in View.search([
        ("key", "in", [
            "website_member.members_list",
            "website_member.s_md_members",
        ]),
    ]):
        arch = view.arch_db or ""
        if 'data-tcg-visual="1"' in arch:
            view.write({"arch_db": arch.replace('data-tcg-visual="1"', 'data-tcg-visual="0"')})
