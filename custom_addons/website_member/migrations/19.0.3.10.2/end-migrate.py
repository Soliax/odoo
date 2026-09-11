# -*- coding: utf-8 -*-
"""HSA is a category, never a brevet — recompute brevet meta to NB."""

from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    partners = env["res.partner"].sudo().search([])
    partners._compute_dive_brevet_meta()
