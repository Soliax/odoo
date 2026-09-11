# -*- coding: utf-8 -*-
"""Register new profile field panels after gender/federations fields."""

from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    # Force recompute of section order for existing member.field rows
    fields = env["member.field"].sudo().search([])
    fields._compute_section_sequence()
