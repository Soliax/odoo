# -*- coding: utf-8 -*-
"""Clear COW copies and rewrite saved member snippet option attributes."""

from odoo import SUPERUSER_ID, api


_OLD_FILTERS = 'data-show-filters="1"'
_NEW_ATTRS = (
    'data-md-options="1" '
    'data-show-brevets-filters="1" '
    'data-show-specialties-filters="1" '
    'data-show-categories-filters="1" '
    'data-tcg-visual="1"'
)


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    View = env["ir.ui.view"].sudo()

    # Drop website-specific overrides so module templates win again.
    View.search([
        ("key", "in", [
            "website_member.members_list",
            "website_member.s_md_members",
            "website_member.s_md_members_content",
            "website_member.md_tcg_card",
            "website_member.md_event_card",
        ]),
        ("website_id", "!=", False),
    ]).unlink()

    # Rewrite embedded snippets on saved pages (oe_structure content).
    candidates = View.search([("arch_db", "ilike", "s_md_members")])
    for view in candidates:
        arch = view.arch_db or ""
        if _OLD_FILTERS not in arch and 'data-show-specialties="' not in arch:
            continue
        updated = (
            arch.replace(_OLD_FILTERS, _NEW_ATTRS)
                .replace('data-show-specialties="1"', "")
                .replace('data-show-specialties="0"', "")
                .replace('data-category=""', "")
                .replace('data-category="all"', "")
        )
        if updated != arch:
            view.write({"arch_db": updated})
