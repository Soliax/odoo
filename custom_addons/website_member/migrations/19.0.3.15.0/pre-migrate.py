# -*- coding: utf-8 -*-
"""Preserve legacy widget selection values before column drop."""


def migrate(cr, version):
    cr.execute(
        """
        SELECT column_name FROM information_schema.columns
        WHERE table_name = 'member_field' AND column_name = 'widget'
        """
    )
    if not cr.fetchone():
        return
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
