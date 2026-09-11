# Agent notes — Odoo website customs

This repo has **one developer**; other people edit the public site in the **Odoo Website builder**. Treat that as a hard constraint.

## Page-builder first (required)

Every custom public feature must remain:

1. **Reachable from a real editable page** — `#wrap.oe_structure` (and a `website.page` when the URL is static, e.g. `/membres`).
2. **Fully configurable in Edit mode** — snippet options for behavior/layout; editors can add other blocks around ours.
3. **Not locked in controller-only QWeb** — dynamic data goes in snippets (`s_md_*`) with protected content + RPC, same pattern as Members / Member Profile / Event Participants.

Canonical examples:

- List: `website_member.members_list` + `s_md_members`
- Profile: `website_member.member_profile` + `s_md_member_profile`
- Static marketing: `website_wdc.formation`

Also see `.cursor/rules/website-page-builder.mdc` and `CLAUDE.md`.
