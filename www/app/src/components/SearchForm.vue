<template>
    <div>
        <b-card no-body class="shadow" style="border: transparent">
            <b-form @submit.prevent @reset="onReset" @keyup.enter="onSubmit()">
                <div id="form-body">
                    <div id="initial-form">
                        <b-button-group id="report" style="width: 100%; top: -1px">
                            <b-button
                                :id="report.value"
                                v-for="searchReport in reports"
                                @click="reportChange(searchReport.value)"
                                :key="searchReport.value"
                                :class="{ active: currentReport == searchReport.value }"
                                squared
                                ><span v-if="searchReport.value != 'kwic'">{{ searchReport.label }}</span>
                                <span v-else
                                    ><span class="d-md-inline d-sm-none">Keyword In Context</span
                                    ><span class="d-md-none">{{ searchReport.label }}</span></span
                                >
                            </b-button>
                        </b-button-group>
                        <div id="search_terms_container" class="p-3">
                            <b-row id="search_terms">
                                <b-col cols="12" md="8">
                                    <b-input-group id="q-group">
                                        <b-input-group-prepend>
                                            <b-button variant="outline-secondary">Search Terms</b-button>
                                            <b-button
                                                v-b-modal.search-tips
                                                variant="outline-info"
                                                @mouseover="showTips = true"
                                                @mouseleave="showTips = false"
                                            >
                                                <span v-if="!showTips">?</span>
                                                <span v-if="showTips">Tips</span>
                                            </b-button>
                                        </b-input-group-prepend>

                                        <b-form-input
                                            type="text"
                                            v-model.lazy="queryTermTyped"
                                            @input="onChange('q')"
                                            @keyup.down.native="onArrowDown('q')"
                                            @keyup.up.native="onArrowUp('q')"
                                            @keyup.enter.native="onEnter('q')"
                                        ></b-form-input>
                                        <ul
                                            id="autocomplete-q"
                                            class="autocomplete-results shadow"
                                            :style="autoCompletePosition('q')"
                                            v-if="autoCompleteResults.q.length > 0"
                                        >
                                            <li
                                                tabindex="-1"
                                                v-for="(result, i) in autoCompleteResults.q"
                                                :key="result"
                                                @click="setResult(result, 'q')"
                                                class="autocomplete-result"
                                                :class="{ 'is-active': i === arrowCounters.q }"
                                                v-html="result"
                                            ></li>
                                        </ul>
                                        <b-input-group-append>
                                            <b-button variant="secondary" id="button-search" @click="onSubmit()"
                                                >Search</b-button
                                            >
                                        </b-input-group-append>
                                    </b-input-group>
                                </b-col>
                            </b-row>
                            <div class="mt-2">
                                <b-form-checkbox
                                    id="approximate"
                                    style="display: inline-block; height: 31px"
                                    v-model="approximateSelected"
                                    value="yes"
                                    switch
                                    unchecked-value="no"
                                    @change="approximateChange(approximateSelected)"
                                    >Approximate match</b-form-checkbox
                                >
                                <b-form-select
                                    style="max-width: fit-content; margin-left: 0.5rem"
                                    :options="approximateValues"
                                    v-model="approximate_ratio"
                                    size="sm"
                                ></b-form-select>
                                <span id="method-args" class="pl-2" v-if="currentReport != 'collocation'">
                                    <b-form-select
                                        style="max-width: fit-content; height: 31px"
                                        v-model="method"
                                        :options="methodOptions"
                                        size="sm"
                                    ></b-form-select>
                                    <input
                                        type="text"
                                        name="arg_proxy"
                                        class="d-inline-block mx-1"
                                        style="width: 50px; text-align: center; height: 31px"
                                        v-model="arg_proxy"
                                        size="sm"
                                        v-if="method == 'proxy'"
                                    />
                                    <input
                                        type="text"
                                        name="arg_phrase"
                                        class="d-inline-block mx-1"
                                        style="width: 50px; text-align: center; height: 31px"
                                        v-model="arg_phrase"
                                        size="sm"
                                        v-if="method == 'phrase'"
                                    />
                                    <span v-if="method != 'cooc'"> words in the same sentence</span></span
                                >
                            </div>
                        </div>
                        <div id="head-search-container" class="px-3 pt-1 pb-3" v-if="dictionary">
                            <div class="input-group" id="head-group">
                                <div class="input-group-prepend">
                                    <b-button variant="outline-secondary">{{
                                        metadataDisplay[headIndex].label
                                    }}</b-button>
                                </div>
                                <input
                                    type="text"
                                    class="form-control"
                                    :name="metadataDisplay[headIndex].value"
                                    :placeholder="metadataDisplay[headIndex].example"
                                    v-model="metadataValues.head"
                                    @input="onChange('head')"
                                    @keydown.down="onArrowDown(metadataDisplay[headIndex].value)"
                                    @keydown.up="onArrowUp(metadataDisplay[headIndex].value)"
                                    @keyup.enter="onEnter(metadataDisplay[headIndex].value)"
                                />
                                <ul
                                    :id="'autocomplete-' + metadataDisplay[headIndex].value"
                                    class="autocomplete-results shadow"
                                    :style="autoCompletePosition(metadataDisplay[headIndex].value)"
                                    v-if="autoCompleteResults[metadataDisplay[headIndex].value].length > 0"
                                >
                                    <li
                                        tabindex="-1"
                                        v-for="(result, i) in autoCompleteResults[metadataDisplay[headIndex].value]"
                                        :key="result"
                                        @click="setResult(result, metadataDisplay[headIndex].value)"
                                        class="autocomplete-result"
                                        :class="{
                                            'is-active': i === arrowCounters[metadataDisplay[headIndex].value],
                                        }"
                                        v-html="result"
                                    ></li>
                                </ul>
                            </div>
                        </div>
                        <div id="search-buttons">
                            <b-button-group>
                                <b-button type="reset" id="reset_form" variant="outline-secondary" @click="onReset()"
                                    >Clear</b-button
                                >
                                <b-button
                                    type="button"
                                    id="show-search-form"
                                    variant="secondary"
                                    @click="toggleForm()"
                                    >{{ searchOptionsButton }}</b-button
                                >
                            </b-button-group>
                        </div>
                    </div>
                    <transition name="slide-fade">
                        <div id="search-elements" v-if="formOpen" class="pl-3 pr-3 pb-3 shadow">
                            <div class="mt-2">
                                <h6>Filter by metadata field:</h6>
                                <div
                                    class="input-group pb-2"
                                    v-for="localField in metadataDisplayFiltered"
                                    :key="localField.value"
                                    :id="localField.value + '-group'"
                                >
                                    <b-input-group-prepend>
                                        <b-button
                                            variant="outline-secondary"
                                            v-if="metadataInputStyle[localField.value] != 'checkbox'"
                                            >{{ localField.label }}</b-button
                                        >
                                    </b-input-group-prepend>
                                    <input
                                        type="text"
                                        class="form-control"
                                        :name="localField.value"
                                        :placeholder="localField.example"
                                        v-model="metadataValues[localField.value]"
                                        @input="onChange(localField.value)"
                                        @keydown.down="onArrowDown(localField.value)"
                                        @keydown.up="onArrowUp(localField.value)"
                                        @keyup.enter="onEnter(localField.value)"
                                        v-if="metadataInputStyle[localField.value] == 'text'"
                                    />

                                    <ul
                                        :id="'autocomplete-' + localField.value"
                                        class="autocomplete-results shadow"
                                        :style="autoCompletePosition(localField.value)"
                                        v-if="autoCompleteResults[localField.value].length > 0"
                                    >
                                        <li
                                            tabindex="-1"
                                            v-for="(result, i) in autoCompleteResults[localField.value]"
                                            :key="result"
                                            @click="setResult(result, localField.value)"
                                            class="autocomplete-result"
                                            :class="{ 'is-active': i === arrowCounters[localField.value] }"
                                            v-html="result"
                                        ></li>
                                    </ul>
                                    <b-form-select
                                        :id="localField.value"
                                        :options="metadataChoiceValues[localField.value]"
                                        v-model="metadataValues[localField.value]"
                                        v-if="metadataInputStyle[localField.value] == 'dropdown'"
                                    ></b-form-select>
                                    <b-button
                                        class="mr-2"
                                        style="border-top-right-radius: 0; border-bottom-right-radius: 0"
                                        variant="outline-secondary"
                                        v-if="metadataInputStyle[localField.value] == 'checkbox'"
                                        >{{ localField.label }}</b-button
                                    >
                                    <b-form-checkbox-group
                                        style="padding-top: 0.35rem"
                                        :id="localField.value"
                                        :options="metadataChoiceValues[localField.value]"
                                        v-model="metadataChoiceSelected[localField.value]"
                                        v-if="metadataInputStyle[localField.value] == 'checkbox'"
                                    ></b-form-checkbox-group>
                                </div>
                            </div>
                            <b-input-group class="mt-4" v-if="currentReport === 'collocation'">
                                <template v-slot:prepend>
                                    <span class="btn btn-outline-secondary" style="height: fit-content"
                                        >Word filtering</span
                                    >
                                </template>
                                <b-form-input
                                    name="filter_frequency"
                                    placeholder="100"
                                    v-model="filter_frequency"
                                    style="max-width: 60px; text-align: center"
                                ></b-form-input>
                                <b-form-group>
                                    <b-form-radio-group
                                        id="btn-radios-3"
                                        v-model="colloc_filter_choice"
                                        :options="collocationOptions"
                                        buttons
                                        stacked
                                    ></b-form-radio-group>
                                </b-form-group>
                            </b-input-group>
                            <b-input-group class="mt-4 pt-1 pb-2" v-if="currentReport === 'time_series'">
                                <template v-slot:prepend>
                                    <span class="btn btn-outline-secondary">Date range</span>
                                    <b-input-group-text>from</b-input-group-text>
                                </template>
                                <input
                                    type="text"
                                    name="start_date"
                                    id="start_date"
                                    style="width: 50px; text-align: center"
                                    v-model="start_date"
                                />
                                <b-input-group-text>to</b-input-group-text>
                                <input
                                    type="text"
                                    name="end_date"
                                    id="end_date"
                                    style="width: 50px; text-align: center"
                                    v-model="end_date"
                                />
                            </b-input-group>
                            <b-input-group v-if="currentReport == 'time_series'">
                                <template v-slot:prepend>
                                    <span class="btn btn-outline-secondary">Year interval</span>
                                    <b-input-group-text>every</b-input-group-text>
                                </template>
                                <input
                                    type="text"
                                    name="year_interval"
                                    id="year_interval"
                                    style="width: 50px; text-align: center"
                                    v-model="year_interval"
                                />
                                <template v-slot:append>
                                    <b-input-group-text>year(s)</b-input-group-text>
                                </template>
                            </b-input-group>
                            <b-input-group class="mt-4" v-if="currentReport === 'aggregation'">
                                <template v-slot:prepend>
                                    <span class="btn btn-outline-secondary">Group results by</span>
                                </template>
                                <b-form-select
                                    style="max-width: fit-content"
                                    v-model="group_by"
                                    :options="aggregationOptions"
                                ></b-form-select>
                            </b-input-group>
                            <h6 class="mt-3" v-if="currentReport === 'concordance' || currentReport === 'bibliography'">
                                Display Options:
                            </h6>
                            <b-input-group
                                class="pb-2"
                                v-if="currentReport === 'concordance' || currentReport === 'bibliography'"
                            >
                                <template v-slot:prepend>
                                    <span class="btn btn-outline-secondary">Sort results by</span>
                                </template>
                                <b-form-select style="max-width: fit-content" v-model="sort_by" :options="sortValues">
                                    <option>Sort results by</option>
                                </b-form-select>
                            </b-input-group>
                            <b-input-group
                                v-if="
                                    currentReport != 'collocation' &&
                                    currentReport != 'time_series' &&
                                    currentReport != 'aggregation'
                                "
                            >
                                <template v-slot:prepend>
                                    <span class="btn btn-outline-secondary">Results per page</span>
                                </template>
                                <b-form-group style="margin-bottom: 0">
                                    <b-form-radio-group
                                        id="btn-radios-3"
                                        v-model="results_per_page"
                                        :options="resultsPerPageOptions"
                                        buttons
                                        name="radio-btn"
                                    ></b-form-radio-group>
                                </b-form-group>
                            </b-input-group>
                        </div>
                    </transition>
                </div>
            </b-form>
        </b-card>

        <div class="d-flex justify-content-center position-relative" v-if="searching">
            <b-spinner
                variant="secondary"
                style="width: 8rem; height: 8rem; position: absolute; z-index: 50; top: 30px"
            ></b-spinner>
        </div>
        <b-modal id="search-tips" size="lg" scrollable title="Search Syntax" hide-header-close ok-only>
            <SearchTips></SearchTips>
        </b-modal>
    </div>
