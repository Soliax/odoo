# -*- coding: utf-8 -*-
"""Rename LIFRAS widget code, seed value list, rebuild Club Plongee custom view."""


def migrate(cr, version):
    from odoo import api, SUPERUSER_ID

    env = api.Environment(cr, SUPERUSER_ID, {})
    env["member.widget"]._ensure_defaults()
    env["member.field"]._sync_backend_custom_view()
