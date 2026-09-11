/** @odoo-module **/

import { Interaction } from "@web/public/interaction";
import { registry } from "@web/core/registry";
import { rpc } from "@web/core/network/rpc";

export class MdEventAttendeesSnippet extends Interaction {
    static selector = ".s_md_event_attendees";
    dynamicContent = {
        ".s_md_attendee": {
            "t-on-click": this.onAttendeeClick,
        },
    };

    setup() {
        this.rpc = rpc;
    }

    get isEditor() {
        return Boolean(
            this.el.closest(".o_editable, .o_wysiwyg_loader, #wrapwrap.o_editable, .o_builder_page")
        );
    }

    async willStart() {
        await this.loadAttendees();
    }

    resolveEventId() {
        const fromData = parseInt(this.el.dataset.eventId || "0", 10) || 0;
        if (fromData) {
            return fromData;
        }
        const path = window.location.pathname || "";
        const match = path.match(/\/event\/(?:[^/]*-)?(\d+)(?:\/|$)/);
        return match ? parseInt(match[1], 10) : 0;
    }

    async loadAttendees() {
        const content = this.el.querySelector(".s_md_attendees_content");
        const countEl = this.el.querySelector(".s_md_attendees_count");
        if (!content) {
            return;
        }
        const eventId = this.resolveEventId();
        if (!eventId && !this.el.dataset.eventId) {
            return;
        }
        try {
            const result = await this.rpc("/membres/snippet/attendees", {
                event_id: eventId,
                limit: this.el.dataset.limit || "0",
                published_only: this.el.dataset.publishedOnly ?? "1",
            });
            if (result.error === "login_required") {
                content.innerHTML =
                    '<div class="alert alert-warning mb-0">Connectez-vous pour voir les participants.</div>';
                if (countEl) {
                    countEl.textContent = "";
                }
                return;
            }
            content.innerHTML = result.html || "";
            content.classList.add("o_not_editable");
            content.setAttribute("data-oe-protected", "true");
            content.setAttribute("contenteditable", "false");
            if (countEl) {
                const n = result.count || 0;
                countEl.textContent = n ? `(${n})` : "(0)";
            }
        } catch (_e) {
            content.innerHTML =
                '<div class="alert alert-danger mb-0">Impossible de charger les participants.</div>';
        }
    }

    onAttendeeClick(ev) {
        if (this.isEditor) {
            ev.preventDefault();
            ev.stopPropagation();
        }
    }
}

registry
    .category("public.interactions")
    .add("website_member.s_md_event_attendees", MdEventAttendeesSnippet);
