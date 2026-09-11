# -*- coding: utf-8 -*-
"""Rename directory -> members / member.field and reset stale website views."""

from odoo import SUPERUSER_ID, api


def _rename_table(cr, old, new):
    cr.execute(
        """
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = %s
        """,
        (old,),
    )
    if cr.fetchone():
        cr.execute(
            """
            SELECT 1 FROM information_schema.tables
            WHERE table_schema = 'public' AND table_name = %s
            """,
            (new,),
        )
        if not cr.fetchone():
            cr.execute('ALTER TABLE "%s" RENAME TO "%s"' % (old, new))


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


def _reset_website(env):
    View = env["ir.ui.view"].sudo()
    Page = env["website.page"].sudo()

    for key in (
        "website.homepage",
        "website.contactus",
        "website_member.members_list",
        "website_member.s_md_members",
        "website_member.s_md_members_content",
        "website_wdc.homepage",
        "website_wdc.contactus",
        "website_wdc.contact_block",
    ):
        View.search([("key", "=", key), ("website_id", "!=", False)]).unlink()

    for page in Page.search([]):
        url = (page.url or "").rstrip("/") or "/"
        arch = page.view_id.arch_db if page.view_id else ""
        arch = arch or ""
        if url in ("/membres", "/members"):
            page.write({"is_published": False, "website_indexed": False})
            continue
        if url.startswith("/event"):
            continue
        if "s_md_members" in arch or "data-border-card" in arch or "Annuaire du club" in arch:
            page.write({"is_published": False, "website_indexed": False})


def migrate(cr, version):
    _rename_table(cr, "member_directory_field", "member_field")
    _rename_table(cr, "member_directory_field_group_rel", "member_field_group_rel")
    _rename_column(cr, "res_users", "directory_published", "members_published")
    _rename_column(cr, "res_users", "directory_subtitle", "members_subtitle")

    cr.execute(
        "UPDATE ir_model SET model = 'member.field' "
        "WHERE model = 'member.directory.field'"
    )
    cr.execute(
        "UPDATE ir_model_data SET name = 'model_member_field' "
        "WHERE module = 'website_member' AND name = 'model_member_directory_field'"
    )
    cr.execute(
        "UPDATE ir_model_fields SET model = 'member.field' "
        "WHERE model = 'member.directory.field'"
    )
    cr.execute(
        "UPDATE ir_model_fields SET relation = 'member.field' "
        "WHERE relation = 'member.directory.field'"
    )
    cr.execute(
        "UPDATE ir_model_fields SET name = 'members_published' "
        "WHERE model = 'res.users' AND name = 'directory_published'"
    )
    cr.execute(
        "UPDATE ir_model_fields SET name = 'members_subtitle' "
        "WHERE model = 'res.users' AND name = 'directory_subtitle'"
    )
    cr.execute(
        "UPDATE ir_model_data SET name = replace(name, 'field_res_users__directory_', 'field_res_users__members_') "
        "WHERE module = 'website_member' AND name LIKE 'field_res_users__directory_%'"
    )
    cr.execute(
        "UPDATE ir_model_access SET name = replace(name, 'member.directory.field', 'member.field') "
        "WHERE name LIKE '%member.directory.field%'"
    )
    cr.execute(
        "UPDATE ir_ui_view SET name = replace(name, 'member.directory.field', 'member.field') "
        "WHERE name LIKE '%member.directory.field%'"
    )
    cr.execute(
        "UPDATE ir_ui_view SET name = replace(name, 'inherit.member.directory', 'inherit.members') "
        "WHERE name LIKE '%inherit.member.directory%'"
    )

    env = api.Environment(cr, SUPERUSER_ID, {})
    _reset_website(env)
