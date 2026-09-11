/** @odoo-module **/

import { Interaction } from "@web/public/interaction";
import { registry } from "@web/core/registry";
import { rpc } from "@web/core/network/rpc";

export class MdMembersSnippet extends Interaction {
    static selector = ".s_md_members";
    dynamicContent = {
        "[data-md-filters]": {
            "t-on-change": this.onFilterChange,
            "t-on-submit.prevent": this.onFilterChange,
        },
        "[data-md-filters] input[name='search']": {
            "t-on-keydown": this.onSearchKeydown,
        },
        ".s_md_card[data-href]": {
            "t-on-click": this.onCardActivate,
            "t-on-keydown": this.onCardKeydown,
        },
    };

    setup() {
        this.rpc = rpc;
        this._searchTimer = null;
    }

    get isEditor() {
        return Boolean(this.el.closest(".o_editable, .o_wysiwyg_loader, #wrapwrap.o_editable"));
    }

    async willStart() {
        await this.loadMembers();
    }

    getOptions(extra = {}) {
        const ds = this.el.dataset;
        const form = this.el.querySelector("[data-md-filters]");
        const fromForm = {};
        if (form) {
            const fd = new FormData(form);
            for (const [k, v] of fd.entries()) {
                fromForm[k] = v;
            }
        }
        return {
            show_filters: ds.showFilters ?? "1",
            show_specialties: ds.showSpecialties ?? "1",
            columns: ds.columns || "4",
            limit: ds.limit || "0",
            category: !ds.category || ds.category === "all" ? "" : ds.category,
            ...fromForm,
            ...extra,
        };
    }

    async loadMembers(extra = {}) {
        const content = this.el.querySelector(".s_md_members_content");
        if (!content) {
            return;
        }
        try {
            const result = await this.rpc("/membres/snippet/members", this.getOptions(extra));
            if (result.error === "login_required") {
                content.innerHTML =
                    '<div class="alert alert-warning mb-0">Connectez-vous pour voir les membres.</div>';
                return;
            }
            content.innerHTML = result.html || "";
            // Keep the editor selectable on the section, not on individual cards
            content.classList.add("o_not_editable");
            content.setAttribute("data-oe-protected", "true");
            content.setAttribute("contenteditable", "false");
        } catch (_e) {
            content.innerHTML =
                '<div class="alert alert-danger mb-0">Impossible de charger les membres.</div>';
        }
    }

    onFilterChange() {
        this.loadMembers();
    }

    onSearchKeydown(ev) {
        if (ev.key === "Enter") {
            ev.preventDefault();
            this.loadMembers();
            return;
        }
        clearTimeout(this._searchTimer);
        this._searchTimer = setTimeout(() => this.loadMembers(), 350);
    }

    onCardActivate(ev) {
        if (this.isEditor) {
            return;
        }
        const card = ev.currentTarget;
        const href = card?.dataset?.href;
        if (href) {
            window.location.href = href;
        }
    }

    onCardKeydown(ev) {
        if (ev.key === "Enter" || ev.key === " ") {
            ev.preventDefault();
            this.onCardActivate(ev);
        }
    }
}

registry
    .category("public.interactions")
    .add("website_member.s_md_members", MdMembersSnippet);
