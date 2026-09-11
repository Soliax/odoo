/** @odoo-module **/

import { Interaction } from "@web/public/interaction";
import { registry } from "@web/core/registry";
import { rpc } from "@web/core/network/rpc";

const FLAG_ON = (value) => value === "1" || value === "true";

const OPTION_ATTRS = [
    "data-show-fields",
    "data-show-events",
    "data-user-id",
];

export class MdMemberProfileSnippet extends Interaction {
    static selector = ".s_md_member_profile";

    setup() {
        this.rpc = rpc;
        this._optTimer = null;
        this._optionObserver = null;
        this._loading = false;
        this._pendingReload = false;
    }

    async willStart() {
        this.ensureOptionScheme();
        await this.loadProfile();
    }

    start() {
        this._optionObserver = new MutationObserver(() => {
            clearTimeout(this._optTimer);
            this._optTimer = setTimeout(() => this.loadProfile(), 40);
        });
        this._optionObserver.observe(this.el, {
            attributes: true,
            attributeFilter: OPTION_ATTRS,
        });
    }

    destroy() {
        this._optionObserver?.disconnect();
        clearTimeout(this._optTimer);
    }

    ensureOptionScheme() {
        const ds = this.el.dataset;
        if ("mdOptions" in ds) {
            return;
        }
        if (!("showFields" in ds)) {
            ds.showFields = "1";
        }
        if (!("showEvents" in ds)) {
            ds.showEvents = "1";
        }
        ds.mdOptions = "1";
    }

    resolveUserId() {
        const raw = this.el.dataset.userId;
        if (raw) {
            const n = parseInt(raw, 10);
            if (n > 0) {
                return n;
            }
        }
        const match = window.location.pathname.match(
            /\/(?:membres|members)\/(\d+)(?:\/|$|\?)/
        );
        return match ? parseInt(match[1], 10) : 0;
    }

    getOptions() {
        this.ensureOptionScheme();
        const ds = this.el.dataset;
        return {
            user_id: this.resolveUserId(),
            show_fields: FLAG_ON(ds.showFields) ? "1" : "0",
            show_events: FLAG_ON(ds.showEvents) ? "1" : "0",
        };
    }

    async loadProfile() {
        const content = this.el.querySelector(".s_md_member_profile_content");
        if (!content) {
            return;
        }
        const userId = this.resolveUserId();
        if (!userId) {
            content.innerHTML =
                '<div class="alert alert-light border mb-0 text-center">Ouvrez un profil membre (/membres/ID) ou choisissez un membre dans les options du bloc.</div>';
            return;
        }
        if (this._loading) {
            this._pendingReload = true;
            return;
        }
        this._loading = true;
        try {
            const result = await this.rpc("/membres/snippet/profile", this.getOptions());
            if (result.error === "login_required") {
                content.innerHTML =
                    '<div class="alert alert-warning mb-0">Connectez-vous pour voir ce profil.</div>';
                return;
            }
            if (result.error === "not_found") {
                content.innerHTML =
                    '<div class="alert alert-warning mb-0">Ce profil membre n’est pas disponible.</div>';
                return;
            }
            content.innerHTML = result.html || "";
            content.classList.add("o_not_editable");
            content.setAttribute("data-oe-protected", "true");
            content.setAttribute("contenteditable", "false");
        } catch (_e) {
            content.innerHTML =
                '<div class="alert alert-danger mb-0">Impossible de charger le profil.</div>';
        } finally {
            this._loading = false;
            if (this._pendingReload) {
                this._pendingReload = false;
                this.loadProfile();
            }
        }
    }
}

registry
    .category("public.interactions")
    .add("website_member.s_md_member_profile", MdMemberProfileSnippet);
