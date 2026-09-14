# -*- coding: utf-8 -*-
"""Ensure Waterloo Diving Club company, fr_BE language, and club groups."""

from __future__ import annotations

import base64
import logging

from odoo import api, models

_logger = logging.getLogger(__name__)

WDC_COMPANY_XMLID = "website_member.company_wdc"
WDC_COMPANY_NAME = "Waterloo Diving Club"


def _is_oa_function(function):
    """Club board / officer roles — not plain 'Membre'."""
    text = (function or "").strip()
    if not text:
        return False
    return text.casefold() not in ("membre", "member")


class ResCompany(models.Model):
    _inherit = "res.company"

    @api.model
    def _ensure_wdc_company(self):
        """Create or update the Waterloo Diving Club company (not the SF demo)."""
        env = self.env
        company = env.ref(WDC_COMPANY_XMLID, raise_if_not_found=False)
        if not company:
            company = self.sudo().search([("name", "=", WDC_COMPANY_NAME)], limit=1)

        be = env.ref("base.be", raise_if_not_found=False)
        eur = env.ref("base.EUR", raise_if_not_found=False)
        state = env["res.country.state"].sudo().search([
            ("country_id", "=", be.id if be else False),
            ("code", "=", "WBR"),
        ], limit=1)

        vals = {
            "name": WDC_COMPANY_NAME,
            "street": "Rue Théophile Delbar, 33",
            "street2": "Boite 1",
            "zip": "1410",
            "city": "Waterloo",
            "country_id": be.id if be else False,
            "state_id": state.id if state else False,
            "vat": "BE0477472701",
            "email": "wdc@waterloodivingclub.be",
            "website": "https://www.waterloodivingclub.be/",
            "currency_id": eur.id if eur else False,
            "color": 5,
        }

        if company:
            # Do not wipe a custom logo already set in the UI.
            company.sudo().write({k: v for k, v in vals.items() if v})
        else:
            logo = self._wdc_logo_b64()
            if logo:
                vals["logo"] = logo
            company = self.sudo().create(vals)

        self._bind_xmlid(WDC_COMPANY_XMLID, company)
        return company

    @api.model
    def _wdc_logo_b64(self):
        try:
            from odoo.tools.misc import file_open
            with file_open("website_wdc/static/src/img/logo/logo-2.png", "rb") as f:
                return base64.b64encode(f.read())
        except (FileNotFoundError, OSError, ValueError):
            return False

    @api.model
    def _bind_xmlid(self, xml_id, record):
        module, name = xml_id.split(".", 1)
        Imd = self.env["ir.model.data"].sudo()
        existing = Imd.search([
            ("module", "=", module),
            ("name", "=", name),
        ], limit=1)
        if existing:
            if existing.res_id != record.id or existing.model != record._name:
                existing.write({
                    "model": record._name,
                    "res_id": record.id,
                    "noupdate": True,
                })
            return
        Imd.create({
            "module": module,
            "name": name,
            "model": record._name,
            "res_id": record.id,
            "noupdate": True,
        })


class ResLang(models.Model):
    _inherit = "res.lang"

    @api.model
    def _ensure_fr_be(self):
        lang = self.with_context(active_test=False).sudo().search(
            [("code", "=", "fr_BE")], limit=1
        )
        if not lang:
            _logger.warning("Language fr_BE is not available in this database.")
            return self.browse()
        if not lang.active:
            # Preferred Odoo API when present.
            if hasattr(lang, "_activate_lang"):
                self.sudo()._activate_lang("fr_BE")
            else:
                lang.sudo().write({"active": True})
            lang = self.sudo().search([("code", "=", "fr_BE")], limit=1)
        return lang


class ResUsers(models.Model):
    _inherit = "res.users"

    @api.model
    def _club_import_context(self):
        """Company, language and groups used by CB member import."""
        company = self.env["res.company"]._ensure_wdc_company()
        lang = self.env["res.lang"]._ensure_fr_be()
        group_user = self.env.ref("base.group_user")
        group_plongeurs = self.env.ref("website_member.group_plongeurs")
        group_hsa = self.env.ref("website_member.group_hsa")
        group_oa = self.env.ref("website_member.group_oa")
        return {
            "company": company,
            "lang": lang.code if lang else "fr_BE",
            "group_user": group_user,
            "group_plongeurs": group_plongeurs,
            "group_hsa": group_hsa,
            "group_oa": group_oa,
        }

    @api.model
    def _club_managed_group_ids(self, ctx=None):
        ctx = ctx or self._club_import_context()
        return {
            ctx["group_user"].id,
            ctx["group_plongeurs"].id,
            ctx["group_hsa"].id,
            ctx["group_oa"].id,
        }

    @api.model
    def _club_group_ids_for_member(self, plongeur=False, hsa=False, function=None, ctx=None):
        """Internal user + Plongeurs / HSA from flags + OA for club officers."""
        ctx = ctx or self._club_import_context()
        ids = [ctx["group_user"].id]
        if plongeur:
            ids.append(ctx["group_plongeurs"].id)
        if hsa:
            ids.append(ctx["group_hsa"].id)
        if _is_oa_function(function):
            ids.append(ctx["group_oa"].id)
        return ids

    @api.model
    def _reassign_members_to_wdc(self):
        """Move published members onto WDC + fr_BE + club groups."""
        ctx = self._club_import_context()
        company = ctx["company"]
        lang = ctx["lang"]
        managed = self._club_managed_group_ids(ctx)
        # Drop obsolete combined group if still present from earlier installs.
        old = self.env.ref("website_member.group_hsa_plongeurs", raise_if_not_found=False)
        if old:
            managed.add(old.id)
        members = self.sudo().search([
            ("members_published", "=", True),
            ("share", "=", False),
        ])
        for user in members:
            partner = user.partner_id
            group_ids = self._club_group_ids_for_member(
                plongeur=bool(partner.dive_is_plongeur),
                hsa=bool(partner.dive_is_hsa),
                function=partner.function,
                ctx=ctx,
            )
            keep = [gid for gid in user.group_ids.ids if gid not in managed]
            user.with_context(
                tracking_disable=True,
                mail_notrack=True,
                no_reset_password=True,
            ).write({
                "company_id": company.id,
                "company_ids": [(6, 0, [company.id])],
                "lang": lang,
                "group_ids": [(6, 0, list(dict.fromkeys(keep + group_ids)))],
            })
            partner.with_context(
                tracking_disable=True, mail_notrack=True
            ).write({
                "lang": lang,
                "company_id": False,  # shared contact usable with the company
            })
        if old:
            old.sudo().unlink()
        _logger.info(
            "Reassigned %s published members to %s / %s",
            len(members), company.name, lang,
        )
        return len(members)
