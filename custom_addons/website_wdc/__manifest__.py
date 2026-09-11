# -*- coding: utf-8 -*-
{
    "name": "WDC Website",
    "version": "19.0.2.1.0",
    "category": "Website",
    "summary": "Lean Waterloo Diving Club public pages (editable website mockups)",
    "description": """
WDC public website
==================
Editable QWeb mockups using standard website snippets:

* Homepage — cover, welcome, Plongée / HSA, practical info
* Formation — one public summary page (brevets + spécialités)
* Contact — default Odoo contact form (French copy)
* Menus — Accueil, Événements, Membres, Formation, Contact

Members / participants stay in website_member. No custom frontend CSS/JS.
""",
    "author": "Independent Developer",
    "license": "LGPL-3",
    "depends": ["website", "website_crm"],
    "data": [
        "views/homepage.xml",
        "views/contactus.xml",
        "views/formation.xml",
        "views/menus.xml",
    ],
    "post_init_hook": "post_init_hook",
    "installable": True,
    "application": False,
}