</template>

<script>
import { mapFields } from "vuex-map-fields";
import { EventBus } from "../main.js";
import SearchTips from "./SearchTips";

export default {
    name: "SearchForm",
    components: {
        SearchTips,
    },
    computed: {
        ...mapFields([
            "formData.report",
            "formData.q",
            "formData.colloc_filter_choice",
            "formData.filter_frequency",
            "formData.approximate",
            "formData.approximate_ratio",
            "formData.method",
            "formData.arg_proxy",
            "formData.arg_phrase",
            "formData.start_date",
            "formData.end_date",
            "formData.year_interval",
            "formData.sort_by",
            "formData.results_per_page",
            "formData.start",
            "formData.end",
            "formData.byte",
            "formData.group_by",
            "searching",
            "currentReport",
        ]),
        formData() {
            return this.$store.state.formData;
        },
        sortValues() {
            let sortValues = [
                {
                    value: "rowid",
                    text: "select",
                },
            ];
            for (let fields of this.$philoConfig.concordance_biblio_sorting) {
                let label = [];
                for (let field of fields) {
                    if (field in this.$philoConfig.metadata_aliases) {
                        label.push(this.$philoConfig.metadata_aliases[field]);
                    } else {
                        label.push(field);
                    }
                }
                sortValues.push({ text: label.join(", "), value: fields });
            }
            return sortValues;
        },
        metadataDisplayFiltered() {
            if (!this.dictionary) {
                return this.metadataDisplay;
            } else {
                let localMetadataDisplay = this.copyObject(this.metadataDisplay);
                localMetadataDisplay.splice(this.headIndex, 1);
                return localMetadataDisplay;
            }
        },
    },
    data() {
        return {
            dictionary: this.$philoConfig.dictionary,
            metadataInputStyle: this.$philoConfig.metadata_input_style,
            headIndex: 0,
            formOpen: false,
            searchOptionsButton: "Show search options",
            approximateValues: [
                { text: "90% or higher", value: "90" },
                { text: "80% or higher", value: "80" },
            ],
            approximateSelected: "no",
            methodOptions: [
                { text: "Within", value: "proxy" },
                { text: "Exactly", value: "phrase" },
                { text: "In the same sentence", value: "cooc" },
            ],
            metadataDisplay: [],
            metadataValues: {},
            metadataChoiceValues: {},
            metadataChoiceSelected: {},
            collocationOptions: [
                { text: "Most Frequent Terms", value: "frequency" },
                { text: "Less distinctive terms on average", value: "tfidf" },
                { text: "Stopwords", value: "stopwords" },
                { text: "No Filtering", value: "nofilter" },
            ],
            selectedSortValues: "rowid",
            resultsPerPageOptions: [25, 100, 500, 1000],
            aggregationOptions: this.$philoConfig.stats_report_config.map((f) => ({
                text: this.$philoConfig.metadata_aliases[f.field] || f.field.charAt(0).toUpperCase() + f.field.slice(1),
                value: f.field,
            })),
            statFieldSelected: this.getLoadedStatField(),
            autoCompleteResults: { q: [] },
            arrowCounters: { q: -1 },
            isOpen: false,
            showTips: false,
            queryTermTyped: this.$route.query.q || this.q || "",
            metadataTyped: {},
        };
    },
    watch: {
        // call again the method if the route changes
        $route: "updateInputData",
    },
    created() {
        this.reports = this.buildReports();
        for (let metadataField of this.$philoConfig.metadata) {
            let metadataObj = {
                label: metadataField[0].toUpperCase() + metadataField.slice(1),
                value: metadataField,
                example: this.$philoConfig.search_examples[metadataField],
            };
            if (metadataField in this.$philoConfig.metadata_aliases) {
                metadataObj.label = this.$philoConfig.metadata_aliases[metadataField];
            }
            this.metadataDisplay.push(metadataObj);
            if (this.formData[metadataField] != "") {
                if (this.$philoConfig.metadata_input_style[metadataField] == "text") {
                    this.metadataValues[metadataField] = this.formData[metadataField];
                } else {
                    this.metadataChoiceSelected[metadataField] = this.formData[metadataField].split(" | ");
                }
            }
            this.$set(this.autoCompleteResults, metadataField, []);
            this.$set(this.arrowCounters, metadataField, -1);
            if (metadataField == "head") {
                this.headIndex = this.metadataDisplay.length - 1;
            }
        }
        EventBus.$on("metadataUpdate", (metadata) => {
            for (let field in metadata) {
                this.metadataValues[field] = metadata[field];
            }
            for (let metadataField of this.$philoConfig.metadata) {
                this.$set(this.autoCompleteResults, metadataField, []);
                this.$set(this.arrowCounters, metadataField, -1);
            }
        });
        for (let metadata in this.$philoConfig.metadata_choice_values) {
            this.metadataChoiceValues[metadata] = [];
            let choiceValue = this.$philoConfig.metadata_choice_values[metadata];
            for (let i = 0; i < choiceValue.length; i++) {
                let quotedValue = choiceValue[i].value;
                this.metadataChoiceValues[metadata].push({
                    text: choiceValue[i].label,
                    value: quotedValue,
                });
            }
        }
    },
    mounted() {
        this.$nextTick(() => {
            document.getElementById("form-body").addEventListener("change", (event) => {
                if (event.srcElement.id in this.$philoConfig.metadata_choice_values) {
                    let value =
                        event.srcElement.options[document.getElementById(event.srcElement.id).selectedIndex].value;
                    this.$store.commit("updateFormDataField", {
                        key: event.srcElement.id,
                        value: value,
                    });
                }
            });
        });
    },
    methods: {
        approximateChange(val) {
            if (val == "yes") {
                this.approximate_ratio = "90";
            } else {
                this.approximate_ratio = "";
            }
        },
        updateInputData() {
            this.queryTermTyped = this.q;
            for (let field in this.metadataValues) {
                this.metadataValues[field] = this.formData[field];
            }
        },
        buildReports() {
            let reports = [];
            for (let value of this.$philoConfig.search_reports) {
                let label = value.replace("_s", "-s");
                label = label.charAt(0).toUpperCase() + label.slice(1);
                reports.push({
                    value: value,
                    label: label,
                });
            }
            return reports;
        },
        buildMetadataFieldDisplay() {
            for (let metadataField of this.$philoConfig.metadata) {
                let metadataObj = {
                    label: metadataField[0].toUpperCase() + metadataField.slice(1),
                    value: metadataField,
                    example: this.$philoConfig.search_examples[metadataField],
                };
                if (metadataField in this.$philoConfig.metadata_aliases) {
                    metadataObj.label = this.$philoConfig.metadata_aliases[metadataField];
                }
                this.metadataValues[metadataField] = "";
                this.metadataDisplay.push(metadataObj);
            }
        },
        getLoadedStatField() {
            let queryParam = this.$store.state.formData.group_by;
            if (queryParam) {
                return (
                    this.$philoConfig.metadata_aliases[queryParam] ||
                    queryParam.charAt(0).toUpperCase() + queryParam.slice(1)
                );
            }
        },
        onSubmit() {
            this.report = this.currentReport;
            this.formOpen = false;
            let metadataChoices = Object.fromEntries(
                Object.entries(this.metadataChoiceSelected).map(([key, val]) => [key, val.join(" | ")])
            );
            this.$router.push(
                this.paramsToRoute({
                    ...this.$store.state.formData,
                    ...this.metadataValues,
                    ...metadataChoices,
                    approximate: this.approximateSelected,
                    q: this.queryTermTyped.trim(),
                    start: "",
                    end: "",
                    byte: "",
                })
            );
        },
        onReset() {
            this.$store.commit("setDefaultFields", this.$parent.defaultFieldValues);
            for (let field in this.metadataValues) {
                this.metadataValues[field] = "";
            }
            this.$nextTick(() => {
                this.show = true;
            });
        },
        reportChange(report) {
            if (report === "landing_page") {
                this.report = this.$philoConfig.search_reports[0];
            } else if (report === "collocation") {
                if (this.$philoConfig.stopwords.length > 0) {
                    this.colloc_filter_choice = "stopwords";
                } else {
                    this.colloc_filter_choice = "frequency";
                }
            }
            this.currentReport = report;
            if (!this.formOpen) {
                this.toggleForm();
            }
        },
        toggleForm() {
            if (!this.formOpen) {
                this.formOpen = true;
                this.searchOptionsButton = "Hide search options";
            } else {
                this.formOpen = false;
                this.searchOptionsButton = "Show search options";
            }
        },
        clearFormData() {},
        selectApproximate(approximateValue) {
            this.approximate_ratio = approximateValue;
        },
        onChange(field) {
            if (this.timeout) clearTimeout(this.timeout);
            this.timeout = setTimeout(() => {
                if (field == "q") {
                    let currentQueryTerm = this.$route.query.q;
                    if (this.queryTermTyped.replace('"', "").length > 1 && this.queryTermTyped != currentQueryTerm) {
                        this.$http
                            .get(`${this.$dbUrl}/scripts/autocomplete_term.py`, {
                                params: { term: this.queryTermTyped },
                            })
                            .then((response) => {
                                this.autoCompleteResults.q = response.data;
                                this.isLoading = false;
                            });
                    }
                } else {
                    let currentFieldValue = this.$route.query[field];
                    if (this.metadataValues[field].length > 1 && this.metadataValues[field] != currentFieldValue) {
                        this.$http
                            .get(`${this.$dbUrl}/scripts/autocomplete_metadata.py`, {
                                params: {
                                    term: this.metadataValues[field],
                                    field: field,
                                },
                            })
                            .then((response) => {
                                this.autoCompleteResults[field] = response.data.map((result) =>
                                    result.replace(/CUTHERE/, "<last/>")
                                );
                            })
                            .catch((error) => {
                                this.debug(this, error);
                            });
                    }
                }
                let popup = document.querySelector(`#autocomplete-${field}`);
                const clearAutocomplete = (e) => {
                    if (e.target !== popup) {
                        this.autoCompleteResults[field] = [];
                    }
                    window.removeEventListener("click", clearAutocomplete);
                };
                window.addEventListener("click", clearAutocomplete);
            }, 200);
        },
        onArrowDown(field) {
            if (this.arrowCounters[field] < this.autoCompleteResults[field].length) {
                this.arrowCounters[field] = this.arrowCounters[field] + 1;
            }
            if (this.arrowCounters[field] > 5) {
                let container = document.getElementById(`autocomplete-${field}`);
                let topOffset = container.scrollTop;
                container.scrollTop = topOffset + 36;
            }
        },
        onArrowUp(field) {
            if (this.arrowCounters[field] > 0) {
                this.arrowCounters[field] = this.arrowCounters[field] - 1;
            }
            let container = document.getElementById(`autocomplete-${field}`);
            let topOffset = container.scrollTop;
            container.scrollTop = topOffset - 36;
        },
        onEnter(field) {
            console.log(field);
            let result = this.autoCompleteResults[field][this.arrowCounters[field]];
            this.setResult(result, field);
        },
        handleClickOutside(evt) {
            if (!this.$el.contains(evt.target)) {
                this.isOpen = false;
                for (let field in this.arrowCounters) {
                    this.arrowCounters[field] = -1;
                }
            }
        },
        setResult(inputString, field) {
            if (typeof inputString != "undefined") {
                let inputGroup, lastInput;
                if (field == "q") {
                    inputGroup = inputString.replace(/<[^>]+>/g, "").split(/(\s*\|\s*|\s*OR\s*|\s+|\s*NOT\s*)/);
                    lastInput = inputGroup.pop();
                    if (lastInput.match(/"/)) {
                        if (lastInput.startsWith('"')) {
                            lastInput = lastInput.slice(1);
                        }
                        if (lastInput.endsWith('"')) {
                            lastInput = lastInput.slice(0, lastInput.length - 1);
                        }
                    }
                    this.queryTermTyped = `${inputGroup.join("")}"${lastInput.trim()}"`;
                } else {
                    let prefix = "";
                    if (inputString.match(/<last\/>/)) {
                        inputGroup = inputString.split(/<last\/>/);
                        lastInput = inputGroup.pop();
                        lastInput = lastInput.trim().replace(/<[^>]+>/g, "");
                        prefix = inputGroup.join("");
                    } else {
                        lastInput = inputString.replace(/<[^>]+>/g, "").trim();
                    }
                    if (lastInput.match(/"/)) {
                        if (lastInput.startsWith('"')) {
                            lastInput = lastInput.slice(1);
                        }
                        if (lastInput.endsWith('"')) {
                            lastInput = lastInput.slice(0, lastInput.length - 1);
                        }
                    }
                    let finalInput = `${prefix}"${lastInput}"`;
                    this.metadataValues[field] = finalInput;
                    this.$store.commit("updateFormDataField", {
                        key: field,
                        value: finalInput,
                    });
                }
            }
            this.autoCompleteResults[field] = [];
            this.arrowCounters[field] = -1;
        },
        autoCompletePosition(field) {
            let parent = document.getElementById(`${field}-group`);
            if (parent) {
                let input = parent.querySelector("input");
                let childOffset = input.offsetLeft - parent.offsetLeft;
                return `left: ${childOffset}px; width: ${input.offsetWidth}px`;
            }
        },
    },
};
</script>

<style scoped>
.input-group,
#search-elements h6 {
    max-width: 700px;
}
#report .btn {
    font-variant: small-caps;
}
.dico-margin {
    margin-top: 210px !important;
}
#search-elements {
    position: absolute;
    z-index: 50;
    background-color: #fff;
    width: 100%;
    left: 0;
}
#search-elements.dico {
    margin-top: 168px;
}

