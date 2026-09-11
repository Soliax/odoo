# -*- coding: utf-8 -*-
import re

from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    """Strip obsolete Members snippet border/frame attrs from saved pages."""
    env = api.Environment(cr, SUPERUSER_ID, {})
    pattern = re.compile(
        r'\sdata-border-(?:card|oval|name|specs|stat|gem)="[^"]*"'
        r'|\sdata-frame-(?:fit|scale-x|scale-y|grow-x|grow-y)="[^"]*"'
        r'|\sdata-oval-scale="[^"]*"'
        r'|\sdata-card-special-corners="[^"]*"',
        re.I,
    )
    views = env["ir.ui.view"].sudo().search([
        "|", "|",
        ("arch_db", "ilike", "data-border-"),
        ("arch_db", "ilike", "data-frame-"),
        ("arch_db", "ilike", "s_md_members"),
    ])
    for view in views:
        arch = view.arch_db or ""
        cleaned = pattern.sub("", arch)
        if cleaned != arch:
            view.write({"arch_db": cleaned})
