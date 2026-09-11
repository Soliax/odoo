# -*- coding: utf-8 -*-
"""Promote /membres to a real website.page and reset locked COW views."""

from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    View = env["ir.ui.view"].sudo()
    Page = env["website.page"].sudo()
    Menu = env["website.menu"].sudo()

    View.search([
        ("key", "in", [
            "website_member.members_list",
            "website_member.s_md_members",
            "website_member.s_md_members_content",
        ]),
        ("website_id", "!=", False),
    ]).unlink()

    base_view = View.search([
        ("key", "=", "website_member.members_list"),
        ("website_id", "=", False),
    ], limit=1)
    if not base_view:
        base_view = View.search([("key", "=", "website_member.members_list")], limit=1)
        if base_view:
            base_view.write({"website_id": False})
    if not base_view:
        return

    for website in env["website"].sudo().search([]):
        pages = Page.search([
            ("url", "=", "/membres"),
            "|", ("website_id", "=", website.id), ("website_id", "=", False),
        ], order="id")
        vals = {
            "name": "Membres",
            "url": "/membres",
            "view_id": base_view.id,
            "is_published": True,
            "website_id": website.id,
            "website_indexed": False,
        }
        if pages:
            keep = pages[0]
            keep.write(vals)
            (pages - keep).unlink()
            page = keep
        else:
            page = Page.create(vals)

        menus = Menu.search([
            ("website_id", "=", website.id),
            ("url", "in", ["/membres", "/members"]),
        ])
        menus.write({"page_id": page.id, "url": "/membres"})
