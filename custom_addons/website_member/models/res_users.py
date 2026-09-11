# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.osv import expression
import unicodedata


def _fold_name(value):
    """Case/accent-insensitive key for stable French name sorting."""
    text = unicodedata.normalize("NFKD", value or "")
    return "".join(c for c in text if not unicodedata.combining(c)).casefold().strip()


class ResUsers(models.Model):
    _inherit = "res.users"

    members_published = fields.Boolean(
        string="Show on Members page",
        default=True,
        help="If enabled, this internal user appears on the website Members page.",
    )
    members_subtitle = fields.Char(
        string="Card subtitle",
        help="Optional short line under the name on member cards.",
    )

    dive_firstname = fields.Char(related="partner_id.dive_firstname", readonly=False)
    dive_lastname = fields.Char(related="partner_id.dive_lastname", readonly=False)
    dive_gender = fields.Selection(related="partner_id.dive_gender", readonly=False)
    dive_member_since = fields.Date(related="partner_id.dive_member_since", readonly=False)
    dive_phone_home = fields.Char(related="partner_id.dive_phone_home", readonly=False)
    dive_phone_work = fields.Char(related="partner_id.dive_phone_work", readonly=False)
    dive_birthday = fields.Date(related="partner_id.dive_birthday", readonly=False)
    dive_profession = fields.Char(related="partner_id.dive_profession", readonly=False)
    dive_is_plongeur = fields.Boolean(related="partner_id.dive_is_plongeur", readonly=False)
    dive_is_hsa = fields.Boolean(related="partner_id.dive_is_hsa", readonly=False)
    dive_fed_adip = fields.Char(related="partner_id.dive_fed_adip", readonly=False)
    dive_fed_cedip = fields.Char(related="partner_id.dive_fed_cedip", readonly=False)
    dive_fed_ida = fields.Char(related="partner_id.dive_fed_ida", readonly=False)
    dive_fed_protec = fields.Char(related="partner_id.dive_fed_protec", readonly=False)
    dive_fed_ssi = fields.Char(related="partner_id.dive_fed_ssi", readonly=False)
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
    def _members_domain(self):
        return [
            ("share", "=", False),
            ("active", "=", True),
            ("members_published", "=", True),
            ("id", "!=", self.env.ref("base.user_root").id),
        ]

    @api.model
    def get_members(
        self,
        search=None,
        category=None,
        brevet=None,
        specialty=None,
        categories=None,
        brevets=None,
        specialties=None,
        limit=None,
        sort="brevet_desc",
    ):
        domain = self._members_domain()
        if search:
            domain += [
                "|", "|", "|",
                ("name", "ilike", search),
                ("login", "ilike", search),
                ("dive_firstname", "ilike", search),
                ("dive_lastname", "ilike", search),
            ]

        # Multi-select OR within each dimension; AND across dimensions
        cats = list(categories or [])
        if category and category not in cats:
            cats.append(category)
        cats = [c for c in cats if c in ("plongeur", "hsa")]
        if len(cats) == 1:
            if cats[0] == "plongeur":
                domain.append(("dive_is_plongeur", "=", True))
            else:
                domain.append(("dive_is_hsa", "=", True))
        elif len(cats) > 1:
            domain += [
                "|",
                ("dive_is_plongeur", "=", True),
                ("dive_is_hsa", "=", True),
            ]

        brev = [str(b).strip().lower() for b in (brevets or []) if b]
        if brevet and str(brevet).strip().lower() not in brev:
            brev.append(str(brevet).strip().lower())
        if brev:
            brevet_leaves = []
            for code in brev:
                if code == "nb":
                    brevet_leaves.append([
                        ("dive_brevet", "=", False),
                        "|",
                        ("dive_is_plongeur", "=", True),
                        ("dive_is_hsa", "=", False),
                    ])
                else:
                    brevet_leaves.append([("dive_brevet", "=", code)])
            domain = expression.AND([domain, expression.OR(brevet_leaves)])

        specs = [str(s).strip().lower() for s in (specialties or []) if s]
        if specialty and str(specialty).strip().lower() not in specs:
            specs.append(str(specialty).strip().lower())
        field_map = {
            "cfps": "dive_spec_cfps",
            "ve": "dive_spec_ve",
            "pn": "dive_spec_pn",
            "pnc": "dive_spec_pnc",
            "in": "dive_spec_in",
            "inc": "dive_spec_inc",
            "fn": "dive_spec_fn",
        }
        spec_fields = [field_map[s] for s in specs if s in field_map]
        if spec_fields:
            domain = expression.AND([
                domain,
                expression.OR([[(f, "!=", False)] for f in spec_fields]),
            ])

        limit = int(limit) if limit else None
        sort_key = str(sort or "brevet_desc").strip().lower()
        members = self.sudo().search(domain)

        if sort_key in ("name_asc", "name_desc"):
            reverse = sort_key.endswith("desc")

            def _name_key(user):
                last = _fold_name(user.dive_lastname)
                first = _fold_name(user.dive_firstname)
                full = _fold_name(user.name)
                # Prefer lastname; if missing, use the end of the display name.
                if not last and full:
                    parts = full.rsplit(" ", 1)
                    last = parts[-1] if parts else full
                    if len(parts) > 1 and not first:
                        first = parts[0]
                # Empty / incomplete records go last (ASC) / first (DESC via reverse)
                if not (last or first or full):
                    return ("\uffff", "\uffff", "\uffff")
                return (last or full or "\uffff", first, full)

            members = members.sorted(key=_name_key, reverse=reverse)
        elif sort_key == "brevet_asc":
            members = members.sorted(
                key=lambda u: (
                    u.dive_brevet_rank or 0,
                    _fold_name(u.dive_lastname or u.name),
                    _fold_name(u.dive_firstname),
                )
            )
        else:  # brevet_desc (default)
            members = members.sorted(
                key=lambda u: (
                    -(u.dive_brevet_rank or 0),
                    _fold_name(u.dive_lastname or u.name),
                    _fold_name(u.dive_firstname),
                )
            )

        if limit:
            members = members[:limit]
        return members


    @api.model
    def get_event_attendee_partners(
        self, event_id, limit=None, states=None, published_only=True
    ):
        """Partners registered on an event, ordered by brevet rank."""
        cards = self.get_event_attendee_cards(
            event_id=event_id,
            limit=limit,
            states=states,
            published_only=published_only,
        )
        return self.env["res.partner"].browse([c["partner"].id for c in cards])

    @api.model
    def get_event_attendee_cards(
        self, event_id, limit=None, states=None, published_only=True
    ):
        """Attendee rows with ticket/inscription counts per partner."""
        if not event_id or "event.registration" not in self.env:
            return []
        states = states or ["open", "done"]
        Registration = self.env["event.registration"].sudo()
        groups = Registration.read_group(
            [
                ("event_id", "=", int(event_id)),
                ("state", "in", list(states)),
                ("partner_id", "!=", False),
            ],
            ["partner_id"],
            ["partner_id"],
            lazy=False,
        )
        counts = {
            g["partner_id"][0]: g["__count"]
            for g in groups
            if g.get("partner_id")
        }
        if not counts:
            return []
        partners = self.env["res.partner"].sudo().browse(list(counts.keys()))
        if published_only:
            published = self.sudo().search([
                ("partner_id", "in", partners.ids),
                ("members_published", "=", True),
                ("share", "=", False),
                ("active", "=", True),
            ]).mapped("partner_id")
            partners = partners & published
        partners = partners.sorted(
            key=lambda p: (-(p.dive_brevet_rank or 0), (p.name or "").lower())
        )
        if limit:
            partners = partners[: int(limit)]
        return [
            {"partner": partner, "ticket_count": counts.get(partner.id, 1)}
            for partner in partners
        ]

    def get_member_card_name(self):
        self.ensure_one()
        return self.partner_id.get_dive_display_name()

    # Alias kept so partially-upgraded DBs / stale workers never break cards
    get_directory_card_name = get_member_card_name

    def get_dive_specialties(self):
        self.ensure_one()
        return self.partner_id.get_dive_specialties()

    def get_dive_categories(self):
        self.ensure_one()
        return self.partner_id.get_dive_categories()

    def get_dive_brevet_dates(self):
        self.ensure_one()
        return self.partner_id.get_dive_brevet_dates()

    def get_member_events(self, states=None):
        """Events this member is or was registered to (grouped by event)."""
        self.ensure_one()
        if "event.registration" not in self.env:
            return []
        states = list(states or ("open", "done"))
        partner = self.partner_id
        if partner.email:
            domain = [
                ("state", "in", states),
                ("active", "=", True),
                "|",
                ("partner_id", "=", partner.id),
                "&",
                ("partner_id", "=", False),
                ("email", "=ilike", partner.email),
            ]
        else:
            domain = [
                ("state", "in", states),
                ("active", "=", True),
                ("partner_id", "=", partner.id),
            ]

        Registration = self.env["event.registration"].sudo()
        rows = Registration._read_group(
            domain,
            groupby=["event_id", "state"],
            aggregates=["__count"],
        )
        if not rows:
            return []

        by_event = {}
        for event, state, count in rows:
            if not event:
                continue
            row = by_event.setdefault(event.id, {
                "event": event,
                "ticket_count": 0,
                "states": set(),
            })
            row["ticket_count"] += count
            row["states"].add(state)

        events = self.env["event.event"].sudo().browse(list(by_event.keys()))
        events = events.sorted(
            key=lambda e: e.date_begin or fields.Datetime.from_string("1970-01-01 00:00:00"),
            reverse=True,
        )
        state_labels = {
            "open": "Inscrit",
            "done": "Participé",
            "draft": "En attente",
            "cancel": "Annulé",
        }
        now = fields.Datetime.now()
        result = []
        for event in events:
            info = by_event[event.id]
            if "done" in info["states"]:
                status = "done"
            elif "open" in info["states"]:
                status = "open"
            else:
                status = next(iter(info["states"]), "open")
            url = False
            if "website_url" in event._fields and event.website_url:
                url = event.website_url
            result.append({
                "event": event,
                "name": event.name,
                "date_begin": event.date_begin,
                "date_end": event.date_end,
                "url": url,
                "ticket_count": info["ticket_count"],
                "status": status,
                "status_label": state_labels.get(status, status),
                "is_past": bool(event.date_end and event.date_end < now),
            })
        return result

    def get_member_profile_fields(self, viewer):
        self.ensure_one()
        Field = self.env["member.field"].sudo()
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
            "lifras", "brevets", "specialties", "federations", "medical", "extra",
        ]:
            if section in by_section and by_section[section]["items"]:
                sections.append(by_section[section])
        return sections

    get_directory_profile_fields = get_member_profile_fields
    get_directory_members = get_members
