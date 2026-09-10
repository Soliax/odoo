# -*- coding: utf-8 -*-
from odoo import fields, models


class SiteCore(models.Model):
    _name = 'site_core.site_core'
    _description = 'Site Core'

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    notes = fields.Text()
