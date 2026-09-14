# -*- coding: utf-8 -*-
"""Preserve legacy section selection values before column drop."""


def migrate(cr, version):
    cr.execute(
        """
        SELECT column_name FROM information_schema.columns
        WHERE table_name = 'member_field' AND column_name = 'section'
        """
    )
    if not cr.fetchone():
        return
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
         WHERE (section_legacy IS NULL OR section_legacy = '')
           AND section IS NOT NULL
        """
    )
