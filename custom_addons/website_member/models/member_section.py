# -*- coding: utf-8 -*-
"""Editable profile sections for member directory / Club Plongee."""

from odoo import api, fields, models


class MemberSection(models.Model):
    _name = "member.section"
    _description = "Member Profile Section"
    _order = "sequence, id"

    name = fields.Char(string="Label", required=True, translate=True)
    code = fields.Char(
        string="Code",
        required=True,
        help="Stable technical key (identity, federations, …).",
    )
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    field_ids = fields.One2many("member.field", "section_id", string="Fields")
    field_count = fields.Integer(compute="_compute_field_count")

    _sql_constraints = [
        ("code_uniq", "unique(code)", "Section code must be unique."),
    ]

    @api.depends("field_ids")
    def _compute_field_count(self):
        for rec in self:
            rec.field_count = len(rec.field_ids)

    @api.model
    def _ensure_defaults(self):
        """Create the built-in sections if missing (safe to call often)."""
        defaults = [
            ("identity", "Identite", 10),
            ("contact", "Contact", 20),
            ("address", "Adresse", 30),
            ("professional", "Profession", 40),
            ("club", "Club", 45),
            ("lifras", "LIFRAS", 50),
            ("brevets", "Brevets", 52),
            ("specialties", "Specialites", 55),
            ("federations", "Autres federations", 58),
            ("medical", "Medical", 60),
            ("extra", "Extra", 70),
        ]
        Section = self.sudo()
        for code, name, sequence in defaults:
            existing = Section.search([("code", "=", code)], limit=1)
            if existing:
                # Keep admin renames for name, but ensure sequence exists.
                if existing.sequence != sequence and code in {
                    "professional", "club",
                }:
                    existing.write({"sequence": sequence})
                if code == "professional" and existing.name in (
                    "Professionnel / Club", "Professionnel/Club",
                ):
                    existing.write({"name": name})
                continue
            Section.create({
                "code": code,
                "name": name,
                "sequence": sequence,
            })
        return Section.search([])