#search-elements > h5 {
    margin-top: 15px;
    margin-bottom: 15px;
}

#search-elements .btn-outline-secondary,
#q-group .btn-outline-secondary,
#head-group .btn {
    pointer-events: none; /*disable hover effect*/
}

#report label {
    font-size: 1.1em;
    font-variant: small-caps;
    text-transform: capitalize;
}

.search_box {
    width: 250px;
    vertical-align: middle;
}

#search_field {
    font-weight: 400;
}

#more_options {
    width: 200px;
}

#more_options:hover {
    cursor: pointer;
}

#search_terms_container {
    padding-top: 15px;
    padding-bottom: 15px;
}

#search_terms,
#head-search-container {
    text-align: center;
}

#head-search-container {
    margin-top: -10px;
    padding-bottom: 15px;
}

.no-example {
    display: none;
}

#method,
.metadata_fields,
#collocation-options > div,
#time-series-options > div {
    margin-top: 10px;
}

#initial-form .btn-primary.active {
    box-shadow: 0px 0px;
    border-top: 0px;
}

#tip-text {
    display: none;
}

#tip-btn:hover #tip-text {
    display: inline;
}

#tip-btn:hover #tip {
    display: none;
}

#search_terms .row {
    text-align: left;
    padding-left: 20px;
    padding-right: 20px;
}
#search-buttons {
    position: absolute;
    bottom: 1rem;
    right: 1rem;
    z-index: 51;
}

