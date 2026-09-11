# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models

# Belgian practice for club dive cylinders:
# - Optical / visual retest every 30 months (2.5 years)
# - Hydrostatic (+ optical) every 5 years
# Regulators / BCDs: annual professional service (manufacturer / club practice)
VISUAL_MONTHS = 30
HYDRO_YEARS = 5
ANNUAL_MONTHS = 12


class MaintenanceEquipment(models.Model):
    _inherit = "maintenance.equipment"

    dive_gear_kind = fields.Selection(
        [
            ("bottle", "Bouteille"),
            ("regulator", "Détendeur"),
            ("bcd", "Gilet / Stab"),
            ("other", "Autre"),
        ],
        string="Type matériel plongée",
        index=True,
    )
    dive_club_number = fields.Char(string="N° club", help="Numéro interne club (CSV Numéro)")
    dive_manufacturer_ref = fields.Char(string="Réf. fabricant")
    dive_capacity_l = fields.Float(string="Capacité (L)")
    dive_present = fields.Boolean(string="Présent", default=True)
    dive_condition = fields.Char(string="État")
    dive_brand = fields.Char(string="Marque")
    dive_size = fields.Char(string="Taille")
    dive_location_label = fields.Char(
        string="Emplacement club",
        help="Ex. Piscine / Carrière",
    )
    dive_product_id = fields.Many2one("product.product", string="Article stock")
    dive_lot_id = fields.Many2one("stock.lot", string="N° de série / lot")

    dive_last_service_date = fields.Date(string="Dernier entretien")
    dive_next_service_date = fields.Date(string="Prochain entretien")
    dive_last_visual_date = fields.Date(string="Dernière réépreuve visuelle")
    dive_next_visual_date = fields.Date(string="Prochaine visuelle (30 mois)")
    dive_last_hydro_date = fields.Date(string="Dernière réépreuve hydraulique")
    dive_next_hydro_date = fields.Date(string="Prochaine hydraulique (5 ans)")
    dive_manufacture_date = fields.Date(string="Date de fabrication")

    dive_maintenance_due = fields.Boolean(
        string="Entretien dû",
        compute="_compute_dive_due",
        search="_search_dive_maintenance_due",
    )

    @api.depends(
        "dive_next_service_date",
        "dive_next_visual_date",
        "dive_next_hydro_date",
    )
    def _compute_dive_due(self):
        today = fields.Date.context_today(self)
        for eq in self:
            dates = [
                eq.dive_next_service_date,
                eq.dive_next_visual_date,
                eq.dive_next_hydro_date,
            ]
            eq.dive_maintenance_due = any(d and d <= today for d in dates)

    def _search_dive_maintenance_due(self, operator, value):
        today = fields.Date.context_today(self)
        domain = [
            "|", "|",
            ("dive_next_service_date", "<=", today),
            ("dive_next_visual_date", "<=", today),
            ("dive_next_hydro_date", "<=", today),
        ]
        if operator in ("=", "!=") and not value:
            return ["!"] + domain if operator == "=" else domain
        if operator in ("=", "!=") and value:
            return domain if operator == "=" else ["!"] + domain
        return domain

    def _dive_schedule_from_dates(self):
        """Fill next-* dates from last-* using Belgian intervals when missing."""
        for eq in self:
            if eq.dive_gear_kind == "bottle":
                if eq.dive_last_visual_date and not eq.dive_next_visual_date:
                    eq.dive_next_visual_date = eq.dive_last_visual_date + relativedelta(
                        months=VISUAL_MONTHS
                    )
                if eq.dive_last_hydro_date and not eq.dive_next_hydro_date:
                    eq.dive_next_hydro_date = eq.dive_last_hydro_date + relativedelta(
                        years=HYDRO_YEARS
                    )
                # If CSV only gave a single "entretien" date, treat as last visual.
                if eq.dive_last_service_date and not eq.dive_last_visual_date:
                    eq.dive_last_visual_date = eq.dive_last_service_date
                    if not eq.dive_next_visual_date:
                        eq.dive_next_visual_date = eq.dive_last_service_date + relativedelta(
                            months=VISUAL_MONTHS
                        )
            elif eq.dive_gear_kind in ("regulator", "bcd", "other"):
                if eq.dive_last_service_date and not eq.dive_next_service_date:
                    eq.dive_next_service_date = eq.dive_last_service_date + relativedelta(
                        months=ANNUAL_MONTHS
                    )
