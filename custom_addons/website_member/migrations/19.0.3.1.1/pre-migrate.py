# -*- coding: utf-8 -*-
"""Rename member.directory.field → member.field BEFORE data XML reload.

end-migrate is too late: ir.model.data still points at the old model name
and env['member.directory.field'] KeyErrors while loading profile_fields.xml.
"""


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


def migrate(cr, version):
    _rename_table(cr, "member_directory_field", "member_field")
    _rename_table(cr, "member_directory_field_group_rel", "member_field_group_rel")
    _rename_column(cr, "res_users", "directory_published", "members_published")
    _rename_column(cr, "res_users", "directory_subtitle", "members_subtitle")

    # name is jsonb (translated); only rename the technical model key
    cr.execute(
        "UPDATE ir_model SET model = 'member.field' "
        "WHERE model = 'member.directory.field'"
    )
    # Critical: xmlids must resolve to the new Python model name
    cr.execute(
        "UPDATE ir_model_data SET model = 'member.field' "
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
        "UPDATE ir_model_data SET name = replace(name, 'model_member_directory_field', 'model_member_field') "
        "WHERE name LIKE '%model_member_directory_field%'"
    )
    cr.execute(
        "UPDATE ir_model_access SET name = replace(name, 'member.directory.field', 'member.field') "
        "WHERE name LIKE '%member.directory.field%'"
    )
    # Access rules reference model via model_id; also fix csv xmlid model names if stored
    cr.execute(
        """
        UPDATE ir_model_data
           SET name = replace(name, 'member_directory_field', 'member_field')
         WHERE module = 'website_member'
           AND name LIKE '%member_directory_field%'
        """
    )
