/** @odoo-module **/

import { Interaction } from "@web/public/interaction";
import { registry } from "@web/core/registry";
import { rpc } from "@web/core/network/rpc";

export class MdEventAttendeesSnippet extends Interaction {
    static selector = ".s_md_event_attendees";

    setup() {
        this.rpc = rpc;
    }

    async willStart() {
        await this.loadAttendees();
    }

    resolveEventId() {
        const fromData = parseInt(this.el.dataset.eventId || "0", 10) || 0;
        if (fromData) {
            return fromData;
        }
        // On an event page: /event/<id> or /event/<slug>-<id>
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
            // Keep placeholder in editor when no event selected
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
                return;
            }
            content.innerHTML = result.html || "";
            if (countEl) {
                countEl.textContent = result.count ? `( ${result.count} )` : "";
            }
        } catch (_e) {
            content.innerHTML =
                '<div class="alert alert-danger mb-0">Impossible de charger les participants.</div>';
        }
    }
}

registry
    .category("public.interactions")
    .add("website_member.s_md_event_attendees", MdEventAttendeesSnippet);
