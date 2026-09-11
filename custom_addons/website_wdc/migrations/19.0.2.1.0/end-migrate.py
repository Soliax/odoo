# -*- coding: utf-8 -*-
"""Apply WDC logo branding on upgrade."""

from odoo import SUPERUSER_ID, api

from odoo.addons.website_wdc.hooks import _ensure_branding


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _ensure_branding(env)
