# -*- coding: utf-8 -*-
"""Import club members from the legacy Community Builder JSON export."""

from __future__ import annotations

import base64
import json
import logging
import random
import re
import tempfile
from datetime import datetime
from pathlib import Path

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

DEFAULT_PASSWORD = "password123"

BREVET_MAP = {
    "nb": False,
    "1*": "1",
    "1": "1",
    "2*": "2",
    "2": "2",
    "3*": "3",
    "3": "3",
    "4*": "4",
    "4": "4",
    "am": "am",
    "mc": "mc",
    "mf": "mf",
    "mn": "mn",
}

TOKEN_SPEC_FIELD = {
    "nitrox basic": "dive_spec_pn",
    "nitrox advanced": "dive_spec_pnc",
    "etanche": "dive_spec_ve",
    "cfps": "dive_spec_cfps",
    "instructeur nitrox": "dive_spec_in",
}

TOKEN_OTHER = {
    "dan o2 provider",
    "padi open water",
    "padi advanced",
    "padi divemaster",
}


def _repo_data_dir():
    return Path(__file__).resolve().parents[3] / "data"


def _parse_date(value):
    if not value or value in ("0000-00-00", "0000-00-00 00:00:00", "--", "None"):
        return False
    text = str(value).strip()[:10]
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return False


def _clean_phone(value):
    if not value or str(value).strip() in ("--", "-", "None"):
        return False
    return str(value).strip()


def _categories_from_nomcomplet(nom):
    text = (nom or "").lower()
    has_hsa = bool(re.search(r"hockey|\bhsa\b", text, flags=re.I))
    has_pl = bool(re.search(r"plongeur|pl\s*/", text, flags=re.I))
    has_2eme = bool(
        re.search(r"2\s*[eèê]me\s+appartenance|2de\s+appartenance", text, flags=re.I)
    )
    hsa = has_hsa or has_2eme
    if has_pl:
        plongeur = True
    elif has_hsa and not has_2eme:
        plongeur = False
    else:
        plongeur = True
    return plongeur, hsa


