/** @odoo-module **/

import { Interaction } from "@web/public/interaction";
import { registry } from "@web/core/registry";
import { rpc } from "@web/core/network/rpc";

const FLAG_ON = (value) => value === "1" || value === "true";
const MULTI_KEYS = ["brevet", "specialty", "category"];

const OPTION_ATTRS = [
    "data-show-brevets-filters",
    "data-show-specialties-filters",
    "data-show-categories-filters",
    "data-tcg-visual",
    "data-columns",
    "data-limit",
];

export class MdMembersSnippet extends Interaction {
    static selector = ".s_md_members";
    dynamicContent = {
        "[data-md-filters]": {
            "t-on-change": this.onFilterChange,
            "t-on-submit.prevent": this.onFilterChange,
            "t-on-mousedown.stop": this.onFilterGuard,
            "t-on-click.stop": this.onFilterGuard,
        },
        "[data-md-filters] .s_md_filter_dropdown": {
            "t-on-click.stop": this.onFilterGuard,
            "t-on-mousedown.stop": this.onFilterGuard,
        },
        "[data-md-filters] input[name='search']": {
            "t-on-keydown": this.onSearchKeydown,
            "t-on-input": this.onSearchInput,
        },
        ".s_md_card, .s_md_event_card": {
            "t-on-click": this.onCardClick,
            "t-on-mousedown": this.onCardMouseDown,
        },
    };

    setup() {
        this.rpc = rpc;
        this._searchTimer = null;
        this._filterTimer = null;
        this._optTimer = null;
        this._optionObserver = null;
        this._loading = false;
        this._pendingReload = false;
        this._filterState = {
            brevet: [],
            specialty: [],
            category: [],
            search: "",
        };
    }

    get isEditor() {
        return Boolean(
            this.el.closest(".o_editable, .o_wysiwyg_loader, #wrapwrap.o_editable, .o_builder_page")
        );
    }

    async willStart() {
        this.ensureOptionScheme();
        await this.loadMembers({ full: true });
    }

    start() {
        this._optionObserver = new MutationObserver(() => {
            clearTimeout(this._optTimer);
            this._optTimer = setTimeout(() => this.loadMembers({ full: true }), 40);
        });
        this._optionObserver.observe(this.el, {
            attributes: true,
            attributeFilter: OPTION_ATTRS,
        });
    }

    destroy() {
        this._optionObserver?.disconnect();
        clearTimeout(this._optTimer);
        clearTimeout(this._searchTimer);
        clearTimeout(this._filterTimer);
    }

    ensureOptionScheme() {
        const ds = this.el.dataset;
        if ("mdOptions" in ds) {
            return;
        }
        if ("showFilters" in ds) {
            const on = FLAG_ON(ds.showFilters) ? "1" : "0";
            ds.showBrevetsFilters = on;
            ds.showSpecialtiesFilters = on;
            ds.showCategoriesFilters = on;
            delete ds.showFilters;
            delete ds.showSpecialties;
        } else {
            if (!("showBrevetsFilters" in ds)) {
                ds.showBrevetsFilters = "1";
            }
            if (!("showSpecialtiesFilters" in ds)) {
                ds.showSpecialtiesFilters = "1";
            }
            if (!("showCategoriesFilters" in ds)) {
                ds.showCategoriesFilters = "1";
            }
        }
        if (!("tcgVisual" in ds)) {
            ds.tcgVisual = "0";
        }
        ds.mdOptions = "1";
    }

    snapshotFilters() {
        const form = this.el.querySelector("[data-md-filters]");
        const next = {
            brevet: [],
            specialty: [],
            category: [],
            search: "",
        };
        if (form) {
            for (const key of MULTI_KEYS) {
                next[key] = [...form.querySelectorAll(`input[name="${key}"]:checked`)]
                    .map((el) => String(el.value || "").trim())
                    .filter(Boolean);
            }
            const searchInput = form.querySelector(`input[name="search"]`);
            next.search = searchInput ? String(searchInput.value || "") : "";
        }
        this._filterState = next;
        this.syncFilterBadges();
        return next;
    }

    syncFilterBadges() {
        const form = this.el.querySelector("[data-md-filters]");
        if (!form) {
            return;
        }
        for (const key of MULTI_KEYS) {
            const badge = form.querySelector(`[data-md-count="${key}"]`);
            if (!badge) {
                continue;
            }
            const count = (this._filterState[key] || []).length;
            badge.textContent = count ? String(count) : "";
            badge.classList.toggle("d-none", !count);
        }
    }

