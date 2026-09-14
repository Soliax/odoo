# -*- coding: utf-8 -*-
"""Configurable profile display widgets (text, Select, MultiSelect, LIFRAS…)."""

from __future__ import annotations

import re
import unicodedata

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


def _slugify(value):
    text = unicodedata.normalize("NFKD", value or "")
    text = "".join(c for c in text if not unicodedata.combining(c)).lower()
    text = re.sub(r"[^a-z0-9]+", "_", text).strip("_")
    return text or "widget"


# Default LIFRAS brevet rows (seeded on the built-in widget; then editable in UI).
LIFRAS_BREVET_OPTIONS = [
    ("1", "1*", "1*", "brevet-1", 1),
    ("2", "2*", "2*", "brevet-2", 2),
    ("3", "3*", "3*", "brevet-3", 3),
    ("4", "4*", "4*", "brevet-4", 4),
    ("am", "AM - Assistant Moniteur", "AM", "brevet-am", 5),
    ("mc", "MC - Moniteur Club", "MC", "brevet-mc", 6),
    ("mf", "MF - Moniteur Federal", "MF", "brevet-mf", 7),
    ("mn", "MN - Moniteur National", "MN", "brevet-mn", 8),
]


class MemberWidget(models.Model):
    _name = "member.widget"
    _description = "Member Profile Widget"
    _order = "sequence, id"

    name = fields.Char(string="Label", required=True, translate=True)
    code = fields.Char(
        string="Code",
        required=True,
        help="Stable key (text, brevets_lifras, select…).",
    )
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    is_system = fields.Boolean(
        string="Built-in",
        default=False,
        help="Seeded widget. Code and render type stay locked; value list stays editable.",
    )
    render_type = fields.Selection(
        [
            ("text", "Text"),
            ("email", "Email"),
            ("phone", "Phone"),
            ("url", "URL"),
            ("html", "HTML"),
            ("date", "Date"),
            ("boolean", "Yes / No"),
            ("address", "Address block"),
            ("many2one", "Related record name"),
            ("brevet", "Brevet LIFRAS"),
            ("select", "Select"),
            ("multiselect", "MultiSelect"),
        ],
        default="text",
        required=True,
        help="Select = one value from the list (dropdown). "
             "MultiSelect = several values. "
             "Brevet LIFRAS = ranking / TCG display driven by its value list.",
    )
    option_ids = fields.One2many(
        "member.widget.option",
        "widget_id",
        string="Values",
        copy=True,
    )
    uses_value_list = fields.Boolean(compute="_compute_uses_value_list")
    field_ids = fields.One2many("member.field", "widget_id", string="Profile fields")
    field_count = fields.Integer(compute="_compute_field_count")

    _sql_constraints = [
        ("code_uniq", "unique(code)", "Widget code must be unique."),
    ]

    @api.depends("render_type")
    def _compute_uses_value_list(self):
        for rec in self:
            rec.uses_value_list = rec.render_type in ("select", "multiselect", "brevet")

    @api.depends("field_ids")
    def _compute_field_count(self):
        for rec in self:
            rec.field_count = len(rec.field_ids)

    @api.onchange("name")
    def _onchange_name(self):
        if self.name and not self.code and not self.is_system:
            self.code = _slugify(self.name)

    @api.constrains("code")
    def _check_code(self):
        for rec in self:
            if not re.fullmatch(r"[a-z][a-z0-9_]*", rec.code or ""):
                raise ValidationError(_(
                    "Widget code must be lowercase letters, digits and underscores."
                ))

    def write(self, vals):
        for rec in self:
            if rec.is_system:
                if "code" in vals and vals["code"] != rec.code:
                    raise UserError(_("Built-in widget codes cannot be changed."))
                if "render_type" in vals and vals["render_type"] != rec.render_type:
                    raise UserError(_("Built-in widget types cannot be changed."))
        res = super().write(vals)
        if "option_ids" in vals or any(k in vals for k in ("name", "active")):
            self._sync_linked_selection_fields()
        return res

    def unlink(self):
        if self.filtered("is_system"):
            raise UserError(_("Built-in widgets cannot be deleted."))
        used = self.filtered(lambda w: w.field_ids)
        if used:
            raise UserError(_(
                "Cannot delete widgets still used by profile fields: %s"
            ) % ", ".join(used.mapped("name")))
        return super().unlink()

    def get_option(self, value):
        self.ensure_one()
        if value in (False, None, ""):
            return self.env["member.widget.option"]
        return self.option_ids.filtered(lambda o: o.value == str(value))[:1]

    def selection_pairs(self):
        """List of (value, label) for ir.model.fields selection / forms."""
        self.ensure_one()
        return [
            (o.value, o.name)
            for o in self.option_ids.filtered("active").sorted("sequence")
        ]

    def _sync_linked_selection_fields(self):
        """Refresh Selection technical fields bound to Select widgets."""
        Field = self.env["ir.model.fields"].sudo()
        for widget in self:
            if widget.render_type not in ("select", "brevet"):
                continue
            pairs = widget.selection_pairs()
            if not pairs:
                continue
            for conf in widget.field_ids.filtered(
                lambda f: f.is_custom and f.source_model == "res.partner"
            ):
                ir_field = Field.search([
                    ("model", "=", "res.partner"),
                    ("name", "=", conf.field_name),
                    ("state", "=", "manual"),
                    ("ttype", "=", "selection"),
                ], limit=1)
                if ir_field:
                    ir_field.write({"selection": str(pairs)})
            # Built-in LIFRAS field: invalidate registry selection cache via env
            if widget.render_type == "brevet":
                self.env.registry.clear_cache()

    def _ensure_lifras_options(self):
        """Seed editable LIFRAS value list when empty."""
        self.ensure_one()
        if self.render_type != "brevet" or self.option_ids:
            return
        Option = self.env["member.widget.option"].sudo()
        for value, name, short, css, seq in LIFRAS_BREVET_OPTIONS:
            Option.create({
                "widget_id": self.id,
                "value": value,
                "name": name,
                "short_name": short,
                "css_class": css,
                "sequence": seq,
            })

    @api.model
    def _ensure_defaults(self):
        defaults = [
            ("text", "Text", "text", 10),
            ("email", "Email", "email", 20),
            ("phone", "Phone", "phone", 30),
            ("url", "URL", "url", 40),
            ("html", "HTML", "html", 50),
            ("date", "Date", "date", 60),
            ("boolean", "Yes / No", "boolean", 70),
            ("address", "Address block", "address", 80),
            ("many2one", "Related record name", "many2one", 90),
            ("brevets_lifras", "Brevets (LIFRAS)", "brevet", 100),
        ]
        Widget = self.sudo()
        # Legacy code "brevet" → brevets_lifras (code only via SQL: name may be jsonb)
        legacy = Widget.search([("code", "=", "brevet")], limit=1)
        if legacy:
            target = Widget.search([("code", "=", "brevets_lifras")], limit=1)
            if target and target.id != legacy.id:
                self.env.cr.execute(
                    "UPDATE member_field SET widget_id = %s WHERE widget_id = %s",
                    (target.id, legacy.id),
                )
                legacy.unlink()
            else:
                self.env.cr.execute(
                    "UPDATE member_widget SET code = 'brevets_lifras' WHERE id = %s",
                    (legacy.id,),
                )
                legacy.invalidate_recordset(["code"])
                legacy.write({"name": "Brevets (LIFRAS)"})
                legacy._ensure_lifras_options()
        for code, name, render_type, sequence in defaults:
            existing = Widget.search([("code", "=", code)], limit=1)
            if existing:
                if render_type == "brevet":
                    existing._ensure_lifras_options()
                continue
            created = Widget.create({
                "code": code,
                "name": name,
                "render_type": render_type,
                "sequence": sequence,
                "is_system": True,
            })
            if render_type == "brevet":
                created._ensure_lifras_options()
        return Widget.search([])


