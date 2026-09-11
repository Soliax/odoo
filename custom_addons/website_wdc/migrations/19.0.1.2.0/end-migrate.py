# -*- coding: utf-8 -*-
from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    from odoo.addons.website_wdc.hooks import _reset_website_pages, _setup_company

    _setup_company(env)
    _reset_website_pages(env)
