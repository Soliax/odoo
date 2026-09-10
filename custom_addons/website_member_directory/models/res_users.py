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
            domain = domain + [
                "|",
                ("name", "ilike", search),
                ("login", "ilike", search),
            ]
        return self.sudo().search(domain, order="name asc")

    def get_directory_profile_fields(self, viewer):
        self.ensure_one()
        Field = self.env["member.directory.field"].sudo()
        fields_conf = Field.search([("active", "=", True)])
        sections = []
        by_section = {}
        for conf in fields_conf:
            if not conf.is_visible_for(viewer):
                continue
            payload = conf.get_display_value(self)
            if not payload:
                continue
            label = dict(conf._fields["section"]._description_selection(self.env)).get(conf.section, conf.section)
            by_section.setdefault(conf.section, {"key": conf.section, "label": label, "items": []})
            by_section[conf.section]["items"].append(
                {
                    "label": conf.name,
                    "widget": conf.widget,
                    "data": payload,
                }
            )
        for section in ["identity", "contact", "address", "professional", "extra"]:
            if section in by_section and by_section[section]["items"]:
                sections.append(by_section[section])
        return sections
