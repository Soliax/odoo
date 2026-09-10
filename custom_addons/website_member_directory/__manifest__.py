# -*- coding: utf-8 -*-
{
    "name": "Members",
    "version": "19.0.1.2.0",
    "category": "Website",
    "summary": "Private diving club members page with LIFRAS brevets and specialties",
    "description": """
Members website page (/membres)
===============================
* Logged-in members grid with photo + name
* Diving club fields and Specialites (date = title earned)
* Specialty pills on cards and profiles
* Game-like metallic frames by brevet level
* Demo divers for each brevet (password: diverdemo)
""",
    "author": "Independent Developer",
    "license": "LGPL-3",
    "depends": ["website", "portal"],
    "data": [
        "security/member_directory_security.xml",
        "security/ir.model.access.csv",
        "data/member_directory_field_data.xml",
        "data/member_directory_specialty_fields.xml",
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
