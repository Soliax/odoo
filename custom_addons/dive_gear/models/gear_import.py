# -*- coding: utf-8 -*-
"""Import club dive gear from data/material CSV dumps into stock + maintenance."""

from __future__ import annotations

import csv
import logging
from datetime import datetime
from pathlib import Path

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from .maintenance_equipment import ANNUAL_MONTHS, HYDRO_YEARS, VISUAL_MONTHS

_logger = logging.getLogger(__name__)


def _repo_material_dir():
    return Path(__file__).resolve().parents[3] / "data" / "material"


def _parse_date(value):
    if not value:
        return False
    text = str(value).strip()
    if not text or text in ("?", "-", "--"):
        return False
    text = text[:10]
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return False


def _parse_float(value):
    if not value:
        return 0.0
    text = str(value).strip().replace(",", ".")
    try:
        return float(text)
    except ValueError:
        return 0.0


def _truthy_present(value):
    v = (value or "").strip().upper()
    return v in ("V", "OUI", "YES", "Y", "1", "TRUE", "X")


def _read_csv(path):
    raw = path.read_bytes()
    text = raw.decode("utf-8-sig", errors="replace")
    rows = list(csv.DictReader(text.splitlines()))
    # Drop empty padding rows (spreadsheet exports often pad to ~1000 lines)
    keys = [k for k in (rows[0].keys() if rows else []) if k]
    col2 = keys[1] if len(keys) > 1 else None

    def keep(row):
        if not col2:
            return any((row.get(k) or "").strip() for k in keys if k and k.upper() != "ID")
        return bool((row.get(col2) or "").strip())

    return [r for r in rows if keep(r)]


class DiveGearImportWizard(models.TransientModel):
    _name = "dive.gear.import.wizard"
    _description = "Import club dive gear from CSV"

    material_path = fields.Char(
        string="Material folder",
        default=lambda self: str(_repo_material_dir()),
        required=True,
    )
    clear_existing = fields.Boolean(
        string="Replace previous dive gear import",
        default=False,
        help="If enabled, archive previously imported dive equipment before re-import.",
    )
    result_log = fields.Text(string="Result", readonly=True)

    def action_import(self):
        self.ensure_one()
        stats = self.env["dive.gear.import.wizard"]._import_from_folder(
            self.material_path,
            clear_existing=self.clear_existing,
        )
        self.result_log = (
            "Bottles: %(bottles)s\n"
            "Regulators: %(regulators)s\n"
            "BCDs: %(bcds)s\n"
            "Other: %(other)s\n"
            "Controls linked: %(controls)s\n"
            "Maintenance requests: %(requests)s\n"
            "Errors: %(errors)s\n"
            "%(detail)s"
        ) % stats
        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "view_mode": "form",
            "res_id": self.id,
            "target": "new",
        }

    @api.model
    def _import_from_folder(self, folder, clear_existing=False):
        root = Path(folder)
        if not root.is_dir():
            raise UserError(_("Material folder not found: %s") % folder)

        def find(*needles):
            for p in root.glob("*.csv"):
                name_fold = p.name.casefold()
                if all(n.casefold() in name_fold for n in needles):
                    return p
            return None

        files = {
            "bottles": find("bouteilles") if find("bouteilles") and "contr" not in (find("bouteilles").name.casefold()) else None,
            "controls": find("contr"),
            "reg_career": find("tend", "carri") or find("detend", "carri"),
            "reg_pool": find("tend", "piscin") or find("detend", "piscin"),
            "bcds": find("gilet"),
            "other": find("autres"),
        }
        # Prefer exact bottle file (not contrôles)
        for p in root.glob("*.csv"):
            n = p.name.casefold()
            if "bouteille" in n and "contr" not in n:
                files["bottles"] = p
            elif "contr" in n and "bouteille" in n:
                files["controls"] = p
            elif "tend" in n and "carri" in n:
                files["reg_career"] = p
            elif "tend" in n and "piscin" in n:
                files["reg_pool"] = p
            elif "gilet" in n:
                files["bcds"] = p
            elif "autre" in n:
                files["other"] = p

        missing = [k for k, v in files.items() if k != "controls" and not v]
        if missing:
            raise UserError(_("Missing CSV files for: %s") % ", ".join(missing))

        if clear_existing:
            old = self.env["maintenance.equipment"].sudo().search([
                ("dive_gear_kind", "!=", False),
            ])
            old.write({"active": False})

        stats = {
            "bottles": 0,
            "regulators": 0,
            "bcds": 0,
            "other": 0,
            "controls": 0,
            "requests": 0,
            "errors": 0,
            "detail": "",
        }
        details = []
        Import = self.env["dive.gear.importer"].sudo()

        try:
            ctx = Import._prepare_context()
            bottles = _read_csv(files["bottles"])
            for row in bottles:
                Import._import_bottle(row, ctx)
                stats["bottles"] += 1
            if files["controls"]:
                for row in _read_csv(files["controls"]):
                    if Import._apply_bottle_control(row, ctx):
                        stats["controls"] += 1
            for row in _read_csv(files["reg_career"]):
                Import._import_regulator(row, ctx, location_label="Carrière")
                stats["regulators"] += 1
            for row in _read_csv(files["reg_pool"]):
                Import._import_regulator(row, ctx, location_label="Piscine")
                stats["regulators"] += 1
            for row in _read_csv(files["bcds"]):
                Import._import_bcd(row, ctx)
                stats["bcds"] += 1
            for row in _read_csv(files["other"]):
                Import._import_other(row, ctx)
                stats["other"] += 1
            stats["requests"] = Import._ensure_due_requests(ctx)
            self.env.cr.commit()
        except Exception as exc:  # noqa: BLE001
            self.env.cr.rollback()
            stats["errors"] += 1
            details.append(str(exc))
            _logger.exception("Dive gear import failed")
            raise

        stats["detail"] = "\n".join(details)
        return stats


