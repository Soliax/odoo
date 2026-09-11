# -*- coding: utf-8 -*-
"""Ensure members_* columns exist and website COW views are cleared."""

from odoo import SUPERUSER_ID, api


def _rename_column(cr, table, old, new):
    cr.execute(
        """
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = %s AND column_name = %s
        """,
        (table, old),
    )
    if cr.fetchone():
        cr.execute(
            """
            SELECT 1 FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = %s AND column_name = %s
            """,
            (table, new),
        )
        if not cr.fetchone():
            cr.execute('ALTER TABLE "%s" RENAME COLUMN "%s" TO "%s"' % (table, old, new))


def migrate(cr, version):
    _rename_column(cr, "res_users", "directory_published", "members_published")
    _rename_column(cr, "res_users", "directory_subtitle", "members_subtitle")
    cr.execute(
        """
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'member_directory_field'
        """
    )
    if cr.fetchone():
        cr.execute(
            """
            SELECT 1 FROM information_schema.tables
            WHERE table_schema = 'public' AND table_name = 'member_field'
            """
        )
        if not cr.fetchone():
            cr.execute('ALTER TABLE member_directory_field RENAME TO member_field')
    cr.execute(
        "UPDATE ir_model SET model = 'member.field' WHERE model = 'member.directory.field'"
    )

    env = api.Environment(cr, SUPERUSER_ID, {})
    # Also clear homepage COW from member upgrade path
    try:
        from odoo.addons.website_wdc.hooks import _reset_website_pages
        _reset_website_pages(env)
    except Exception:
        View = env["ir.ui.view"].sudo()
        View.search([
            ("key", "in", ["website.homepage", "website.contactus"]),
            ("website_id", "!=", False),
        ]).unlink()
