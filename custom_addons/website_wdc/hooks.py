# -*- coding: utf-8 -*-
import base64

from odoo.tools.misc import file_open


def _clear_cow_views(env):
    """Drop website-specific copies so module templates apply cleanly."""
    View = env["ir.ui.view"].sudo()
    keys = (
        "website.homepage",
        "website.contactus",
        "website_wdc.homepage",
        "website_wdc.contactus",
        "website_wdc.formation",
        "website_wdc.contact_block",
    )
    View.search([("key", "in", keys), ("website_id", "!=", False)]).unlink()


def _ensure_homepage_shell(env):
    View = env["ir.ui.view"].sudo()
    base_home = View.search([
        ("key", "=", "website.homepage"),
        ("website_id", "=", False),
    ], limit=1)
    if not base_home:
        return
    # Keep a clean shell; website_wdc.homepage inherit fills content
    if "oe_structure" not in (base_home.arch_db or ""):
        base_home.write({
            "arch_db": """
                <t name="Home" t-name="website.homepage">
                    <t t-call="website.layout" pageName.f="homepage">
                        <div id="wrap" class="oe_structure oe_empty"/>
                    </t>
                </t>
            """,
        })
    Page = env["website.page"].sudo()
    for website in env["website"].sudo().search([]):
        home = Page.search([
            ("website_id", "=", website.id),
            ("url", "=", "/"),
        ], limit=1) or Page.search([("url", "=", "/")], limit=1)
        if home:
            home.write({"view_id": base_home.id, "is_published": True})


def _ensure_menus(env):
    Menu = env["website.menu"].sudo()
    for website in env["website"].sudo().search([]):
        website.write({"name": "Waterloo Diving Club"})
        main = website.menu_id
        if not main:
            continue
        wanted = [
            ("/", "Accueil", 10),
            ("/event", "Événements", 20),
            ("/membres", "Membres", 30),
            ("/formation", "Formation", 35),
            ("/contactus", "Contact", 40),
        ]
        existing = {
            (m.url or "").split("?")[0]: m
            for m in Menu.search([
                ("website_id", "=", website.id),
                ("parent_id", "=", main.id),
            ])
        }
        for url, name, seq in wanted:
            menu = existing.pop(url, None)
            if url == "/event":
                # Keep any /event* menu as Événements
                event_menus = [m for u, m in list(existing.items()) if u.startswith("/event")]
                if event_menus and not menu:
                    menu = event_menus[0]
                    existing.pop(menu.url.split("?")[0], None)
            if menu:
                menu.write({"name": name, "sequence": seq, "url": url})
            else:
                Menu.create({
                    "name": name,
                    "url": url,
                    "parent_id": main.id,
                    "website_id": website.id,
                    "sequence": seq,
                })


def _setup_company(env):
    # Prefer the dedicated WDC company when website_member is installed.
    company = env.ref("website_member.company_wdc", raise_if_not_found=False)
    if not company and hasattr(env["res.company"], "_ensure_wdc_company"):
        company = env["res.company"]._ensure_wdc_company()
    if not company:
        company = env["res.company"].sudo().search(
            [("name", "=", "Waterloo Diving Club")], limit=1
        ) or env.company.sudo()
    be = env.ref("base.be", raise_if_not_found=False)
    eur = env.ref("base.EUR", raise_if_not_found=False)
    state = env["res.country.state"].sudo().search([
        ("country_id", "=", be.id if be else False),
        ("code", "=", "WBR"),
    ], limit=1)
    vals = {
        "name": "Waterloo Diving Club",
        "street": "Rue Théophile Delbar, 33",
        "street2": "Boite 1",
        "city": "Waterloo",
        "zip": "1410",
        "country_id": be.id if be else company.country_id.id,
        "state_id": state.id if state else company.state_id.id,
        "vat": company.vat or "BE0477472701",
        "email": company.email or "wdc@waterloodivingclub.be",
        "website": company.website or "https://www.waterloodivingclub.be/",
        "currency_id": eur.id if eur else company.currency_id.id,
        "color": company.color or 5,
    }
    company.write({k: v for k, v in vals.items() if v})


def _ensure_branding(env):
    """Site logo = logo-2.png (favicon derived from the same asset)."""
    with file_open("website_wdc/static/src/img/logo/logo-2.png", "rb") as f:
        logo_b64 = base64.b64encode(f.read())
    company = env.ref("website_member.company_wdc", raise_if_not_found=False)
    if not company:
        company = env["res.company"].sudo().search(
            [("name", "=", "Waterloo Diving Club")], limit=1
        ) or env.company.sudo()
    company.write({"logo": logo_b64, "name": "Waterloo Diving Club"})
    for website in env["website"].sudo().search([]):
        website.write({
            "name": "Waterloo Diving Club",
            "company_id": company.id,
            "logo": logo_b64,
            "favicon": logo_b64,
        })


def post_init_hook(env):
    _setup_company(env)
    _ensure_branding(env)
    _clear_cow_views(env)
    _ensure_homepage_shell(env)
    _ensure_menus(env)
