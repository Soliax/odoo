# -*- coding: utf-8 -*-
from odoo import api, fields, models

DIVE_BREVET_SELECTION = [
    ("1", "1*"),
    ("2", "2*"),
    ("3", "3*"),
    ("4", "4*"),
    ("am", "AM - Assistant Moniteur"),
    ("mc", "MC - Moniteur Club"),
    ("mf", "MF - Moniteur Federal"),
    ("mn", "MN - Moniteur National"),
]

DIVE_BREVET_RANK = {
    "1": 1,
    "2": 2,
    "3": 3,
    "4": 4,
    "am": 5,
    "mc": 6,
    "mf": 7,
    "mn": 8,
}

DIVE_BREVET_SHORT = {
    "1": "1*",
    "2": "2*",
    "3": "3*",
    "4": "4*",
    "am": "AM",
    "mc": "MC",
    "mf": "MF",
    "mn": "MN",
}


class ResPartner(models.Model):
    _inherit = "res.partner"

    dive_firstname = fields.Char(string="Prenom")
    dive_lastname = fields.Char(string="Nom")
    dive_phone_home = fields.Char(string="Telephone domicile")
    dive_phone_work = fields.Char(string="Telephone professionnel")
    dive_birthday = fields.Date(string="Date de naissance")
    dive_profession = fields.Char(string="Profession")
    dive_brevet = fields.Selection(DIVE_BREVET_SELECTION, string="Brevet LIFRAS")
    dive_brevet_label = fields.Char(compute="_compute_dive_brevet_meta")
    dive_brevet_short = fields.Char(compute="_compute_dive_brevet_meta")
    dive_brevet_rank = fields.Integer(compute="_compute_dive_brevet_meta", store=True)
    dive_brevet_css = fields.Char(compute="_compute_dive_brevet_meta")
    dive_contact_name = fields.Char(string="Personne de contact")
    dive_contact_phone = fields.Char(string="Telephone du contact")
    dive_last_medical = fields.Date(string="Derniere Visite Medicale")
    dive_last_ecg = fields.Date(string="Dernier ECG Effort")
    dive_lifras_id = fields.Char(string="ID membre Lifras")
    dive_other_brevets = fields.Text(string="Autres Brevets")
    dive_cfps = fields.Boolean(string="CFPS")
    dive_nitrox_basic_date = fields.Date(string="Date Nitrox Basic")
    dive_cfps_start = fields.Date(string="Date Debut CFPS")
    dive_cfps_end = fields.Date(string="Date Fin CFPS")

    @api.depends("dive_brevet")
    def _compute_dive_brevet_meta(self):
        selection = dict(DIVE_BREVET_SELECTION)
        for partner in self:
            brevet = partner.dive_brevet or False
            partner.dive_brevet_label = selection.get(brevet, "")
            partner.dive_brevet_short = DIVE_BREVET_SHORT.get(brevet, "")
            partner.dive_brevet_rank = DIVE_BREVET_RANK.get(brevet, 0)
            partner.dive_brevet_css = ("brevet-%s" % brevet) if brevet else "brevet-none"

    def get_dive_display_name(self):
        self.ensure_one()
        parts = [p for p in [self.dive_firstname, self.dive_lastname] if p]
        return " ".join(parts) if parts else self.name
