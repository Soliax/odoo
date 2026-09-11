# CLAUDE.md — Odoo WDC / website customs

## Who edits what

- **Developer (you / coding agents):** Python, QWeb, SCSS, JS, migrations in `custom_addons/`.
- **Everyone else:** Website builder only (Edit → drag blocks, change snippet options, text, images).

## Non-negotiable

Custom website work must stay **page-builder accessible and configurable**:

- Public templates use `#wrap.oe_structure` so blocks can be dropped.
- Static URLs get a `website.page` when possible (`/membres`, Formation, …).
- Dynamic content (members grid, member profile, event attendees) = **snippets** with builder options, not hard-coded locked pages.
- Do not ship features that require a coder to change copy, layout sections, or toggle filters/visual modes.

Details: `AGENTS.md` and `.cursor/rules/website-page-builder.mdc`.