class DiveGearImporter(models.AbstractModel):
    _name = "dive.gear.importer"
    _description = "Dive gear CSV importer helpers"

    @api.model
    def _prepare_context(self):
        company = self.env.company
        warehouse = self.env["stock.warehouse"].search(
            [("company_id", "=", company.id)], limit=1
        )
        if not warehouse:
            raise UserError(_("No warehouse found for company %s") % company.display_name)

        ProductCat = self.env["product.category"].sudo()
        root = ProductCat.search([("name", "=", "Matériel club")], limit=1)
        if not root:
            root = ProductCat.create({"name": "Matériel club"})

        def ensure_cat(name, parent):
            cat = ProductCat.search([("name", "=", name), ("parent_id", "=", parent.id)], limit=1)
            return cat or ProductCat.create({"name": name, "parent_id": parent.id})

        EqCat = self.env["maintenance.equipment.category"].sudo()

        def ensure_eq_cat(name, note):
            cat = EqCat.search([("name", "=", name)], limit=1)
            if cat:
                return cat
            return EqCat.create({"name": name, "note": note})

        team = self.env["maintenance.team"].sudo().search([], limit=1)
        if not team:
            team = self.env["maintenance.team"].sudo().create({"name": "Club matériel"})

        return {
            "company": company,
            "location": warehouse.lot_stock_id,
            "product_cats": {
                "bottle": ensure_cat("Bouteilles", root),
                "regulator": ensure_cat("Détendeurs", root),
                "bcd": ensure_cat("Gilets", root),
                "other": ensure_cat("Autres", root),
            },
            "eq_cats": {
                "bottle": ensure_eq_cat(
                    "Bouteilles plongée",
                    "Belgique: visuelle 30 mois / hydraulique 5 ans.",
                ),
                "regulator": ensure_eq_cat(
                    "Détendeurs",
                    "Entretien annuel (pratique fabricant / club).",
                ),
                "bcd": ensure_eq_cat(
                    "Gilets / Stabs",
                    "Entretien annuel (pratique club).",
                ),
                "other": ensure_eq_cat("Autre matériel", "Contrôle annuel recommandé."),
            },
            "team": team,
            "products": {},
            "by_mfr_ref": {},
        }

    @api.model
    def _product(self, ctx, kind, name, tracking="serial"):
        key = (kind, name, tracking)
        if key in ctx["products"]:
            return ctx["products"][key]
        Product = self.env["product.product"].sudo()
        existing = Product.search([
            ("name", "=", name),
            ("categ_id", "=", ctx["product_cats"][kind].id),
        ], limit=1)
        if existing:
            ctx["products"][key] = existing
            return existing
        tmpl = self.env["product.template"].sudo().create({
            "name": name,
            "type": "consu",
            "is_storable": True,
            "tracking": tracking,
            "categ_id": ctx["product_cats"][kind].id,
            "list_price": 0.0,
            "purchase_ok": False,
            "sale_ok": False,
        })
        product = tmpl.product_variant_id
        ctx["products"][key] = product
        return product

    @api.model
    def _put_in_stock(self, ctx, product, lot, qty=1.0):
        Quant = self.env["stock.quant"].sudo().with_context(inventory_mode=True)
        vals = {
            "product_id": product.id,
            "location_id": ctx["location"].id,
            "inventory_quantity": qty,
        }
        if lot:
            vals["lot_id"] = lot.id
        quant = Quant.create(vals)
        quant.action_apply_inventory()
        return quant

    @api.model
    def _lot(self, product, serial):
        Lot = self.env["stock.lot"].sudo()
        lot = Lot.search([
            ("product_id", "=", product.id),
            ("name", "=", serial),
        ], limit=1)
        if lot:
            return lot
        return Lot.create({
            "name": serial,
            "product_id": product.id,
            "company_id": self.env.company.id,
        })

    @api.model
    def _equipment_vals_common(self, ctx, kind, name, serial, note=None):
        return {
            "name": name,
            "serial_no": serial or False,
            "category_id": ctx["eq_cats"][kind].id,
            "maintenance_team_id": ctx["team"].id,
            "dive_gear_kind": kind,
            "note": note or False,
            "company_id": ctx["company"].id,
            "effective_date": fields.Date.context_today(self),
        }

    @api.model
    def _upsert_equipment(self, domain, vals):
        Eq = self.env["maintenance.equipment"].sudo()
        eq = Eq.search(domain, limit=1)
        if eq:
            eq.write(vals)
            return eq
        return Eq.create(vals)

    @api.model
    def _split_service_date(self, d):
        """CSV dates may be last service (past) or next due (future)."""
        if not d:
            return False, False
        today = fields.Date.context_today(self)
        if d > today:
            return False, d
        return d, d + relativedelta(months=ANNUAL_MONTHS)

    @api.model
    def _import_bottle(self, row, ctx):
        mfr = (row.get("Fabricant") or "").strip() or "Inconnu"
        ref = (row.get("Référence") or row.get("Reference") or "").strip()
        capacity = _parse_float(row.get("Capacité (L)") or row.get("Capacite (L)"))
        club_no = (row.get("Numéro") or row.get("Numero") or "").strip()
        note = (row.get("Note") or "").strip()
        present = _truthy_present(row.get("Présent") or row.get("Present")) or (
            (row.get("Présent") or row.get("Present") or "").strip() == "?"
        )
        entretien = _parse_date(row.get("Date entretien"))
        reepreuve = _parse_date(row.get("Date Réepreuve") or row.get("Date Reepreuve"))

        product_name = "Bouteille %s %sL" % (mfr, int(capacity) if capacity else "?")
        product = self._product(ctx, "bottle", product_name, tracking="serial")
        serial = ref or ("BOT-%s" % (club_no or row.get("ID") or fields.Datetime.now()))
        lot = self._lot(product, serial)
        self._put_in_stock(ctx, product, lot, 1)

        last_svc, next_svc = self._split_service_date(entretien)
        # Réépreuve column in this export is the next due stamp when in the future;
        # if in the past, treat as last hydro.
        last_hydro = False
        next_hydro = False
        last_visual = last_svc
        next_visual = False
        today = fields.Date.context_today(self)
        if reepreuve:
            if reepreuve > today:
                next_hydro = reepreuve
            else:
                last_hydro = reepreuve
                next_hydro = reepreuve + relativedelta(years=HYDRO_YEARS)
        if last_visual and not next_visual:
            next_visual = last_visual + relativedelta(months=VISUAL_MONTHS)

        name = "Bouteille %s%s" % (
            ("#%s " % club_no) if club_no else "",
            serial,
        )
        vals = self._equipment_vals_common(ctx, "bottle", name, serial, note)
        vals.update({
            "model": "%sL" % (int(capacity) if capacity else "?"),
            "partner_ref": mfr,
            "dive_brand": mfr,
            "dive_manufacturer_ref": ref,
            "dive_club_number": club_no or False,
            "dive_capacity_l": capacity,
            "dive_present": present,
            "dive_product_id": product.id,
            "dive_lot_id": lot.id,
            "dive_last_service_date": last_svc,
            "dive_next_service_date": next_svc,
            "dive_last_visual_date": last_visual,
            "dive_next_visual_date": next_visual,
            "dive_last_hydro_date": last_hydro,
            "dive_next_hydro_date": next_hydro,
            "effective_date": last_svc or fields.Date.context_today(self),
        })
        eq = self._upsert_equipment([
            "|",
            ("serial_no", "=", serial),
            "&",
            ("dive_gear_kind", "=", "bottle"),
            ("dive_manufacturer_ref", "=", ref),
        ], vals)
        if ref:
            ctx["by_mfr_ref"][ref] = eq
        eq._dive_schedule_from_dates()
        return eq

    @api.model
    def _apply_bottle_control(self, row, ctx):
        ref = (row.get("Numéro fabricant") or row.get("Numero fabricant") or "").strip()
        if not ref:
            return False
        eq = ctx["by_mfr_ref"].get(ref) or self.env["maintenance.equipment"].sudo().search([
            ("dive_manufacturer_ref", "=", ref),
            ("dive_gear_kind", "=", "bottle"),
        ], limit=1)
        if not eq:
            return False
        control_date = _parse_date(row.get("Date contrôle") or row.get("Date controle"))
        manufacture = _parse_date(row.get("Date de fabrication"))
        result = (row.get("Résultat contrôle") or row.get("Resultat controle") or "").strip()
        observation = (row.get("Observation") or "").strip()
        note_bits = [n for n in [eq.note or "", result and ("Contrôle: %s" % result), observation] if n]
        vals = {
            "dive_manufacture_date": manufacture or eq.dive_manufacture_date,
            "note": "<br/>".join(note_bits) if note_bits else eq.note,
        }
        if control_date:
            vals["dive_last_visual_date"] = control_date
            vals["dive_last_service_date"] = control_date
            vals["dive_next_visual_date"] = control_date + relativedelta(months=VISUAL_MONTHS)
        capacity = _parse_float(row.get("Capacité (L)") or row.get("Capacite (L)"))
        if capacity:
            vals["dive_capacity_l"] = capacity
        eq.write(vals)
        eq._dive_schedule_from_dates()
        return True

    @api.model
    def _import_regulator(self, row, ctx, location_label):
        ref = (row.get("Référence") or row.get("Reference") or "").strip() or "?"
        rtype = (row.get("Type") or "").strip() or "Détendeur"
        note = (row.get("Note") or "").strip()
        etat = (row.get("État") or row.get("Etat") or "").strip()
        present = _truthy_present(row.get("Présent") or row.get("Present"))
        entretien = _parse_date(row.get("Date entretien"))
        last_svc, next_svc = self._split_service_date(entretien)

        product = self._product(ctx, "regulator", "Détendeur club", tracking="serial")
        serial = ref if ref != "?" else "REG-%s-%s" % (location_label[:3].upper(), row.get("ID") or fields.Datetime.now())
        # Notes sometimes hold SN like BNS22595
        if note and note.upper().startswith("BNS"):
            serial = note.split()[0]
        lot = self._lot(product, serial)
        self._put_in_stock(ctx, product, lot, 1)

        name = "Détendeur %s (%s)" % (serial, location_label)
        vals = self._equipment_vals_common(ctx, "regulator", name, serial, note)
        vals.update({
            "model": rtype,
            "dive_condition": etat,
            "dive_present": present,
            "dive_location_label": location_label,
            "dive_manufacturer_ref": ref if ref != "?" else False,
            "dive_product_id": product.id,
            "dive_lot_id": lot.id,
            "dive_last_service_date": last_svc,
            "dive_next_service_date": next_svc,
            "effective_date": last_svc or fields.Date.context_today(self),
        })
        eq = self._upsert_equipment([
            ("dive_gear_kind", "=", "regulator"),
            ("serial_no", "=", serial),
        ], vals)
        eq._dive_schedule_from_dates()
        return eq

    @api.model
    def _import_bcd(self, row, ctx):
        size = (row.get("Taille") or "").strip()
        ref = (row.get("Référence") or row.get("Reference") or "").strip() or "?"
        brand = (row.get("Marque") or "").strip()
        sn = (row.get("SN") or "").strip()
        note = (row.get("Note") or "").strip()
        etat = (row.get("État") or row.get("Etat") or "").strip()
        present = _truthy_present(row.get("Présent") or row.get("Present"))
        entretien = _parse_date(row.get("Date entretien"))
        last_svc, next_svc = self._split_service_date(entretien)

        product = self._product(ctx, "bcd", "Gilet / Stab club", tracking="serial")
        serial = sn or (ref if ref != "?" else "BCD-%s" % (row.get("ID") or fields.Datetime.now()))
        lot = self._lot(product, serial)
        self._put_in_stock(ctx, product, lot, 1)

        name = "Gilet %s%s" % (
            ("%s " % brand) if brand else "",
            serial,
        )
        vals = self._equipment_vals_common(ctx, "bcd", name, serial, note)
        vals.update({
            "model": ref if ref != "?" else False,
            "dive_brand": brand or False,
            "dive_size": size or False,
            "dive_condition": etat,
            "dive_present": present,
            "dive_manufacturer_ref": ref if ref != "?" else False,
            "dive_product_id": product.id,
            "dive_lot_id": lot.id,
            "dive_last_service_date": last_svc,
            "dive_next_service_date": next_svc,
            "effective_date": last_svc or fields.Date.context_today(self),
        })
        eq = self._upsert_equipment([
            ("dive_gear_kind", "=", "bcd"),
            ("serial_no", "=", serial),
        ], vals)
        eq._dive_schedule_from_dates()
        return eq

    @api.model
    def _import_other(self, row, ctx):
        label = (row.get("Matériel") or row.get("Materiel") or "").strip() or "Autre"
        qty = _parse_float(row.get("Quantité") or row.get("Quantite")) or 1.0
        note = (row.get("Note") or "").strip()
        product = self._product(ctx, "other", label, tracking="none")
        self._put_in_stock(ctx, product, None, qty)
        vals = self._equipment_vals_common(ctx, "other", label, False, note)
        vals.update({
            "dive_product_id": product.id,
            "dive_present": True,
            "dive_next_service_date": fields.Date.context_today(self) + relativedelta(
                months=ANNUAL_MONTHS
            ),
        })
        return self._upsert_equipment([
            ("dive_gear_kind", "=", "other"),
            ("name", "=", label),
        ], vals)

    @api.model
    def _ensure_due_requests(self, ctx):
        today = fields.Date.context_today(self)
        Eq = self.env["maintenance.equipment"].sudo()
        Request = self.env["maintenance.request"].sudo()
        stage = self.env["maintenance.stage"].sudo().search([], order="sequence", limit=1)
        created = 0
        due = Eq.search([("dive_gear_kind", "!=", False), ("dive_maintenance_due", "=", True)])
        for eq in due:
            reasons = []
            if eq.dive_next_visual_date and eq.dive_next_visual_date <= today:
                reasons.append("Réépreuve visuelle due (%s)" % eq.dive_next_visual_date)
            if eq.dive_next_hydro_date and eq.dive_next_hydro_date <= today:
                reasons.append("Réépreuve hydraulique due (%s)" % eq.dive_next_hydro_date)
            if eq.dive_next_service_date and eq.dive_next_service_date <= today:
                reasons.append("Entretien annuel dû (%s)" % eq.dive_next_service_date)
            subject = " / ".join(reasons) or "Entretien matériel dû"
            existing = Request.search([
                ("equipment_id", "=", eq.id),
                ("stage_id.done", "=", False),
                ("name", "ilike", "Réépreuve"),
            ], limit=1) if "done" in self.env["maintenance.stage"]._fields else Request.search([
                ("equipment_id", "=", eq.id),
                ("close_date", "=", False),
            ], limit=1)
            if existing:
                continue
            Request.create({
                "name": subject,
                "equipment_id": eq.id,
                "category_id": eq.category_id.id,
                "maintenance_team_id": ctx["team"].id,
                "schedule_date": fields.Datetime.now(),
                "request_date": today,
                "maintenance_type": "preventive",
                "stage_id": stage.id if stage else False,
            })
            created += 1
        return created
