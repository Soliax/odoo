# -*- coding: utf-8 -*-
"""Wizard: create a partner technical field + profile field from the UI."""

from __future__ import annotations

import re
import unicodedata

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


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
    field_type = fields.Selection(
        [
            ("char", "Text (short)"),
            ("text", "Text (long)"),
            ("date", "Date"),
            ("boolean", "Yes / No"),
            ("html", "HTML"),
        ],
        default="char",
        required=True,
    )
    technical_name = fields.Char(
        string="Technical name",
        help="Free technical name. Odoo custom fields must start with x_ "
             "(example: x_dive_spec_pa). Only suggested from the label when empty.",
    )
    show_on_backend = fields.Boolean(
        string="Show on Club Plongee tab",
        default=True,
    )
    show_on_profile = fields.Boolean(
        string="Show on website profile",
        default=True,
    )
    sequence = fields.Integer(default=90)

    @api.onchange("name")
    def _onchange_name(self):
        # Suggest once only — never overwrite a name the user already typed.
        if self.name and not self.technical_name:
            self.technical_name = "x_%s" % _slugify(self.name)

    def action_create(self):
        self.ensure_one()
        self.env["member.section"]._ensure_defaults()
        tech = (self.technical_name or "").strip()
        if not tech:
            raise ValidationError(_("Please set a technical name."))
        if not re.fullmatch(r"[a-z][a-z0-9_]*", tech):
            raise ValidationError(_(
                "Technical name must be lowercase letters, digits and underscores, "
                "starting with a letter (example: x_dive_spec_pa)."
            ))
        # Manual (UI) fields are stored as ir.model.fields state=manual → require x_
        if not tech.startswith("x_"):
            raise ValidationError(_(
                "Odoo only allows UI-created fields whose name starts with x_.\n"
                "You typed %(typed)s — use for example %(hint)s.",
                typed=tech,
                hint="x_%s" % tech,
            ))
        if tech in self.env["res.partner"]._fields:
            raise UserError(_("Field %s already exists on contacts.") % tech)

        widget = {
            "char": "text",
            "text": "text",
            "date": "date",
            "boolean": "boolean",
            "html": "html",
        }[self.field_type]

        partner_model = self.env["ir.model"]._get("res.partner")
        self.env["ir.model.fields"].sudo().create({
            "name": tech,
            "field_description": self.name,
            "model_id": partner_model.id,
            "ttype": self.field_type,
            "state": "manual",
            "copied": True,
        })

        if self.show_on_profile:
            profile = self.env["member.field"].create({
                "name": self.name,
                "section_id": self.section_id.id,
                "source_model": "res.partner",
                "field_name": tech,
                "widget": widget,
                "sequence": self.sequence,
                "is_custom": True,
                "show_on_backend": self.show_on_backend,
                "visibility": "connected",
            })
        elif self.show_on_backend:
            profile = self.env["member.field"].create({
                "name": self.name,
                "section_id": self.section_id.id,
                "source_model": "res.partner",
                "field_name": tech,
                "widget": widget,
                "sequence": self.sequence,
                "is_custom": True,
                "show_on_backend": True,
                "active": False,
                "visibility": "connected",
            })
        else:
            raise UserError(_("Enable at least website profile or Club Plongee tab."))

        self.env["member.field"]._sync_backend_custom_view()
        return {
            "type": "ir.actions.act_window",
            "res_model": "member.field",
            "res_id": profile.id,
            "view_mode": "form",
            "target": "current",
        }
