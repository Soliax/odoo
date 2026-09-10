# -*- coding: utf-8 -*-
from odoo import http
from odoo.exceptions import MissingError
from odoo.http import request


class MemberDirectoryController(http.Controller):

    def _ensure_access(self):
        if not request.env.user._is_public():
            return None
        deny = request.env["ir.config_parameter"].sudo().get_param(
            "website_member_directory.deny_redirect", "login"
        )
        if deny == "forbidden":
            return request.render(
                "website_member_directory.members_forbidden",
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
            "website_member_directory.intro",
            "Meet the team",
        )

    @http.route(
        ["/membres", "/members"],
        type="http",
        auth="public",
        website=True,
        sitemap=False,
    )
    def members_list(self, search="", category="", **kwargs):
        denied = self._ensure_access()
        if denied:
            return denied

        category = (category or "").strip().lower()
        if category not in ("", "plongeur", "hsa"):
            category = ""

        members = request.env["res.users"].get_directory_members(
            search=search or None,
            category=category or None,
        )
        return request.render(
            "website_member_directory.members_list",
            {
                "members": members,
                "search": search or "",
                "category": category,
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
            "website_member_directory.member_profile",
            {
                "member": member,
                "partner": member.partner_id,
                "sections": sections,
                "specialties": member.get_dive_specialties(),
                "categories": member.get_dive_categories(),
                "page_name": "member_directory",
            },
        )
