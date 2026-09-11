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
                {"page_name": "members"},
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

    def _parse_list(self, value):
        """Normalize multi-select values from GET/JSON into a clean list."""
        if value is None or value is False:
            return []
        if isinstance(value, (list, tuple, set)):
            items = list(value)
        else:
            items = str(value).replace(";", ",").split(",")
        out = []
        for item in items:
            # JSON-RPC may wrap a lone value oddly; flatten one level.
            if isinstance(item, (list, tuple)):
                for sub in item:
                    v = str(sub or "").strip().lower()
                    if v and v not in out and v != "all":
                        out.append(v)
                continue
            v = str(item or "").strip().lower()
            if v and v not in out and v != "all":
                out.append(v)
        return out

    def _parse_filters(self, kwargs):
        search = (kwargs.get("search") or "").strip()
        # Support both single legacy params and multi-select lists
        categories = self._parse_list(
            kwargs.get("category") if "category" in kwargs else kwargs.get("categories")
        )
        categories = [c for c in categories if c in ("plongeur", "hsa")]
        brevets = self._parse_list(
            kwargs.get("brevet") if "brevet" in kwargs else kwargs.get("brevets")
        )
        specialties = self._parse_list(
            kwargs.get("specialty") if "specialty" in kwargs else kwargs.get("specialties")
        )
        try:
            limit = int(kwargs.get("limit") or 0) or None
        except (TypeError, ValueError):
            limit = None
        sort = str(kwargs.get("sort") or "brevet_desc").strip().lower()
        if sort not in ("name_asc", "name_desc", "brevet_asc", "brevet_desc"):
            sort = "brevet_desc"
        return search, categories, brevets, specialties, limit, sort

    def _user_profile_url(self, partner):
        """Same detail page as the members directory (/membres/<user_id>)."""
        user = request.env["res.users"].sudo().search(
            [
                ("partner_id", "=", partner.id),
                ("share", "=", False),
                ("active", "=", True),
                ("members_published", "=", True),
            ],
            limit=1,
        )
        return "/membres/%s" % user.id if user else False

    def _user_image_url(self, partner):
        user = request.env["res.users"].sudo().search(
            [("partner_id", "=", partner.id), ("share", "=", False), ("active", "=", True)],
            limit=1,
        )
        if user and user.image_128:
            return "/web/image/res.users/%s/image_128" % user.id
        if partner.image_128:
            return "/web/image/res.partner/%s/image_128" % partner.id
        return False

    @http.route(
        ["/membres", "/members"],
        type="http",
        auth="public",
        website=True,
        sitemap=False,
    )
    def members_list(self, search="", **kwargs):
        denied = self._ensure_access()
        if denied:
            return denied

        return request.render(
            "website_member.members_list",
            {
                "page_name": "members",
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
        allowed = Users.get_members()
        if not member.exists() or member not in allowed:
            raise MissingError("This member profile is not available.")

        # Editable shell (#wrap.oe_structure); dynamic body loads via snippet RPC.
        return request.render(
            "website_member.member_profile",
            {
                "member": member,
                "page_name": "members",
            },
        )

    @http.route(
        ["/membres/snippet/profile", "/members/snippet/profile"],
        type="jsonrpc",
        auth="public",
        website=True,
    )
    def snippet_profile(self, **kwargs):
        if request.env.user._is_public():
            return {"html": "", "error": "login_required"}

        try:
            user_id = int(kwargs.get("user_id") or 0)
        except (TypeError, ValueError):
            user_id = 0

        def _flag(key, default="1"):
            return str(kwargs.get(key, default)) not in ("0", "false", "False", "")

        Users = request.env["res.users"].sudo()
        member = Users.browse(user_id)
        allowed = Users.get_members()
        if not user_id or not member.exists() or member not in allowed:
            return {"html": "", "error": "not_found"}

        html = request.env["ir.ui.view"]._render_template(
            "website_member.s_md_member_profile_content",
            {
                "member": member,
                "partner": member.partner_id,
                "sections": member.get_member_profile_fields(request.env.user),
                "specialties": member.get_dive_specialties(),
                "categories": member.get_dive_categories(),
                "member_events": member.get_member_events(),
                "show_fields": _flag("show_fields"),
                "show_events": _flag("show_events"),
            },
        )
        return {"html": html}

    @http.route(
        ["/membres/snippet/members", "/members/snippet/members"],
        type="jsonrpc",
        auth="public",
        website=True,
    )
    def snippet_members(self, **kwargs):
        if request.env.user._is_public():
            return {"html": "", "error": "login_required"}

        search, categories, brevets, specialties, limit, sort = self._parse_filters(kwargs)

        def _flag(key, default="1"):
            return str(kwargs.get(key, default)) not in ("0", "false", "False", "")

        show_brevets_filters = _flag("show_brevets_filters")
        show_specialties_filters = _flag("show_specialties_filters")
        show_categories_filters = _flag("show_categories_filters")
        tcg_visual = _flag("tcg_visual", default="0")
        columns = kwargs.get("columns") or "4"
        if columns not in ("2", "3", "4"):
            columns = "4"

        try:
            page_size = int(kwargs.get("limit") if kwargs.get("limit") not in (None, "") else 24)
        except (TypeError, ValueError):
            page_size = 24
        try:
            page = max(1, int(kwargs.get("page") or 1))
        except (TypeError, ValueError):
            page = 1

        all_members = request.env["res.users"].get_members(
            search=search or None,
            categories=categories or None,
            brevets=brevets or None,
            specialties=specialties or None,
            limit=None,
            sort=sort,
        )
        total = len(all_members)
        if page_size <= 0:
            page_size = total or 1
            page = 1
            page_count = 1
            members = all_members
        else:
            page_count = max(1, (total + page_size - 1) // page_size) if total else 1
            if page > page_count:
                page = page_count
            offset = (page - 1) * page_size
            members = all_members[offset: offset + page_size]

        values = {
            "members": members,
            "search": search,
            "categories": categories or [],
            "brevets": brevets or [],
            "specialties_filter": specialties or [],
            "show_brevets_filters": show_brevets_filters,
            "show_specialties_filters": show_specialties_filters,
            "show_categories_filters": show_categories_filters,
            "tcg_visual": tcg_visual,
            "columns": columns,
            "sort": sort,
            "page": page,
            "page_size": page_size,
            "page_count": page_count,
            "total": total,
            "brevet_choices": DIVE_BREVET_SELECTION + [
                ("nb", "NB"),
            ],
            "specialty_choices": [
                (code, short) for code, short, _full, _f in DIVE_SPECIALTIES
            ],
        }
        View = request.env["ir.ui.view"]
        html = str(View._render_template("website_member.s_md_members_content", values))
        results_html = str(
            View._render_template("website_member.s_md_members_results", values)
        )
        return {"html": html, "results_html": results_html}

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

        cards_data = request.env["res.users"].get_event_attendee_cards(
            event_id=event_id,
            limit=limit,
            published_only=published_only,
        )
        cards = []
        for row in cards_data:
            partner = row["partner"]
            cards.append({
                "partner": partner,
                "name": partner.get_dive_display_name(),
                "brevet_css": partner.dive_brevet_css or "brevet-nb",
                "brevet_short": partner.dive_brevet_short or "NB",
                "brevet_label": partner.dive_brevet_label or "",
                "profile_url": self._user_profile_url(partner),
                "image_url": self._user_image_url(partner),
                "ticket_count": row["ticket_count"],
            })
        html = request.env["ir.ui.view"]._render_template(
            "website_member.s_md_attendees_content",
            {
                "cards": cards,
                "event_id": event_id,
            },
        )
        # Count people (tickets), not unique contact cards.
        people_count = sum(int(card.get("ticket_count") or 1) for card in cards)
        return {"html": html, "count": people_count}
