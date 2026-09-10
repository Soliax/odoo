# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class MemberDirectoryField(models.Model):
    _name = "member.directory.field"
    _description = "Member Directory Profile Field"
    _order = "section_sequence, sequence, id"

    name = fields.Char(string="Label", required=True, translate=True)
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)
    section = fields.Selection(
        [
            ("identity", "Identity"),
            ("contact", "Contact"),
            ("address", "Address"),
            ("professional", "Professional"),
            ("extra", "Extra"),
        ],
        default="contact",
        required=True,
    )
    section_sequence = fields.Integer(
        compute="_compute_section_sequence",
        store=True,
    )
    source_model = fields.Selection(
        [
            ("res.partner", "Contact (res.partner)"),
            ("res.users", "User (res.users)"),
        ],
        default="res.partner",
        required=True,
    )
    field_name = fields.Char(
        string="Technical Field",
        required=True,
        help="Technical name of the field on the source model, e.g. email, phone, street.",
    )
    widget = fields.Selection(
        [
            ("text", "Text"),
            ("email", "Email"),
            ("phone", "Phone"),
            ("url", "URL"),
            ("html", "HTML"),
            ("address", "Address block"),
            ("many2one", "Related record name"),
        ],
        default="text",
        required=True,
    )
    visibility = fields.Selection(
        [
            ("connected", "All logged-in members"),
            ("group", "Specific groups only"),
        ],
        default="connected",
        required=True,
    )
    group_ids = fields.Many2many(
        "res.groups",
        "member_directory_field_group_rel",
        "field_id",
        "group_id",
        string="Allowed Groups",
    )

    @api.depends("section")
    def _compute_section_sequence(self):
        order = {
            "identity": 10,
            "contact": 20,
            "address": 30,
            "professional": 40,
            "extra": 50,
        }
        for rec in self:
            rec.section_sequence = order.get(rec.section, 99)

    @api.constrains("field_name", "source_model")
    def _check_field_exists(self):
        for rec in self:
            model = self.env[rec.source_model]
            if rec.field_name not in model._fields:
                raise ValidationError(
                    self.env._(
                        "Field %(field)s does not exist on model %(model)s.",
                        field=rec.field_name,
                        model=rec.source_model,
                    )
                )

    def is_visible_for(self, user):
        self.ensure_one()
        if not self.active:
            return False
        if self.visibility == "connected":
            return bool(user and not user._is_public())
        return bool(user.groups_id & self.group_ids)

    def get_display_value(self, member_user):
        """Return a render-ready dict for QWeb."""
        self.ensure_one()
        record = member_user.partner_id if self.source_model == "res.partner" else member_user
        field = record._fields.get(self.field_name)
        if not field:
            return False

        raw = record[self.field_name]
        if self.widget == "address":
            partner = member_user.partner_id
            lines = (partner.contact_address or partner._display_address(without_company=True) or "").strip()
            return {"type": "address", "value": lines} if lines else False

        if field.type in ("many2one",):
            if not raw:
                return False
            return {"type": "many2one", "value": raw.display_name, "id": raw.id}

        if field.type in ("boolean",):
            return {"type": "text", "value": self.env._("Yes") if raw else self.env._("No")}

        if field.type in ("html",):
            if not raw:
                return False
            return {"type": "html", "value": raw}

        if raw in (False, None, ""):
            return False

        value = raw
        if field.type == "selection":
            value = dict(field._description_selection(self.env)).get(raw, raw)

        widget = self.widget
        if widget == "email":
            return {"type": "email", "value": value}
        if widget == "phone":
            return {"type": "phone", "value": value}
        if widget == "url":
            return {"type": "url", "value": value}
        return {"type": "text", "value": value}
