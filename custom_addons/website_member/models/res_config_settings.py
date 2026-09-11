# -*- coding: utf-8 -*-
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    member_intro = fields.Char(
        string="Members Intro",
        config_parameter="website_member.intro",
    )
    member_deny_redirect = fields.Selection(
        [
            ("login", "Redirect to login"),
            ("forbidden", "Show access denied"),
        ],
        string="Anonymous Visitors",
        config_parameter="website_member.deny_redirect",
    )
