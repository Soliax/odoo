# -*- coding: utf-8 -*-
"""Clear old hard-coded homepage COW and refresh menus after lean mockup rewrite."""

from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    from odoo.addons.website_wdc.hooks import (
        _clear_cow_views,
        _ensure_homepage_shell,
        _ensure_menus,
        _setup_company,
    )
    _setup_company(env)
    _clear_cow_views(env)
    _ensure_homepage_shell(env)
    _ensure_menus(env)
