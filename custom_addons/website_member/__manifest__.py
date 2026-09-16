# -*- coding: utf-8 -*-
{
    "name": "Members",
    "version": "19.0.3.15.7",
    "category": "Website",
    "summary": "Easy club member visualization, search, profiles & event participants",
    "description": """
WDC Members
===========
Browse, search and present club members on the website.

* Member visualization (photo, brevet, specialties)
* Search, multiselect filters and sort by name / brevet
* Public member profiles
* Event participants website block
* Website builder snippets with configurable options
* Club Plongée / Profile Fields & Profile Widgets
* CB JSON member import wizard

Copyright (C) 2026 Anton Lallemand / Waterloo Diving Club
License: LGPL-3
""",
    "author": "Anton Lallemand / Waterloo Diving Club",
    "license": "LGPL-3",
    "icon": "/website_member/static/description/icon.png",
    "depends": ["website", "portal", "html_builder", "website_event"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/member_sections.xml",
        "data/member_widgets.xml",
        "views/res_users_views.xml",
        "data/profile_fields.xml",
        "data/specialty_fields.xml",
        "data/brevet_fields.xml",
        "data/federation_fields.xml",
        "views/member_field_views.xml",
        "views/res_config_settings_views.xml",
        "views/member_import_views.xml",
        "views/templates.xml",
        "views/event_templates.xml",
        "views/snippets/s_md_members.xml",
        "views/snippets/s_md_member_profile.xml",
        "views/snippets/s_md_event_attendees.xml",
        "views/snippets/snippets.xml",
        "views/website_menus.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "website_member/static/src/scss/member.scss",
            "website_member/static/src/snippets/**/*.js",
        ],
        "website.website_builder_assets": [
            "website_member/static/src/website_builder/**/*",
        ],
    },
    "post_init_hook": "post_init_hook",
    "installable": True,
    "application": True,
}
