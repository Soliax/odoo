# -*- coding: utf-8 -*-
{
    "name": "Members",
    "version": "19.0.2.9.8",
    "category": "Website",
    "summary": "Member directory TCG cards + event participant website blocks",
    "description": """
Members website blocks
======================
* Members block: TCG-style cards with brevet gem, photo, specialties, HSA/dive icons
* Filters: name, brevet, specialty, category
* Event Participants block: horizontal rows (face, name, brevet)
* Club Plongee fields on contacts/users
* /membres page still available
""",
    "author": "Independent Developer",
    "license": "LGPL-3",
    "depends": ["website", "portal", "html_builder", "website_event"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/profile_fields.xml",
        "data/specialty_fields.xml",
        "data/brevet_fields.xml",
        "views/member_field_views.xml",
        "views/res_users_views.xml",
        "views/res_config_settings_views.xml",
        "views/templates.xml",
        "views/snippets/s_md_members.xml",
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
