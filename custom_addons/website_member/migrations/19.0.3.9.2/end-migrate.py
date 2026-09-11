# -*- coding: utf-8 -*-
"""Keep filters host as a real HTML element (Odoo collapses empty <div></div> to <div/>)."""

import re

from odoo import SUPERUSER_ID, api

_HOST_RE = re.compile(
    r'<div([^>]*\bs_md_members_filters_host\b[^>]*)\s*(?:/>|></div>)',
    re.I,
)
_HOST_FIXED = (
    r'<div\1><span class="d-none">filters</span></div>'
)


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    View = env["ir.ui.view"].sudo()
    for view in View.search([("arch_db", "ilike", "s_md_members_filters_host")]):
        arch = view.arch_db or ""
        new_arch, n = _HOST_RE.subn(_HOST_FIXED, arch, count=1)
        if n and new_arch != arch:
            view.write({"arch_db": new_arch})
