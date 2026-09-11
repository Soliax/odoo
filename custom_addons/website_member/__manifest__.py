# -*- coding: utf-8 -*-
{
    "name": "Members",
    "version": "19.0.3.12.0",
    "category": "Website",
    "summary": "Club members TCG cards + event participant website blocks",
    "description": """
Members website blocks
======================
* Members block: TCG-style cards with brevet gem, photo, specialties, HSA/dive icons
* Multiselect filters + sort by name/brevet
* Event Participants: compact TCG rows (portrait, brevet heptagon, ticket bubble)
* Event page Style toggle for Participants
* Club Plongee fields on contacts/users
* CB JSON member import wizard
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
        "data/federation_fields.xml",
        "views/member_field_views.xml",
        "views/res_users_views.xml",
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
