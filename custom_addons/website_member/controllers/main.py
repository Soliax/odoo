# -*- coding: utf-8 -*-
from odoo import http
from odoo.exceptions import MissingError
from odoo.http import request

from ..models.res_partner import DIVE_BREVET_SELECTION, DIVE_SPECIALTIES


class MemberDirectoryController(http.Controller):

    def _ensure_access(self):
        if not request.env.user._is_public():
            return None
        deny = request.env["ir.config_parameter"].sudo().get_param(
            "website_member.deny_redirect", "login"
        )
        if deny == "forbidden":
            return request.render(
                "website_member.members_forbidden",
                {"page_name": "member_directory"},
            )
        redirect = "/membres"
        if request.httprequest.path:
            redirect = request.httprequest.path
            if request.httprequest.query_string:
                redirect = "%s?%s" % (
                    redirect,
                    request.httprequest.query_string.decode("utf-8"),
                )
        return request.redirect("/web/login?redirect=%s" % redirect, code=303)

    def _get_intro(self):
        return request.env["ir.config_parameter"].sudo().get_param(
            "website_member.intro",
            "Meet the team",
        )

    def _parse_filters(self, kwargs):
        search = (kwargs.get("search") or "").strip()
        category = (kwargs.get("category") or "").strip().lower()
        if category not in ("", "plongeur", "hsa"):
            category = ""
        brevet = (kwargs.get("brevet") or "").strip().lower()
        specialty = (kwargs.get("specialty") or "").strip().lower()
        try:
            limit = int(kwargs.get("limit") or 0) or None
        except (TypeError, ValueError):
            limit = None
        return search, category, brevet, specialty, limit

    def _user_profile_url(self, partner):
        user = request.env["res.users"].sudo().search(
            [("partner_id", "=", partner.id), ("share", "=", False)],
            limit=1,
        )
        return "/membres/%s" % user.id if user else False

    @http.route(
        ["/membres", "/members"],
        type="http",
        auth="public",
        website=True,
        sitemap=False,
    )
    def members_list(self, search="", category="", brevet="", specialty="", **kwargs):
        denied = self._ensure_access()
        if denied:
            return denied

        search, category, brevet, specialty, _limit = self._parse_filters({
            "search": search,
            "category": category,
            "brevet": brevet,
            "specialty": specialty,
        })
        members = request.env["res.users"].get_directory_members(
            search=search or None,
            category=category or None,
            brevet=brevet or None,
            specialty=specialty or None,
        )
        return request.render(
            "website_member.members_list",
            {
                "members": members,
                "search": search,
                "category": category,
                "brevet": brevet,
                "specialty": specialty,
                "brevet_choices": DIVE_BREVET_SELECTION + [
                    ("nb", "NB"),
                    ("hsa", "HSA"),
                ],
                "specialty_choices": [
                    (code, short) for code, short, _full, _f in DIVE_SPECIALTIES
                ],
                "intro": self._get_intro(),
                "page_name": "member_directory",
            },
        )

    @http.route(
        ["/membres/<int:user_id>", "/members/<int:user_id>"],
        type="http",
        auth="public",
        website=True,
        sitemap=False,
    )
    def member_profile(self, user_id, **kwargs):
        denied = self._ensure_access()
        if denied:
            return denied

        Users = request.env["res.users"].sudo()
        member = Users.browse(user_id)
        allowed = Users.get_directory_members()
        if not member.exists() or member not in allowed:
            raise MissingError("This member profile is not available.")

        sections = member.get_directory_profile_fields(request.env.user)
        return request.render(
            "website_member.member_profile",
            {
                "member": member,
                "partner": member.partner_id,
                "sections": sections,
                "specialties": member.get_dive_specialties(),
                "categories": member.get_dive_categories(),
                "page_name": "member_directory",
            },
        )

    @http.route(
        ["/membres/snippet/members", "/members/snippet/members"],
        type="jsonrpc",
        auth="public",
        website=True,
    )
    def snippet_members(self, **kwargs):
        if request.env.user._is_public():
            return {"html": "", "error": "login_required"}

        search, category, brevet, specialty, limit = self._parse_filters(kwargs)
        show_filters = str(kwargs.get("show_filters", "1")) not in ("0", "false", "False")
        show_specialties = str(kwargs.get("show_specialties", "1")) not in ("0", "false", "False")
        columns = kwargs.get("columns") or "4"
        if columns not in ("2", "3", "4"):
            columns = "4"

        members = request.env["res.users"].get_directory_members(
            search=search or None,
            category=category or None,
            brevet=brevet or None,
            specialty=specialty or None,
            limit=limit,
        )
        html = request.env["ir.ui.view"]._render_template(
            "website_member.s_md_members_content",
            {
                "members": members,
                "search": search,
                "category": category,
                "brevet": brevet,
                "specialty": specialty,
                "show_filters": show_filters,
                "show_specialties": show_specialties,
                "columns": columns,
                "brevet_choices": DIVE_BREVET_SELECTION + [
                    ("nb", "NB"),
                    ("hsa", "HSA"),
                ],
                "specialty_choices": [
                    (code, short) for code, short, _full, _f in DIVE_SPECIALTIES
                ],
            },
        )
        return {"html": html}

    @http.route(
        ["/membres/snippet/attendees", "/members/snippet/attendees"],
        type="jsonrpc",
        auth="public",
        website=True,
    )
    def snippet_attendees(self, **kwargs):
        if request.env.user._is_public():
            return {"html": "", "error": "login_required"}

        try:
            event_id = int(kwargs.get("event_id") or 0)
        except (TypeError, ValueError):
            event_id = 0
        try:
            limit = int(kwargs.get("limit") or 0) or None
        except (TypeError, ValueError):
            limit = None
        published_only = str(kwargs.get("published_only", "1")) not in (
            "0", "false", "False",
        )

        partners = request.env["res.users"].get_event_attendee_partners(
            event_id=event_id,
            limit=limit,
            published_only=published_only,
        )
        cards = []
        for partner in partners:
            cards.append({
                "partner": partner,
                "name": partner.get_dive_display_name(),
                "brevet_css": partner.dive_brevet_css or "brevet-nb",
                "brevet_short": partner.dive_brevet_short or "NB",
                "profile_url": self._user_profile_url(partner),
            })
        html = request.env["ir.ui.view"]._render_template(
            "website_member.s_md_attendees_content",
            {
                "cards": cards,
                "event_id": event_id,
            },
        )
        return {"html": html, "count": len(cards)}