@media (max-width: 992px) {
    #search-buttons {
        position: initial;
        margin-bottom: 1rem;
        margin-left: 0;
        margin-right: 0;
        text-align: center;
    }
    #search-elements {
        margin-top: -1rem;
    }
}

@media (max-width: 768px) {
    #method-args {
        display: block;
        margin-left: -0.5rem;
    }
    #collocation-options .row {
        margin-left: -15px;
    }
}

/*Dico layout changes*/

#search_elements {
    border-top-width: 0px;
}

.select {
    font-size: inherit;
    position: relative;
    display: inline-block;
    width: 100%;
    text-align: center;
}

.select select {
    outline: none;
    -webkit-appearance: none;
    display: block;
    padding: 6px 12px;
    margin: 0;
    transition: border-color 0.2s;
    border: 1px solid #ccc;
    border-radius: 0px;
    background: #fff;
    color: #555;
    line-height: normal;
    font-family: inherit;
    font-size: inherit;
    line-height: inherit;
    width: 100%;
}

.autocomplete {
    position: relative;
}
.autocomplete-results {
    padding: 0;
    margin: 3px 0 0 15px;
    border: 1px solid #eeeeee;
    border-top-width: 0px;
    max-height: 216px;
    overflow-y: scroll;
    width: 267px;
    position: absolute;
    left: 0;
    background-color: #fff;
    z-index: 100;
    top: 34px;
    font-size: 1.2rem;
}
.autocomplete-result {
    list-style: none;
    text-align: left;
    padding: 4px 12px;
    cursor: pointer;
    font-size: 1.2rem;
}
.autocomplete-result:hover,
.is-active {
    background-color: #ddd;
    color: black;
}
::placeholder {
    /* Chrome, Firefox, Opera, Safari 10.1+ */
    opacity: 0.4; /* Firefox */
}

:-ms-input-placeholder {
    /* Internet Explorer 10-11 */
    opacity: 0.4;
}

::-ms-input-placeholder {
    /* Microsoft Edge */
    opacity: 0.4;
}
input:focus::placeholder {
    /* Chrome, Firefox, Opera, Safari 10.1+ */
    opacity: 0; /* Firefox */
}

input:focus:-ms-input-placeholder {
    /* Internet Explorer 10-11 */
    opacity: 0;
}

input:focus::-ms-input-placeholder {
    /* Microsoft Edge */
    opacity: 0;
}
.code-block {
    font-family: monospace;
    font-size: 120%;
    background-color: #ededed;
    padding: 0px 4px;
}
.slide-fade-enter-active {
    transition: all 0.3s ease-out;
}
.slide-fade-leave-active {
    transition: all 0.3s ease-out;
}
.slide-fade-enter, .slide-fade-leave-to
/* .slide-fade-leave-active below version 2.1.8 */ {
    transform: translateY(-30px);
    opacity: 0;
}
</style>