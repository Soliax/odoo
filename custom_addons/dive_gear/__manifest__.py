# -*- coding: utf-8 -*-
{
    "name": "Dive Club Gear",
    "version": "19.0.1.0.0",
    "category": "Inventory",
    "summary": "Club dive equipment inventory + Belgian maintenance schedules",
    "description": """
Import and manage club dive gear (bottles, regulators, BCDs) in Inventory,
with Maintenance equipment and Belgian retest intervals:

* Bottles: visual every 30 months, hydrostatic every 5 years
* Regulators: annual service
* BCDs / other: annual service (club practice)
""",
    "author": "Independent Developer",
    "license": "LGPL-3",
    "depends": ["stock", "maintenance", "product"],
    "data": [
        "security/ir.model.access.csv",
        "data/equipment_categories.xml",
        "data/product_categories.xml",
        "views/maintenance_equipment_views.xml",
        "views/gear_import_views.xml",
    ],
    "installable": True,
    "application": True,
}
