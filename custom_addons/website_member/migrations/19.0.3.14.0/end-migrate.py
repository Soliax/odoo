# -*- coding: utf-8 -*-
"""Migrate member.field.section selection → member.section + section_id."""


def migrate(cr, version):
    from odoo import api, SUPERUSER_ID

    cr.execute(
        """
        SELECT column_name FROM information_schema.columns
        WHERE table_name = 'member_field' AND column_name = 'section'
        """
    )
    has_legacy = bool(cr.fetchone())
    if has_legacy:
        cr.execute(
            """
            ALTER TABLE member_field
            ADD COLUMN IF NOT EXISTS section_legacy varchar
            """
        )
        cr.execute(
            """
            UPDATE member_field
               SET section_legacy = section
             WHERE section_legacy IS NULL AND section IS NOT NULL
            """
        )

    env = api.Environment(cr, SUPERUSER_ID, {})
    env["member.section"]._ensure_defaults()
    Section = env["member.section"].sudo()
    Field = env["member.field"].sudo()

    # Map by legacy code if column still present in DB values
    if has_legacy:
        cr.execute("SELECT id, section_legacy FROM member_field WHERE section_id IS NULL")
        rows = cr.fetchall()
        by_code = {s.code: s.id for s in Section.search([])}
        extra = by_code.get("extra") or Section.search([], limit=1).id
        for field_id, code in rows:
            section_id = by_code.get(code) or extra
            cr.execute(
                "UPDATE member_field SET section_id = %s WHERE id = %s",
                (section_id, field_id),
            )

    # Any remaining without section_id
    orphan = Field.search([("section_id", "=", False)])
    if orphan:
        extra = Section.search([("code", "=", "extra")], limit=1) or Section.search([], limit=1)
        orphan.write({"section_id": extra.id})

    env["member.field"]._sync_backend_custom_view()
