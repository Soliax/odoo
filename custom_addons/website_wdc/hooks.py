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
    company = env.company.sudo()
    company.write({
        "name": company.name if company.name and company.name != "My Company" else "Waterloo Diving Club",
        "street": company.street or "33 Rue Théophile Delbar",
        "city": company.city or "Waterloo",
        "zip": company.zip or "1410",
        "country_id": env.ref("base.be", raise_if_not_found=False).id or company.country_id.id,
        "email": company.email or "contact@wdc.be",
        "website": company.website or "/",
    })


def _ensure_branding(env):
    """Site logo = logo-2.png (favicon derived from the same asset)."""
    with file_open("website_wdc/static/src/img/logo/logo-2.png", "rb") as f:
        logo_b64 = base64.b64encode(f.read())
    company = env.company.sudo()
    company.write({"logo": logo_b64, "name": "Waterloo Diving Club"})
    for website in env["website"].sudo().search([]):
        website.write({
            "name": "Waterloo Diving Club",
            "logo": logo_b64,
            "favicon": logo_b64,
        })


def post_init_hook(env):
    _setup_company(env)
    _ensure_branding(env)
    _clear_cow_views(env)
    _ensure_homepage_shell(env)
    _ensure_menus(env)
