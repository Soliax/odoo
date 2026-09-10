# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    directory_published = fields.Boolean(
        string="Show in Member Directory",
        default=True,
        help="If enabled, this internal user appears in the website member directory.",
    )
    directory_subtitle = fields.Char(
        string="Directory Subtitle",
        help="Optional short line under the name on directory cards (e.g. role).",
    )

    # Related diving club fields (editable from the user form)
    dive_firstname = fields.Char(related="partner_id.dive_firstname", readonly=False)
    dive_lastname = fields.Char(related="partner_id.dive_lastname", readonly=False)
    dive_phone_home = fields.Char(related="partner_id.dive_phone_home", readonly=False)
    dive_phone_work = fields.Char(related="partner_id.dive_phone_work", readonly=False)
    dive_birthday = fields.Date(related="partner_id.dive_birthday", readonly=False)
    dive_profession = fields.Char(related="partner_id.dive_profession", readonly=False)
    dive_brevet = fields.Selection(related="partner_id.dive_brevet", readonly=False)
    dive_brevet_label = fields.Char(related="partner_id.dive_brevet_label")
    dive_brevet_short = fields.Char(related="partner_id.dive_brevet_short")
    dive_brevet_rank = fields.Integer(related="partner_id.dive_brevet_rank")
    dive_brevet_css = fields.Char(related="partner_id.dive_brevet_css")
    dive_contact_name = fields.Char(related="partner_id.dive_contact_name", readonly=False)
    dive_contact_phone = fields.Char(related="partner_id.dive_contact_phone", readonly=False)
    dive_last_medical = fields.Date(related="partner_id.dive_last_medical", readonly=False)
    dive_last_ecg = fields.Date(related="partner_id.dive_last_ecg", readonly=False)
    dive_lifras_id = fields.Char(related="partner_id.dive_lifras_id", readonly=False)
    dive_other_brevets = fields.Text(related="partner_id.dive_other_brevets", readonly=False)
    dive_cfps = fields.Boolean(related="partner_id.dive_cfps", readonly=False)
    dive_nitrox_basic_date = fields.Date(related="partner_id.dive_nitrox_basic_date", readonly=False)
    dive_cfps_start = fields.Date(related="partner_id.dive_cfps_start", readonly=False)
    dive_cfps_end = fields.Date(related="partner_id.dive_cfps_end", readonly=False)

    @api.model
    def _directory_domain(self):
        return [
            ("share", "=", False),
            ("active", "=", True),
            ("directory_published", "=", True),
            ("id", "!=", self.env.ref("base.user_root").id),
        ]

    @api.model
    def get_directory_members(self, search=None):
        domain = self._directory_domain()
        if search:
            domain += [
                "|", "|", "|",
                ("name", "ilike", search),
                ("login", "ilike", search),
                ("dive_firstname", "ilike", search),
                ("dive_lastname", "ilike", search),
            ]
        return self.sudo().search(domain, order="dive_brevet_rank desc, name asc")

    def get_directory_card_name(self):
        self.ensure_one()
        return self.partner_id.get_dive_display_name()

    def get_directory_profile_fields(self, viewer):
        self.ensure_one()
        Field = self.env["member.directory.field"].sudo()
        fields_conf = Field.search([("active", "=", True)])
        by_section = {}
        for conf in fields_conf:
            if not conf.is_visible_for(viewer):
                continue
            payload = conf.get_display_value(self)
            if not payload:
                continue
            label = dict(conf._fields["section"]._description_selection(self.env)).get(
                conf.section, conf.section
            )
            by_section.setdefault(
                conf.section, {"key": conf.section, "label": label, "items": []}
            )
            by_section[conf.section]["items"].append(
                {
                    "label": conf.name,
                    "widget": conf.widget,
                    "data": payload,
                }
            )
        sections = []
        for section in [
            "identity",
            "contact",
            "address",
            "professional",
            "lifras",
            "medical",
            "extra",
        ]:
            if section in by_section and by_section[section]["items"]:
                sections.append(by_section[section])
        return sections
