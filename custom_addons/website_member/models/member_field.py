# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
import re


def _ensure_x_prefix(name):
    tech = re.sub(r"[^a-z0-9_]", "_", (name or "").strip().lower()).strip("_")
    if not tech:
        return ""
    if not tech.startswith("x_"):
        tech = "x_%s" % tech
    while tech.startswith("x_x_"):
        tech = tech[2:]
    return tech


class MemberField(models.Model):
    _name = "member.field"
    _description = "Member Profile Field"
    _order = "section_sequence, sequence, id"

    name = fields.Char(string="Label", required=True, translate=True)
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)
    section_id = fields.Many2one(
        "member.section",
        string="Section",
        required=True,
        ondelete="restrict",
        index=True,
    )
    section_sequence = fields.Integer(
        related="section_id.sequence", store=True, readonly=True
    )
    source_model = fields.Selection(
        [
            ("res.partner", "Contact (res.partner)"),
            ("res.users", "User (res.users)"),
        ],
        default="res.partner",
        required=True,
    )
    field_name = fields.Char(string="Technical Field", required=True)
    is_custom = fields.Boolean(
        string="Created from UI",
        default=False,
        readonly=True,
        copy=False,
        help="Technical field was created from the Members configuration UI.",
    )
    show_on_backend = fields.Boolean(
        string="Show on Plongée tab",
        default=True,
        help="For custom fields: display on the contact Plongée tab.",
    )
    widget_id = fields.Many2one(
        "member.widget",
        string="Widget",
        required=True,
        ondelete="restrict",
        index=True,
    )
    widget_code = fields.Char(related="widget_id.code", store=True, readonly=True)
    visibility = fields.Selection(
        [
            ("connected", "All logged-in members"),
            ("group", "Specific groups only"),
        ],
        default="connected",
        required=True,
    )
    group_ids = fields.Many2many(
        "res.groups",
        "member_field_group_rel",
        "field_id",
        "group_id",
        string="Allowed Groups",
    )

    @api.constrains("field_name", "source_model")
    def _check_field_exists(self):
        for rec in self:
            model = self.env[rec.source_model]
            if rec.field_name not in model._fields:
                raise ValidationError(
                    self.env._(
                        "Field %(field)s does not exist on model %(model)s.",
                        field=rec.field_name,
                        model=rec.source_model,
                    )
                )

    def is_visible_for(self, user):
        self.ensure_one()
        if not self.active:
            return False
        if self.visibility == "connected":
            return bool(user and not user._is_public())
        return bool(user.all_group_ids & self.group_ids)

    def get_display_value(self, member_user):
        self.ensure_one()
        record = member_user.partner_id if self.source_model == "res.partner" else member_user
        field = record._fields.get(self.field_name)
        if not field:
            return False

        raw = record[self.field_name]
        widget = self.widget_id
        render = widget.render_type if widget else "text"

        if render == "address":
            partner = member_user.partner_id
            lines = (
                partner.contact_address
                or partner._display_address(without_company=True)
                or ""
            ).strip()
            return {"type": "address", "value": lines} if lines else False

        if render == "brevet" or self.field_name == "dive_brevet":
            if not raw:
                return False
            partner = member_user.partner_id
            return {
                "type": "brevet",
                "value": partner.dive_brevet_label or raw,
                "short": partner.dive_brevet_short or raw,
                "css": partner.dive_brevet_css or "brevet-none",
            }

        # Select = one value; MultiSelect = several option tags
        if render in ("select", "multiselect") or (
            field.type == "selection" and widget and widget.uses_value_list
            and render != "brevet"
        ):
            if render == "multiselect":
                items = []
                if field.type == "many2many":
                    opts = raw if raw else self.env["member.widget.option"]
                    for opt in opts.sorted("sequence"):
                        items.append({
                            "value": opt.name,
                            "short": opt.short_name or opt.name,
                            "css": opt.css_class or "",
                        })
                else:
                    if raw in (False, None, ""):
                        return False
                    keys = [k.strip() for k in str(raw).split(",") if k.strip()]
                    for key in keys:
                        opt = widget.get_option(key) if widget else False
                        items.append({
                            "value": (opt.name if opt else key),
                            "short": (opt.short_name or opt.name if opt else key),
                            "css": (opt.css_class or "") if opt else "",
                        })
                return {"type": "select_multi", "items": items} if items else False
            if raw in (False, None, ""):
                return False
            opt = widget.get_option(raw) if widget else False
            return {
                "type": "select",
                "value": (opt.name if opt else raw),
                "short": (opt.short_name or opt.name if opt else raw),
                "css": (opt.css_class or "") if opt else "",
            }

        if field.type in ("many2one",) or render == "many2one":
            if not raw:
                return False
            return {"type": "many2one", "value": raw.display_name, "id": raw.id}

        if field.type in ("boolean",) or render == "boolean":
            return {
                "type": "boolean",
                "value": self.env._("Oui") if raw else self.env._("Non"),
                "checked": bool(raw),
            }

        if field.type in ("html",) or render == "html":
            if not raw:
                return False
            return {"type": "html", "value": raw}

        if field.type == "date" or render == "date":
            if not raw:
                return False
            return {"type": "date", "value": raw.strftime("%d-%m-%Y")}

        if raw in (False, None, ""):
            return False

        value = raw
        if field.type == "selection":
            value = dict(field._description_selection(self.env)).get(raw, raw)

        if render == "email":
            return {"type": "email", "value": value}
        if render == "phone":
            return {"type": "phone", "value": value}
        if render == "url":
            return {"type": "url", "value": value}
        return {"type": "text", "value": value}

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._sync_backend_custom_view()
        return records

    def write(self, vals):
        vals = dict(vals)
        if "is_custom" in vals:
            # Never flip this flag from the UI / imports accidentally.
            vals.pop("is_custom", None)
        if "field_name" in vals:
            raw = vals.get("field_name") or ""
            # Seed XML re-writes the same field_name on every upgrade — only
            # react when the technical name actually changes.
            customs = self.filtered("is_custom")
            builtins = self - customs
            if customs and builtins:
                raise UserError(
                    self.env._(
                        "Cannot change the technical name on custom and built-in "
                        "fields in the same write."
                    )
                )
            if builtins and any(rec.field_name != raw for rec in builtins):
                raise UserError(
                    self.env._("Only UI-created technical fields can be renamed.")
                )
            if customs:
                new_name = _ensure_x_prefix(raw)
                if not new_name or not re.fullmatch(r"x_[a-z][a-z0-9_]*", new_name):
                    raise ValidationError(self.env._(
                        "Technical name must look like x_dive_brevet_pa."
                    ))
                vals["field_name"] = new_name
                for rec in customs:
                    if rec.field_name != new_name:
                        rec._rename_manual_partner_field(new_name)
        res = super().write(vals)
        sync_keys = (
            "active", "show_on_backend", "field_name", "section_id",
            "sequence", "name", "source_model", "is_custom", "widget_id",
        )
        if any(k in vals for k in sync_keys):
            self._sync_backend_custom_view()
        if any(k in vals for k in ("name", "widget_id", "field_name")):
            self.filtered("is_custom")._sync_ir_model_field()
        return res

    def _rename_manual_partner_field(self, new_name):
        """Rename the underlying manual ir.model.fields (+ DB column)."""
        self.ensure_one()
        old_name = self.field_name
        if old_name == new_name:
            return
        if new_name in self.env["res.partner"]._fields:
            raise UserError(
                self.env._("Field %s already exists on contacts.") % new_name
            )
        ir_field = self.env["ir.model.fields"].sudo().search([
            ("model", "=", "res.partner"),
            ("name", "=", old_name),
            ("state", "=", "manual"),
        ], limit=1)
        if not ir_field:
            raise UserError(
                self.env._("Manual field %s was not found; cannot rename.") % old_name
            )
        ir_field.write({"name": new_name})

    def unlink(self):
        builtins = self.filtered(lambda f: not f.is_custom)
        if builtins:
            raise UserError(
                self.env._(
                    "Cannot delete built-in profile fields (%s). "
                    "Only UI-created technical fields can be removed."
                ) % ", ".join(builtins.mapped("name"))
            )
        customs = self.filtered(
            lambda f: f.is_custom and f.source_model == "res.partner" and f.field_name
        )
        manual_names = customs.mapped("field_name")
        # Remove from Club Plongee view before dropping ir.model.fields
        # (Odoo refuses to delete a field still referenced in a view).
        if manual_names:
            super(MemberField, customs).write({
                "show_on_backend": False,
                "active": False,
            })
            self.env["member.field"]._sync_backend_custom_view()
        res = super().unlink()
        if manual_names:
            self.env["ir.model.fields"].sudo().search([
                ("model", "=", "res.partner"),
                ("name", "in", manual_names),
                ("state", "=", "manual"),
            ]).unlink()
            self.env["member.field"]._sync_backend_custom_view()
        return res
    def _sync_ir_model_field(self):
        """Keep manual ir.model.fields label / selection in sync for UI fields."""
        Field = self.env["ir.model.fields"].sudo()
        for rec in self:
            if not rec.is_custom or rec.source_model != "res.partner":
                continue
            ir_field = Field.search([
                ("model", "=", "res.partner"),
                ("name", "=", rec.field_name),
                ("state", "=", "manual"),
            ], limit=1)
            if not ir_field:
                continue
            vals = {"field_description": rec.name}
            widget = rec.widget_id
            if widget and widget.render_type == "select":
                pairs = widget.selection_pairs()
                if pairs and ir_field.ttype == "selection":
                    vals["selection"] = str(pairs)
            ir_field.write(vals)

    def action_open_widget(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": self.widget_id.display_name,
            "res_model": "member.widget",
            "res_id": self.widget_id.id,
            "view_mode": "form",
            "target": "current",
        }

    def action_open_create_wizard(self):
        """Open the new-field wizard (also callable from code / other buttons)."""
        return self.env["ir.actions.act_window"]._for_xml_id(
            "website_member.action_member_field_create_wizard"
        )

    # Club Plongee static groups (see res_users_views.xml) keyed by member.section.code.
    # For multi-column sections (brevets/specialties/federations), target the last
    # inner column — a direct <field> inside the outer group is ignored by the form layout.
    _BACKEND_SECTION_ANCHORS = {
        "identity": "//page[@name='dive_club']//group[@name='dive_section_identity']",
        "club": "//page[@name='dive_club']//group[@name='dive_section_club']",
        "contact": "//page[@name='dive_club']//group[@name='dive_section_contact']",
        "lifras": "//page[@name='dive_club']//group[@name='dive_section_lifras']",
        "medical": "//page[@name='dive_club']//group[@name='dive_section_medical']",
        "brevets": "//page[@name='dive_club']//group[@name='dive_section_brevets']/group[last()]",
        "specialties": "//page[@name='dive_club']//group[@name='dive_section_specialties']/group[last()]",
        "federations": "//page[@name='dive_club']//group[@name='dive_section_federations']/group[last()]",
        "professional": "//page[@name='dive_club']//group[@name='dive_section_identity']",
        "address": "//page[@name='dive_club']//group[@name='dive_section_identity']",
    }

    # Built-in partner fields whose Club Plongee placement follows member.field.section_id
    _BACKEND_PLACED_FIELDS = (
        "dive_is_plongeur",
        "dive_is_hsa",
    )

    @api.model
    def _sync_backend_custom_view(self):
        """Inject UI-created fields into existing Club Plongee sections (no duplicate headers)."""
        View = self.env["ir.ui.view"].sudo()
        xmlid = "website_member.view_partner_form_dive_custom_fields"
        view = self.env.ref(xmlid, raise_if_not_found=False)
        parent = self.env.ref(
            "website_member.view_partner_form_dive", raise_if_not_found=False
        )
        # Fall back to page-level inject until section anchors exist on the Club form.
        parent_arch = (parent.arch_db or "") if parent else ""
        anchors_ready = "dive_section_brevets" in parent_arch

        fields_rec = self.sudo().search([
            ("active", "=", True),
            ("show_on_backend", "=", True),
            ("source_model", "=", "res.partner"),
            "|",
            ("is_custom", "=", True),
            ("field_name", "in", list(self._BACKEND_PLACED_FIELDS)),
        ], order="section_sequence, sequence, id")

        chunks = ["<data>"]
        if not fields_rec:
            chunks.append(
                '<xpath expr="//page[@name=\'dive_club\']" position="inside">'
                '<group name="dive_custom_fields" invisible="1"/></xpath>'
            )
        else:
            by_section = []
            current = None
            bucket = []
            for conf in fields_rec:
                if conf.field_name not in self.env["res.partner"]._fields:
                    continue
                sec = conf.section_id
                if sec != current:
                    if bucket:
                        by_section.append((current, bucket))
                    current = sec
                    bucket = [conf]
                else:
                    bucket.append(conf)
            if bucket:
                by_section.append((current, bucket))

            orphan_blocks = []
            for sec, confs in by_section:
                code = (sec.code if sec else "") or ""
                anchor = (
                    self._BACKEND_SECTION_ANCHORS.get(code) if anchors_ready else None
                )
                field_xml = []
                for conf in confs:
                    fname = conf.field_name
                    flabel = (conf.name or fname).replace('"', "&quot;")
                    attrs = f'name="{fname}" string="{flabel}"'
                    partner_field = self.env["res.partner"]._fields.get(fname)
                    if (
                        conf.widget_id
                        and conf.widget_id.render_type == "multiselect"
                        and partner_field
                        and partner_field.type == "many2many"
                    ):
                        wid = conf.widget_id.id
                        attrs += (
                            f' widget="many2many_tags"'
                            f' domain="[(\'widget_id\', \'=\', {wid}),'
                            f' (\'active\', \'=\', True)]"'
                        )
                    field_xml.append(f"<field {attrs}/>")
                body = "\n".join(field_xml)
                if anchor:
                    # Do NOT wrap in an extra <group>: nesting a group inside a
                    # labeled section (LIFRAS, …) breaks Odoo's label/value grid
                    # for the existing fields in that section.
                    chunks.append(
                        f'<xpath expr="{anchor}" position="inside">'
                        f"{body}"
                        f"</xpath>"
                    )
                else:
                    label = ((sec.name if sec else None) or code or "Extra").replace(
                        '"', "&quot;"
                    )
                    orphan_blocks.append(
                        f'<group name="dive_custom_{code or "extra"}" string="{label}">'
                        f"{body}</group>"
                    )

            if orphan_blocks:
                chunks.append(
                    '<xpath expr="//page[@name=\'dive_club\']" position="inside">'
                    '<group name="dive_custom_fields">'
                    + "".join(orphan_blocks)
                    + "</group></xpath>"
                )

        chunks.append("</data>")
        arch = "\n".join(chunks)
        inherit = parent or self.env.ref("base.view_partner_form")

        if view:
            view.write({
                "arch": arch,
                "inherit_id": inherit.id,
            })
        else:
            view = View.create({
                "name": "res.partner.form.dive.custom.fields",
                "type": "form",
                "model": "res.partner",
                "inherit_id": inherit.id,
                "mode": "extension",
                "arch": arch,
            })
            Imd = self.env["ir.model.data"].sudo()
            if not Imd.search([
                ("module", "=", "website_member"),
                ("name", "=", "view_partner_form_dive_custom_fields"),
            ], limit=1):
                Imd.create({
                    "module": "website_member",
                    "name": "view_partner_form_dive_custom_fields",
                    "model": "ir.ui.view",
                    "res_id": view.id,
                    "noupdate": True,
                })
        return view
