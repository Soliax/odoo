# -*- coding: utf-8 -*-
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    member_directory_intro = fields.Char(
        string="Directory Intro",
        config_parameter="website_member_directory.intro",
    )
    member_directory_deny_redirect = fields.Selection(
        [
            ("login", "Redirect to login"),
            ("forbidden", "Show access denied"),
        ],
        string="Anonymous Visitors",
        config_parameter="website_member_directory.deny_redirect",
    )