class MemberImportWizard(models.TransientModel):
    _name = "member.import.wizard"
    _description = "Import members from CB JSON export"

    export_file = fields.Binary(
        string="Export JSON file",
        help="Upload users_export.txt / .json from Community Builder.",
    )
    export_filename = fields.Char(string="Filename")
    default_password = fields.Char(
        string="Default password",
        default=DEFAULT_PASSWORD,
        required=True,
    )
    use_random_avatars = fields.Boolean(
        string="Assign random placeholder avatars",
        default=True,
        help="Only used when local data/avatars folders exist (dev). "
             "In production, leave members without photo or upload later.",
    )
    result_log = fields.Text(string="Result", readonly=True)

    def action_import(self):
        self.ensure_one()
        if not self.export_file:
            raise UserError(_("Please upload the CB JSON export file."))

        raw = base64.b64decode(self.export_file)
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
            tmp.write(raw)
            tmp_path = Path(tmp.name)

        avatars_path = None
        if self.use_random_avatars:
            candidate = _repo_data_dir() / "avatars"
            if candidate.is_dir():
                avatars_path = candidate

        try:
            stats = self.env["res.users"].import_members_from_cb_export(
                export_path=tmp_path,
                avatars_path=avatars_path,
                password=self.default_password,
            )
        finally:
            try:
                tmp_path.unlink(missing_ok=True)
            except OSError:
                pass

        self.result_log = (
            "Created: %(created)s\n"
            "Updated: %(updated)s\n"
            "Skipped: %(skipped)s\n"
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


class ResUsers(models.Model):
    _inherit = "res.users"

    @api.model
    def import_members_from_cb_export(self, export_path=None, avatars_path=None, password=None):
        export_path = Path(export_path) if export_path else (_repo_data_dir() / "users_export.txt")
        password = password or DEFAULT_PASSWORD
        if not export_path.is_file():
            raise UserError(_("Export file not found: %s") % export_path)

        try:
            rows = json.loads(export_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise UserError(_("Invalid JSON export: %s") % exc) from exc
        if not isinstance(rows, list):
            raise UserError(_("Export root must be a JSON list of users."))

        man_avatars, woman_avatars = [], []
        if avatars_path:
            avatars_path = Path(avatars_path)
            if avatars_path.exists():
                man_avatars = [
                    p for p in (avatars_path / "man").glob("*")
                    if p.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp")
                ]
                woman_avatars = [
                    p for p in (avatars_path / "woman").glob("*")
                    if p.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp")
                ]

        stats = {"created": 0, "updated": 0, "skipped": 0, "errors": 0, "detail": ""}
        details = []
        group_user = self.env.ref("base.group_user")

        for i, row in enumerate(rows, 1):
            try:
                created = self._import_one_cb_member(
                    row,
                    password=password,
                    group_user=group_user,
                    man_avatars=man_avatars,
                    woman_avatars=woman_avatars,
                )
                if created is True:
                    stats["created"] += 1
                elif created is False:
                    stats["updated"] += 1
                else:
                    stats["skipped"] += 1
                if i % 10 == 0:
                    self.env.cr.commit()
                    _logger.info("Member import progress %s/%s", i, len(rows))
            except Exception as exc:  # noqa: BLE001
                self.env.cr.rollback()
                stats["errors"] += 1
                details.append("%s: %s" % (row.get("username") or row.get("email"), exc))
                _logger.exception("Member import failed for %s", row.get("username"))

        stats["detail"] = "\n".join(details[:40])
        return stats

    @api.model
    def _import_one_cb_member(self, row, password, group_user, man_avatars, woman_avatars):
        email = (row.get("email") or "").strip().lower()
        login = (row.get("username") or "").strip().lower()
        firstname = (row.get("firstname") or "").strip()
        lastname = (row.get("lastname") or "").strip()
        if not login and email:
            login = email.split("@")[0]
        if not login:
            return None

        user = self._find_cb_import_user(
            row, email=email, login=login, firstname=firstname, lastname=lastname
        )
        is_new = not user

        gender = (row.get("cb_sexe") or "").strip().upper()
        if gender not in ("M", "F"):
            gender = False

        plongeur, hsa = _categories_from_nomcomplet(row.get("cb_nomcomplet") or "")
        brevet_raw = (row.get("cb_brevet") or "NB").strip().lower()
        brevet = BREVET_MAP.get(brevet_raw, False)

        partner_vals = {
            "name": " ".join(p for p in [firstname, lastname] if p) or row.get("name") or login,
            "dive_firstname": firstname or False,
            "dive_lastname": lastname or False,
            "dive_gender": gender,
            "email": email or False,
            "phone": _clean_phone(row.get("cb_portable")),
            "dive_phone_home": _clean_phone(row.get("cb_teldomicile")),
            "dive_phone_work": _clean_phone(row.get("cb_telprof")),
            "street": (row.get("cb_adresse") or "").strip() or False,
            "zip": (row.get("cb_codepostal") or "").strip() or False,
            "city": (row.get("cb_ville") or "").strip() or False,
            "function": (row.get("cb_fonction") or "").strip() or False,
            "dive_profession": (row.get("cb_profession") or "").strip() or False,
            "dive_birthday": _parse_date(row.get("cb_naissance")),
            "dive_member_since": _parse_date(row.get("cb_inscription")),
            "dive_lifras_id": (row.get("cb_idmembgemeli") or "").strip() or False,
            "dive_contact_name": (row.get("cb_personnedecontact") or "").strip() or False,
            "dive_contact_phone": _clean_phone(row.get("cb_telperscontact")),
            "dive_last_medical": _parse_date(row.get("cb_visitemdicale")),
            "dive_last_ecg": _parse_date(row.get("cb_ecgeffort")),
            "dive_is_plongeur": plongeur,
            "dive_is_hsa": hsa,
            "dive_brevet": brevet,
            "dive_brevet_date_1": _parse_date(row.get("cb_brevetp1")),
            "dive_brevet_date_2": _parse_date(row.get("cb_brevetp2")),
            "dive_brevet_date_3": _parse_date(row.get("cb_brevetp3")),
            "dive_brevet_date_4": _parse_date(row.get("cb_brevetp4")),
            "dive_brevet_date_am": _parse_date(row.get("cb_brevetam")),
            "dive_brevet_date_mc": _parse_date(row.get("cb_brevetmc")),
            "dive_brevet_date_mf": _parse_date(row.get("cb_brevetmf")),
            "dive_brevet_date_mn": _parse_date(row.get("cb_brevetmn")),
            "dive_spec_pn": _parse_date(row.get("cb_datenitroxbasic")),
            "dive_spec_pnc": _parse_date(row.get("cb_datenitroxadvanced")),
            "dive_spec_ve": _parse_date(row.get("cb_datebrevetetanche")),
            "dive_spec_cfps": _parse_date(row.get("cb_datedebutcfps")),
            "dive_cfps_end": _parse_date(row.get("cb_datefincfps")),
            "dive_fed_adip": (row.get("cb_brevet_adip") or "").strip() or False,
            "dive_fed_cedip": (row.get("cb_brevet_cedip") or "").strip() or False,
            "dive_fed_ida": (row.get("cb_brevet_ida") or "").strip() or False,
            "dive_fed_protec": (row.get("cb_brevet_protec") or "").strip() or False,
            "dive_fed_ssi": (row.get("cb_brevet_ssi") or "").strip() or False,
        }

        other_bits = []
        autre = (row.get("cb_brevet_autre") or "").strip()
        if autre:
            other_bits.append(autre)

        fallback_date = (
            partner_vals["dive_member_since"]
            or partner_vals["dive_spec_cfps"]
            or partner_vals["dive_birthday"]
            or fields.Date.today()
        )
        for token in re.split(r"\|\*\|", row.get("cb_autresbrevets") or ""):
            token = token.strip()
            if not token:
                continue
            key = token.lower()
            fname = TOKEN_SPEC_FIELD.get(key)
            if fname:
                if not partner_vals.get(fname):
                    partner_vals[fname] = fallback_date
                continue
            if key in TOKEN_OTHER or key not in TOKEN_SPEC_FIELD:
                other_bits.append(token)
        if other_bits:
            partner_vals["dive_other_brevets"] = " / ".join(dict.fromkeys(other_bits))

        pool = woman_avatars if gender == "F" else man_avatars
        if pool:
            avatar_path = random.choice(pool)
            partner_vals["image_1920"] = base64.b64encode(avatar_path.read_bytes())

        if is_new:
            base_login = login
            n = 1
            while self.sudo().search_count([("login", "=", login)]):
                n += 1
                login = "%s%s" % (base_login, n)
            image = partner_vals.pop("image_1920", False)
            user = self.sudo().with_context(
                no_reset_password=True,
                tracking_disable=True,
                mail_create_nolog=True,
                mail_notrack=True,
                mail_auto_delete=False,
                send_email=False,
            ).create({
                "name": partner_vals["name"],
                "login": login,
                "email": email or False,
                "password": password,
                "group_ids": [(6, 0, [group_user.id])],
                "members_published": True,
                "notification_type": "inbox",
            })
            if image:
                partner_vals["image_1920"] = image
            user.partner_id.with_context(
                tracking_disable=True, mail_notrack=True
            ).write(partner_vals)
            return True

        user.partner_id.with_context(
            tracking_disable=True, mail_notrack=True
        ).write(partner_vals)
        vals = {"members_published": True}
        if email and (user.email or "").lower() != email:
            vals["email"] = email
        if vals:
            user.with_context(
                tracking_disable=True, mail_notrack=True, no_reset_password=True
            ).write(vals)
        return False

    @api.model
    def _find_cb_import_user(self, row, email, login, firstname, lastname):
        Users = self.sudo()
        if lastname.lower() == "aubry" or "aubry" in email:
            user = Users.search([
                "|", "|", "|",
                ("login", "=", "diver.2star"),
                ("login", "=", "vinab"),
                ("email", "ilike", "aubry"),
                "&",
                ("dive_firstname", "ilike", "Vinciane"),
                ("dive_lastname", "ilike", "Aubry"),
            ], limit=1)
            if user:
                return user
        if email:
            user = Users.search([("email", "=ilike", email)], limit=1)
            if user:
                return user
        if login:
            user = Users.search([("login", "=", login)], limit=1)
            if user:
                return user
        if firstname and lastname:
            user = Users.search([
                ("dive_firstname", "=ilike", firstname),
                ("dive_lastname", "=ilike", lastname),
            ], limit=1)
            if user:
                return user
        return Users.browse()
