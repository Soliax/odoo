# -*- coding: utf-8 -*-
"""Reset COW members views so the filters host is present."""

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
            "website_member.s_md_members_results",
        ]),
        ("website_id", "!=", False),
    ]).unlink()
