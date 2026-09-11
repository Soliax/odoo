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
    "1": 1, "2": 2, "3": 3, "4": 4,
    "am": 5, "mc": 6, "mf": 7, "mn": 8,
}

DIVE_BREVET_SHORT = {
    "1": "1*", "2": "2*", "3": "3*", "4": "4*",
    "am": "AM", "mc": "MC", "mf": "MF", "mn": "MN",
}

# code, field name, form label
DIVE_BREVET_DATES = [
    ("1", "dive_brevet_date_1", "1*"),
    ("2", "dive_brevet_date_2", "2*"),
    ("3", "dive_brevet_date_3", "3*"),
    ("4", "dive_brevet_date_4", "4*"),
    ("am", "dive_brevet_date_am", "AM"),
    ("mc", "dive_brevet_date_mc", "MC"),
    ("mf", "dive_brevet_date_mf", "MF"),
    ("mn", "dive_brevet_date_mn", "MN"),
]

# code, short label, full label, field name
DIVE_SPECIALTIES = [
    ("cfps", "CFPS", "Certificat Federal Premier Secours", "dive_spec_cfps"),
    ("ve", "VE", "Vetement Etanche", "dive_spec_ve"),
    ("pn", "PN", "Plongeur Nitrox", "dive_spec_pn"),
    ("pnc", "PNC", "Plongeur Nitrox Confirme", "dive_spec_pnc"),
    ("in", "IN", "Instructeur Nitrox", "dive_spec_in"),
    ("inc", "INC", "Instructeur Nitrox Confirme", "dive_spec_inc"),
    ("fn", "FN", "Formateur Nitrox", "dive_spec_fn"),
]

class ResPartner(models.Model):
    _inherit = "res.partner"

    dive_firstname = fields.Char(string="Prenom")
    dive_lastname = fields.Char(string="Nom")
    dive_gender = fields.Selection(
        [("M", "Homme"), ("F", "Femme")],
        string="Sexe",
    )
    dive_member_since = fields.Date(string="Membre depuis")
    dive_phone_home = fields.Char(string="Telephone domicile")
    dive_phone_work = fields.Char(string="Telephone professionnel")
    dive_birthday = fields.Date(string="Date de naissance")
    dive_profession = fields.Char(string="Profession")
    dive_is_plongeur = fields.Boolean(string="Plongeur", default=True)
    dive_is_hsa = fields.Boolean(string="HSA (Hockey subaquatique)", default=False)

    # Other federations / certifications (free text; empty in legacy export for now)
    dive_fed_adip = fields.Char(string="ADIP")
    dive_fed_cedip = fields.Char(string="CEDIP")
    dive_fed_ida = fields.Char(string="IDA")
    dive_fed_protec = fields.Char(string="PROTEC")
    dive_fed_ssi = fields.Char(string="SSI")

    # Obtention dates for each LIFRAS brevet (filled date = earned)
    dive_brevet_date_1 = fields.Date(string="1*")
    dive_brevet_date_2 = fields.Date(string="2*")
    dive_brevet_date_3 = fields.Date(string="3*")
    dive_brevet_date_4 = fields.Date(string="4*")
    dive_brevet_date_am = fields.Date(string="AM")
    dive_brevet_date_mc = fields.Date(string="MC")
    dive_brevet_date_mf = fields.Date(string="MF")
    dive_brevet_date_mn = fields.Date(string="MN")

    dive_brevet = fields.Selection(
        DIVE_BREVET_SELECTION,
        string="Brevet LIFRAS",
    )
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

    # Specialites: a filled date means the title is earned
    dive_spec_cfps = fields.Date(string="CFPS")
    dive_spec_ve = fields.Date(string="VE")
    dive_spec_pn = fields.Date(string="PN")
    dive_spec_pnc = fields.Date(string="PNC")
    dive_spec_in = fields.Date(string="IN")
    dive_spec_inc = fields.Date(string="INC")
    dive_spec_fn = fields.Date(string="FN")
    dive_cfps_end = fields.Date(string="Date Fin CFPS")

    # legacy fields kept for upgrade safety (hidden in views)
    dive_cfps = fields.Boolean(string="CFPS (legacy)")
    dive_nitrox_basic_date = fields.Date(string="Date Nitrox Basic (legacy)")
    dive_cfps_start = fields.Date(string="Date Debut CFPS (legacy)")

    def _highest_brevet_from_dates(self):
        self.ensure_one()
        best = False
        best_rank = 0
        for code, fname, _label in DIVE_BREVET_DATES:
            if self[fname]:
                rank = DIVE_BREVET_RANK[code]
                if rank >= best_rank:
                    best_rank = rank
                    best = code
        return best

    def _sync_brevet_from_dates(self):
        for partner in self:
            highest = partner._highest_brevet_from_dates()
            if highest and partner.dive_brevet != highest:
                partner.dive_brevet = highest

    @api.model_create_multi
    def create(self, vals_list):
        partners = super().create(vals_list)
        partners._sync_brevet_from_dates()
        return partners

    def write(self, vals):
        res = super().write(vals)
        if any(fname in vals for _c, fname, _l in DIVE_BREVET_DATES):
            self._sync_brevet_from_dates()
        return res

    @api.depends("dive_brevet")
    def _compute_dive_brevet_meta(self):
        selection = dict(DIVE_BREVET_SELECTION)
        for partner in self:
            brevet = partner.dive_brevet or False
            if brevet:
                partner.dive_brevet_label = selection.get(brevet, "")
                partner.dive_brevet_short = DIVE_BREVET_SHORT.get(brevet, "")
                partner.dive_brevet_rank = DIVE_BREVET_RANK.get(brevet, 0)
                partner.dive_brevet_css = "brevet-%s" % brevet
            else:
                # No LIFRAS brevet → NB. HSA is a category, never a brevet.
                partner.dive_brevet_label = "NB - Non Brevete"
                partner.dive_brevet_short = "NB"
                partner.dive_brevet_rank = 0
                partner.dive_brevet_css = "brevet-nb"

    def get_dive_display_name(self):
        self.ensure_one()
        parts = [p for p in [self.dive_firstname, self.dive_lastname] if p]
        return " ".join(parts) if parts else self.name

    def get_dive_categories(self):
        self.ensure_one()
        cats = []
        if self.dive_is_plongeur:
            cats.append({"code": "plongeur", "short": "Plongeur", "label": "Plongeur", "css": "cat-plongeur"})
        if self.dive_is_hsa:
            cats.append({"code": "hsa", "short": "HSA", "label": "Hockey subaquatique", "css": "cat-hsa"})
        return cats

    def get_dive_brevet_dates(self):
        """Return earned brevets as payloads (date filled => obtained)."""
        self.ensure_one()
        selection = dict(DIVE_BREVET_SELECTION)
        items = []
        for code, fname, short in DIVE_BREVET_DATES:
            obtained = self[fname]
            if obtained:
                items.append({
                    "code": code,
                    "short": short,
                    "label": selection.get(code, short),
                    "date": obtained.strftime("%d-%m-%y"),
                    "css": "brevet-%s" % code,
                })
        return items

    def get_dive_specialties(self):
        """Return earned specialties as pill payloads (date filled => title owned)."""
        self.ensure_one()
        pills = []
        for code, short, full, fname in DIVE_SPECIALTIES:
            obtained = self[fname]
            if obtained:
                pills.append({
                    "code": code,
                    "short": short,
                    "label": full,
                    "date": obtained.strftime("%d-%m-%y"),
                    "css": "spec-%s" % code,
                })
        return pills
