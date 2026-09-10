# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    directory_published = fields.Boolean(
        string="Show on Members page",
        default=True,
        help="If enabled, this internal user appears on the website Members page.",
    )
    directory_subtitle = fields.Char(
        string="Card subtitle",
        help="Optional short line under the name on member cards.",
    )

    dive_firstname = fields.Char(related="partner_id.dive_firstname", readonly=False)
    dive_lastname = fields.Char(related="partner_id.dive_lastname", readonly=False)
    dive_phone_home = fields.Char(related="partner_id.dive_phone_home", readonly=False)
    dive_phone_work = fields.Char(related="partner_id.dive_phone_work", readonly=False)
    dive_birthday = fields.Date(related="partner_id.dive_birthday", readonly=False)
    dive_profession = fields.Char(related="partner_id.dive_profession", readonly=False)
    dive_is_plongeur = fields.Boolean(related="partner_id.dive_is_plongeur", readonly=False)
    dive_is_hsa = fields.Boolean(related="partner_id.dive_is_hsa", readonly=False)
    dive_brevet_date_1 = fields.Date(related="partner_id.dive_brevet_date_1", readonly=False)
    dive_brevet_date_2 = fields.Date(related="partner_id.dive_brevet_date_2", readonly=False)
    dive_brevet_date_3 = fields.Date(related="partner_id.dive_brevet_date_3", readonly=False)
    dive_brevet_date_4 = fields.Date(related="partner_id.dive_brevet_date_4", readonly=False)
    dive_brevet_date_am = fields.Date(related="partner_id.dive_brevet_date_am", readonly=False)
    dive_brevet_date_mc = fields.Date(related="partner_id.dive_brevet_date_mc", readonly=False)
    dive_brevet_date_mf = fields.Date(related="partner_id.dive_brevet_date_mf", readonly=False)
    dive_brevet_date_mn = fields.Date(related="partner_id.dive_brevet_date_mn", readonly=False)
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
    dive_spec_cfps = fields.Date(related="partner_id.dive_spec_cfps", readonly=False)
    dive_spec_ve = fields.Date(related="partner_id.dive_spec_ve", readonly=False)
    dive_spec_pn = fields.Date(related="partner_id.dive_spec_pn", readonly=False)
    dive_spec_pnc = fields.Date(related="partner_id.dive_spec_pnc", readonly=False)
    dive_spec_in = fields.Date(related="partner_id.dive_spec_in", readonly=False)
    dive_spec_inc = fields.Date(related="partner_id.dive_spec_inc", readonly=False)
    dive_spec_fn = fields.Date(related="partner_id.dive_spec_fn", readonly=False)
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
    def get_directory_members(
        self,
        search=None,
        category=None,
        brevet=None,
        specialty=None,
        limit=None,
    ):
        domain = self._directory_domain()
        if search:
            domain += [
                "|", "|", "|",
                ("name", "ilike", search),
                ("login", "ilike", search),
                ("dive_firstname", "ilike", search),
                ("dive_lastname", "ilike", search),
            ]
        if category == "plongeur":
            domain.append(("dive_is_plongeur", "=", True))
        elif category == "hsa":
            domain.append(("dive_is_hsa", "=", True))
        if brevet:
            brevet = brevet.strip().lower()
            if brevet == "nb":
                domain += [
                    ("dive_brevet", "=", False),
                    "|",
                    ("dive_is_plongeur", "=", True),
                    ("dive_is_hsa", "=", False),
                ]
            elif brevet == "hsa":
                domain += [
                    ("dive_brevet", "=", False),
                    ("dive_is_hsa", "=", True),
                    ("dive_is_plongeur", "=", False),
                ]
            else:
                domain.append(("dive_brevet", "=", brevet))
        if specialty:
            specialty = specialty.strip().lower()
            field_map = {
                "cfps": "dive_spec_cfps",
                "ve": "dive_spec_ve",
                "pn": "dive_spec_pn",
                "pnc": "dive_spec_pnc",
                "in": "dive_spec_in",
                "inc": "dive_spec_inc",
                "fn": "dive_spec_fn",
            }
            fname = field_map.get(specialty)
            if fname:
                domain.append((fname, "!=", False))
        limit = int(limit) if limit else None
        return self.sudo().search(
            domain,
            order="dive_brevet_rank desc, name asc",
            limit=limit or None,
        )

    @api.model
    def get_event_attendee_partners(
        self, event_id, limit=None, states=None, published_only=True
    ):
        """Partners registered on an event, ordered by brevet rank."""
        if not event_id or "event.registration" not in self.env:
            return self.env["res.partner"]
        states = states or ["open", "done"]
        regs = self.env["event.registration"].sudo().search([
            ("event_id", "=", int(event_id)),
            ("state", "in", list(states)),
            ("partner_id", "!=", False),
        ])
        partners = regs.mapped("partner_id")
        if published_only:
            published = self.sudo().search([
                ("partner_id", "in", partners.ids),
                ("directory_published", "=", True),
                ("share", "=", False),
                ("active", "=", True),
            ]).mapped("partner_id")
            partners = partners & published
        partners = partners.sorted(
            key=lambda p: (-(p.dive_brevet_rank or 0), (p.name or "").lower())
        )
        if limit:
            partners = partners[: int(limit)]
        return partners

    def get_directory_card_name(self):
        self.ensure_one()
        return self.partner_id.get_dive_display_name()

    def get_dive_specialties(self):
        self.ensure_one()
        return self.partner_id.get_dive_specialties()

    def get_dive_categories(self):
        self.ensure_one()
        return self.partner_id.get_dive_categories()

    def get_dive_brevet_dates(self):
        self.ensure_one()
        return self.partner_id.get_dive_brevet_dates()

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
            "identity", "contact", "address", "professional",
            "lifras", "brevets", "specialties", "medical", "extra",
        ]:
            if section in by_section and by_section[section]["items"]:
                sections.append(by_section[section])
        return sections