    applyFilterStateToDom() {
        const form = this.el.querySelector("[data-md-filters]");
        if (!form) {
            return;
        }
        const state = this._filterState || {};
        for (const key of MULTI_KEYS) {
            const selected = new Set(state[key] || []);
            for (const input of form.querySelectorAll(`input[name="${key}"]`)) {
                input.checked = selected.has(String(input.value || ""));
            }
        }
        const searchInput = form.querySelector(`input[name="search"]`);
        if (searchInput) {
            searchInput.value = state.search || "";
        }
        this.syncFilterBadges();
    }

    getOptions(extra = {}) {
        this.ensureOptionScheme();
        const ds = this.el.dataset;
        const filters = this._filterState || this.snapshotFilters();
        return {
            show_brevets_filters: FLAG_ON(ds.showBrevetsFilters) ? "1" : "0",
            show_specialties_filters: FLAG_ON(ds.showSpecialtiesFilters) ? "1" : "0",
            show_categories_filters: FLAG_ON(ds.showCategoriesFilters) ? "1" : "0",
            tcg_visual: FLAG_ON(ds.tcgVisual) ? "1" : "0",
            columns: ds.columns || "4",
            limit: ds.limit || "0",
            brevet: (filters.brevet || []).join(","),
            specialty: (filters.specialty || []).join(","),
            category: (filters.category || []).join(","),
            search: filters.search || "",
            ...extra,
        };
    }

    async loadMembers(extra = {}) {
        const content = this.el.querySelector(".s_md_members_content");
        if (!content) {
            return;
        }
        if (this._loading) {
            this._pendingReload = true;
            return;
        }
        this._loading = true;
        // Keep existing form when possible so multi-select state survives.
        const hasForm = Boolean(content.querySelector("[data-md-filters]"));
        const full = Boolean(extra.full) || !hasForm;
        if (hasForm) {
            this.snapshotFilters();
        }
        const opts = this.getOptions();
        delete opts.full;
        try {
            const result = await this.rpc("/membres/snippet/members", opts);
            if (result.error === "login_required") {
                content.innerHTML =
                    '<div class="alert alert-warning mb-0">Connectez-vous pour voir les membres.</div>';
                return;
            }
            if (full || !content.querySelector(".s_md_members_results")) {
                content.innerHTML = result.html || "";
                this.applyFilterStateToDom();
            } else {
                const results = content.querySelector(".s_md_members_results");
                // Never inject full payload (filters + results) into the results
                // host — that duplicates the filter bar. Prefer results_html;
                // otherwise extract the results node from html.
                let chunk = result.results_html;
                if (chunk == null && result.html) {
                    const tmp = document.createElement("div");
                    tmp.innerHTML = result.html;
                    const node = tmp.querySelector(".s_md_members_results");
                    chunk = node ? node.innerHTML : "";
                }
                if (results) {
                    results.innerHTML = chunk || "";
                } else {
                    content.innerHTML = result.html || "";
                    this.applyFilterStateToDom();
                }
                this.syncFilterBadges();
            }
            content.classList.add("o_not_editable");
            content.setAttribute("data-oe-protected", "true");
            content.setAttribute("contenteditable", "false");
        } catch (_e) {
            content.innerHTML =
                '<div class="alert alert-danger mb-0">Impossible de charger les membres.</div>';
        } finally {
            this._loading = false;
            if (this._pendingReload) {
                this._pendingReload = false;
                this.loadMembers({ full: false });
            }
        }
    }

    onFilterGuard() {}

    onFilterChange() {
        this.snapshotFilters();
        clearTimeout(this._filterTimer);
        this._filterTimer = setTimeout(() => this.loadMembers({ full: false }), 80);
    }

    onSearchInput() {
        this.snapshotFilters();
        clearTimeout(this._searchTimer);
        this._searchTimer = setTimeout(() => this.loadMembers({ full: false }), 350);
    }

    onSearchKeydown(ev) {
        if (ev.key === "Enter") {
            ev.preventDefault();
            this.snapshotFilters();
            clearTimeout(this._searchTimer);
            this.loadMembers({ full: false });
        }
    }

    onCardMouseDown(ev) {
        if (this.isEditor) {
            ev.preventDefault();
            ev.stopPropagation();
        }
    }

    onCardClick(ev) {
        if (this.isEditor) {
            ev.preventDefault();
            ev.stopPropagation();
        }
    }
}

registry
    .category("public.interactions")
    .add("website_member.s_md_members", MdMembersSnippet);
