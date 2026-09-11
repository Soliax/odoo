# -*- coding: utf-8 -*-
"""Clear website COW copies of members templates so the snippet-based page applies."""

from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    View = env["ir.ui.view"].sudo()
    View.search([
        ("key", "in", [
            "website_member.members_list",
            "website_member.member_profile",
            "website_member.s_md_members",
            "website_member.s_md_members_content",
            "website_member.md_tcg_card",
            "website_member.event_description_participants",
            "website_event.event_description_full",
        ]),
        ("website_id", "!=", False),
    ]).unlink()
