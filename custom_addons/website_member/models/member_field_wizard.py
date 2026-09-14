# -*- coding: utf-8 -*-
"""Wizard: create a partner technical field + profile field from the UI."""

from __future__ import annotations

import re
import unicodedata

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

from .member_field import _ensure_x_prefix


def _slugify(value):
    text = unicodedata.normalize("NFKD", value or "")
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "_", text).strip("_")
    return text or "field"


class MemberFieldCreateWizard(models.TransientModel):
    _name = "member.field.create.wizard"
    _description = "Create member profile technical field"

    name = fields.Char(string="Label", required=True)
    section_id = fields.Many2one("member.section", string="Section", required=True)
    widget_id = fields.Many2one(
        "member.widget",
        string="Widget",
        required=True,
        default=lambda self: self.env.ref(
            "website_member.widget_text", raise_if_not_found=False
        ),
    )
    field_type = fields.Selection(
        [
            ("char", "Text (short)"),
            ("text", "Text (long)"),
            ("date", "Date"),
            ("boolean", "Yes / No"),
            ("html", "HTML"),
            ("selection", "Select (dropdown)"),
            ("multiselect", "MultiSelect"),
        ],
        string="Storage type",
        compute="_compute_field_type",
        readonly=True,
    )
    technical_name = fields.Char(
        string="Technical name",
        help="Manual fields always get an x_ prefix (Odoo rule). "
             "You can type dive_brevet_pa — it becomes x_dive_brevet_pa.",
    )
    show_on_backend = fields.Boolean(
        string="Show on Plongée tab",
        default=True,
    )
    show_on_profile = fields.Boolean(
        string="Show on website profile",
        default=True,
    )
    sequence = fields.Integer(default=90)

    @api.depends("widget_id", "widget_id.render_type")
    def _compute_field_type(self):
        for wiz in self:
            render = wiz.widget_id.render_type if wiz.widget_id else "text"
            wiz.field_type = {
                "select": "selection",
                "multiselect": "multiselect",
                "date": "date",
                "boolean": "boolean",
                "html": "html",
                "text": "char",
                "email": "char",
                "phone": "char",
                "url": "char",
                "brevet": "selection",
            }.get(render, "char")

    @api.onchange("name")
    def _onchange_name(self):
        if self.name and not self.technical_name:
            self.technical_name = _ensure_x_prefix(_slugify(self.name))

    @api.onchange("technical_name")
    def _onchange_technical_name(self):
        raw = (self.technical_name or "").strip()
        if not raw:
            return
        if not raw.lower().startswith("x_"):
            self.technical_name = "x_%s" % raw

    def action_create(self):
        self.ensure_one()
        self.env["member.section"]._ensure_defaults()
        self.env["member.widget"]._ensure_defaults()
        tech = _ensure_x_prefix(self.technical_name)
        self.technical_name = tech
        if not tech:
            raise ValidationError(_("Please set a technical name."))
        if not re.fullmatch(r"x_[a-z][a-z0-9_]*", tech):
            raise ValidationError(_(
                "Technical name must be lowercase letters, digits and underscores "
                "(example: dive_brevet_pa → x_dive_brevet_pa)."
            ))
        if tech in self.env["res.partner"]._fields:
            raise UserError(_("Field %s already exists on contacts.") % tech)

        widget = self.widget_id
        render = widget.render_type
        pairs = widget.selection_pairs() if widget.uses_value_list else []

        if render in ("select", "multiselect", "brevet"):
            if not pairs:
                raise ValidationError(_(
                    "Add values on the widget « %s » before creating the field."
                ) % widget.name)

        field_vals = {
            "name": tech,
            "field_description": self.name,
            "model_id": self.env["ir.model"]._get("res.partner").id,
            "state": "manual",
            "copied": True,
        }

        if render == "select":
            field_vals["ttype"] = "selection"
            field_vals["selection"] = str(pairs)
        elif render == "multiselect":
            rel_table = ("res_partner_%s_rel" % tech)[:63]
            field_vals.update({
                "ttype": "many2many",
                "relation": "member.widget.option",
                "relation_table": rel_table,
            })
        elif render == "date":
            field_vals["ttype"] = "date"
        elif render == "boolean":
            field_vals["ttype"] = "boolean"
        elif render == "html":
            field_vals["ttype"] = "html"
        elif render == "text":
            field_vals["ttype"] = "char"
        else:
            field_vals["ttype"] = "char"

        self.env["ir.model.fields"].sudo().create(field_vals)

        profile_vals = {
            "name": self.name,
            "section_id": self.section_id.id,
            "source_model": "res.partner",
            "field_name": tech,
            "widget_id": widget.id,
            "sequence": self.sequence,
            "is_custom": True,
            "show_on_backend": self.show_on_backend,
            "visibility": "connected",
        }
        if self.show_on_profile:
            profile = self.env["member.field"].create(profile_vals)
        elif self.show_on_backend:
            profile_vals["active"] = False
            profile_vals["show_on_backend"] = True
            profile = self.env["member.field"].create(profile_vals)
        else:
            raise UserError(_("Enable at least website profile or Plongée tab."))

        self.env["member.field"]._sync_backend_custom_view()
        return {
            "type": "ir.actions.act_window",
            "res_model": "member.field",
            "res_id": profile.id,
            "view_mode": "form",
            "target": "current",
        }
