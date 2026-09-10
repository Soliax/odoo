/** @odoo-module **/

import { BuilderAction } from "@html_builder/core/builder_action";
import { BaseOptionComponent } from "@html_builder/core/utils";
import { Plugin } from "@html_editor/plugin";
import { withSequence } from "@html_editor/utils/resource";
import { before, SNIPPET_SPECIFIC_END } from "@html_builder/utils/option_sequence";
import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";

export class MdMembersOption extends BaseOptionComponent {
    static template = "website_member.MdMembersOption";
    static selector = ".s_md_members";
    static title = _t("Members");
}

export class MdAttendeesOption extends BaseOptionComponent {
    static template = "website_member.MdAttendeesOption";
    static selector = ".s_md_event_attendees";
    static title = _t("Event Participants");
}

export class ReloadMdSnippetAction extends BuilderAction {
    static id = "reloadMdSnippet";
    apply({ editingElement }) {
        return this.dispatchTo("update_interactions", editingElement);
    }
}

class MdSnippetOptionPlugin extends Plugin {
    static id = "mdSnippetOption";
    resources = {
        builder_options: [
            withSequence(before(SNIPPET_SPECIFIC_END), MdMembersOption),
            withSequence(before(SNIPPET_SPECIFIC_END), MdAttendeesOption),
        ],
        so_content_addition_selector: [".s_md_members", ".s_md_event_attendees"],
        builder_actions: {
            ReloadMdSnippetAction,
        },
    };
}

registry.category("website-plugins").add(MdSnippetOptionPlugin.id, MdSnippetOptionPlugin);
