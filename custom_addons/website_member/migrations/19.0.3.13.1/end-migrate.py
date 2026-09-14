# -*- coding: utf-8 -*-
"""Split club groups into Plongeurs / HSA and reassign members."""


def migrate(cr, version):
    from odoo import api, SUPERUSER_ID

    env = api.Environment(cr, SUPERUSER_ID, {})
    company = env["res.company"]._ensure_wdc_company()
    env["res.lang"]._ensure_fr_be()
    env["res.users"]._reassign_members_to_wdc()
    env["website"].sudo().search([]).write({
        "company_id": company.id,
        "name": company.name,
    })
