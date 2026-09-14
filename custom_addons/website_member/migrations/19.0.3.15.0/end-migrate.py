# -*- coding: utf-8 -*-
"""Migrate member.field.widget selection → member.widget + widget_id."""


def migrate(cr, version):
    from odoo import api, SUPERUSER_ID

    cr.execute(
        """
        SELECT column_name FROM information_schema.columns
        WHERE table_name = 'member_field' AND column_name = 'widget'
        """
    )
    has_legacy = bool(cr.fetchone())
    if has_legacy:
        cr.execute(
            "ALTER TABLE member_field ADD COLUMN IF NOT EXISTS widget_legacy varchar"
        )
        cr.execute(
            """
            UPDATE member_field
               SET widget_legacy = widget
             WHERE (widget_legacy IS NULL OR widget_legacy = '')
               AND widget IS NOT NULL
            """
        )

    env = api.Environment(cr, SUPERUSER_ID, {})
    env["member.widget"]._ensure_defaults()
    Widget = env["member.widget"].sudo()
    Field = env["member.field"].sudo()
    by_code = {w.code: w.id for w in Widget.search([])}
    text_id = by_code.get("text")

    if has_legacy:
        cr.execute(
            """
            SELECT id, COALESCE(widget_legacy, 'text')
              FROM member_field
             WHERE widget_id IS NULL
            """
        )
        for field_id, code in cr.fetchall():
            widget_id = by_code.get(code) or text_id
            cr.execute(
                "UPDATE member_field SET widget_id = %s WHERE id = %s",
                (widget_id, field_id),
            )

    orphan = Field.search([("widget_id", "=", False)])
    if orphan and text_id:
        orphan.write({"widget_id": text_id})
