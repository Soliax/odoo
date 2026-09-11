/** @odoo-module **/

import { BuilderAction } from "@html_builder/core/builder_action";
import { BaseOptionComponent } from "@html_builder/core/utils";
import { Plugin } from "@html_editor/plugin";
import { withSequence } from "@html_editor/utils/resource";
import { before, SNIPPET_SPECIFIC_END } from "@html_builder/utils/option_sequence";
import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";

const MEMBERS_PLACEHOLDER = `<div class="s_md_snippet_placeholder text-center text-muted py-5">Les cartes membres se chargent ici…</div>`;
const PROFILE_PLACEHOLDER = `<div class="s_md_snippet_placeholder text-center text-muted py-5">Le profil membre se charge ici…</div>`;
const ATTENDEES_PLACEHOLDER = `<div class="s_md_snippet_placeholder text-center text-muted py-4 mb-0">Les participants se chargent ici…</div>`;

export class MdMembersOption extends BaseOptionComponent {
    static template = "website_member.MdMembersOption";
    static selector = ".s_md_members";
    static title = _t("Members");
}

export class MdMemberProfileOption extends BaseOptionComponent {
    static template = "website_member.MdMemberProfileOption";
    static selector = ".s_md_member_profile";
    static title = _t("Member Profile");
}

export class MdAttendeesOption extends BaseOptionComponent {
    static template = "website_member.MdAttendeesOption";
    static selector = ".s_md_event_attendees";
    static title = _t("Event Participants");
}

export class ReloadMdSnippetAction extends BuilderAction {
    static id = "reloadMdSnippet";
    static dependencies = ["edit_interaction"];
    setup() {
        this.preview = false;
    }
    apply({ editingElement }) {
        this.dependencies.edit_interaction.restartInteractions(editingElement);
    }
}

class MdSnippetOptionPlugin extends Plugin {
    static id = "mdSnippetOption";
    static dependencies = ["edit_interaction"];
    resources = {
        builder_options: [
            withSequence(before(SNIPPET_SPECIFIC_END), MdMembersOption),
            withSequence(before(SNIPPET_SPECIFIC_END), MdMemberProfileOption),
            withSequence(before(SNIPPET_SPECIFIC_END), MdAttendeesOption),
        ],
        so_content_addition_selector: [
            ".s_md_members",
            ".s_md_member_profile",
            ".s_md_event_attendees",
        ],
        builder_actions: {
            ReloadMdSnippetAction,
        },
        clean_for_save_handlers: this.cleanForSave.bind(this),
        normalize_handlers: this.normalize.bind(this),
    };

    normalize(root) {
        for (const el of root.querySelectorAll(
            ".s_md_members_content, .s_md_member_profile_content, .s_md_attendees_content"
        )) {
            el.classList.add("o_not_editable");
            el.setAttribute("data-oe-protected", "true");
            el.setAttribute("contenteditable", "false");
        }
    }

    cleanForSave({ root }) {
        for (const el of root.querySelectorAll(".s_md_members_filters_host")) {
            el.remove();
        }
        for (const el of root.querySelectorAll(".s_md_members_content")) {
            el.innerHTML = MEMBERS_PLACEHOLDER;
            el.classList.add("o_not_editable");
            el.setAttribute("data-oe-protected", "true");
            el.removeAttribute("contenteditable");
        }
        for (const el of root.querySelectorAll(".s_md_member_profile_content")) {
            el.innerHTML = PROFILE_PLACEHOLDER;
            el.classList.add("o_not_editable");
            el.setAttribute("data-oe-protected", "true");
            el.removeAttribute("contenteditable");
        }
        for (const el of root.querySelectorAll(".s_md_attendees_content")) {
            el.innerHTML = ATTENDEES_PLACEHOLDER;
            el.classList.add("o_not_editable");
            el.setAttribute("data-oe-protected", "true");
            el.removeAttribute("contenteditable");
        }
    }
}

registry.category("website-plugins").add(MdSnippetOptionPlugin.id, MdSnippetOptionPlugin);
