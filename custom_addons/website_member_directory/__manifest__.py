# -*- coding: utf-8 -*-
{
    "name": "Website Member Directory",
    "version": "19.0.1.0.0",
    "category": "Website",
    "summary": "Private member directory with configurable profile fields",
    "description": """
Logged-in member directory (/membres)
=====================================
* Card grid with photo + name (internal users only)
* Generic profile page filled from backend data
* Admin-configurable visible fields, order and sections
* Access restricted to authenticated users
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
    "installable": True,
    "application": True,
}
