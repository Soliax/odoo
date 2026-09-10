# -*- coding: utf-8 -*-
{
    "name": "Website Member Directory",
    "version": "19.0.1.1.0",
    "category": "Website",
    "summary": "Private diving club member directory with LIFRAS brevets",
    "description": """
Logged-in member directory (/membres)
=====================================
* Card grid with photo + name for internal users
* Diving club fields (LIFRAS brevet, medical, contacts...)
* Dynamic profile fields from backend
* Brevet-tier card visuals (1* to MN)
* Demo divers for each brevet level (password: diverdemo)
""",
    "author": "Independent Developer",
    "license": "LGPL-3",
    "depends": ["website", "portal"],
    "data": [
        "security/member_directory_security.xml",
        "security/ir.model.access.csv",
        "data/member_directory_field_data.xml",
        "views/member_directory_field_views.xml",
        "views/res_users_views.xml",
        "views/res_config_settings_views.xml",
        "views/member_directory_templates.xml",
        "views/website_menus.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "website_member_directory/static/src/scss/member_directory.scss",
        ],
    },
    "post_init_hook": "post_init_hook",
    "installable": True,
    "application": True,
}
