# -*- coding: utf-8 -*-
"""Back to single content host (filters + results together)."""

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

    # Drop obsolete empty filters hosts from specialized page arches.
    for view in View.search([("arch_db", "ilike", "s_md_members_filters_host")]):
        arch = view.arch_db or ""
        if "s_md_members_filters_host" not in arch:
            continue
        import re
        new_arch = re.sub(
            r'\s*<div[^>]*\bs_md_members_filters_host\b[\s\S]*?</div>\s*',
            '\n',
            arch,
            count=1,
        )
        if new_arch != arch:
            view.write({"arch_db": new_arch})
