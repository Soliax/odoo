# -*- coding: utf-8 -*-
"""Rename widget render_type badge/selection → select/multiselect."""


def migrate(cr, version):
    cr.execute(
        """
        UPDATE member_widget
           SET render_type = 'select'
         WHERE render_type = 'badge'
        """
    )
    cr.execute(
        """
        UPDATE member_widget
           SET render_type = 'multiselect'
         WHERE render_type = 'selection'
        """
    )
    from odoo import api, SUPERUSER_ID

    env = api.Environment(cr, SUPERUSER_ID, {})
    env["member.widget"]._ensure_defaults()
    env["member.field"]._sync_backend_custom_view()