class MemberWidgetOption(models.Model):
    _name = "member.widget.option"
    _description = "Member Widget Value"
    _order = "sequence, id"

    widget_id = fields.Many2one(
        "member.widget",
        required=True,
        ondelete="cascade",
        index=True,
    )
    name = fields.Char(string="Label", required=True, translate=True)
    value = fields.Char(
        string="Technical value",
        required=True,
        help="Stored on the contact field (selection key).",
    )
    short_name = fields.Char(
        string="Short label",
        help="Compact label for badge display (like 1*, AM, PA).",
    )
    css_class = fields.Char(
        string="CSS class",
        help="Optional class suffix, e.g. brevet-1 or badge-pa.",
    )
    sequence = fields.Integer(
        default=10,
        help="Display order. For LIFRAS brevet, also used as rank (higher = stronger).",
    )
    active = fields.Boolean(default=True)

    _sql_constraints = [
        (
            "widget_value_uniq",
            "unique(widget_id, value)",
            "Each value must be unique inside a widget.",
        ),
    ]

    @api.onchange("name")
    def _onchange_name(self):
        if self.name and not self.value:
            self.value = _slugify(self.name)
        if self.name and not self.short_name:
            self.short_name = self.name

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records.mapped("widget_id")._sync_linked_selection_fields()
        return records

    def write(self, vals):
        res = super().write(vals)
        self.mapped("widget_id")._sync_linked_selection_fields()
        return res

    def unlink(self):
        widgets = self.mapped("widget_id")
        res = super().unlink()
        widgets._sync_linked_selection_fields()
        return res
