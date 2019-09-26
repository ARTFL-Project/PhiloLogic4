<template>
    <b-container fluid>
        <b-row>
            <b-col sm="10" offset-sm="1" xl="8" offset-xl="2">
                <b-card no-body class="shadow">
                    <b-form @submit.prevent @reset="onReset" @keyup.enter="onSubmit()">
                        <div id="form_body">
                            <div id="initial-form">
                                <b-button-group id="report" style="width: 100%">
                                    <b-button
                                        :id="report"
                                        v-for="searchReport in reports"
                                        @click="reportChange(searchReport.value)"
                                        :key="searchReport.value"
                                        :class="{'active':  report == searchReport.value}"
                                    >{{ searchReport.label }}</b-button>
                                </b-button-group>
                                <div id="search_terms_container" class="p-3">
                                    <b-row id="search_terms">
                                        <b-col cols="12" md="8">
                                            <b-input-group id="q-group" prepend="Search Terms">
                                                <b-input-group-prepend>
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
                                                    autocomplete="off"
                                                    type="text"
                                                    v-model="q"
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
                                                    <b-button
                                                        variant="outline-secondary"
                                                        id="button-search"
                                                        @click="onSubmit()"
                                                    >Search</b-button>
                                                </b-input-group-append>
                                            </b-input-group>
                                        </b-col>
                                        <b-col cols="12" md="4" id="search-buttons">
                                            <b-button-group>
                                                <b-button
                                                    type="reset"
                                                    id="reset_form"
                                                    variant="outline-danger"
                                                    @click="onReset()"
                                                >Clear</b-button>
                                                <b-button
                                                    type="button"
                                                    id="show-search-form"
                                                    variant="outline-info"
                                                    @click="toggleForm()"
                                                >{{ searchOptionsButton }}</b-button>
                                            </b-button-group>
                                        </b-col>
                                    </b-row>
                                </div>
                                <b-row id="head-search-container" class="p-3" v-if="dictionary">
                                    <b-col cols="12" md="8">
                                        <div class="input-group" id="head-group">
                                            <div class="input-group-prepend">
                                                <span
                                                    class="input-group-text"
                                                >{{metadataDisplay[headIndex].label}}</span>
                                            </div>
                                            <input
                                                type="text"
                                                class="form-control"
                                                autocomplete="off"
                                                :name="metadataDisplay[headIndex].value"
                                                :placeholder="metadataDisplay[headIndex].example"
                                                v-model="metadataValues.head"
                                                @input="onChange(metadataDisplay[headIndex].value)"
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
                                                    :class="{ 'is-active': i === arrowCounters[metadataDisplay[headIndex].value] }"
                                                    v-html="result"
                                                ></li>
                                            </ul>
                                        </div>
                                    </b-col>
                                </b-row>
                            </div>
                            <transition name="slide-fade">
                                s
                                <div id="search-elements" v-if="formOpen" class="pl-3 pr-3 shadow">
                                    <h5>Refine your search with the following options and fields:</h5>
                                    <b-row>
                                        <b-col cols="12" sm="2">Search Terms</b-col>
                                        <b-col cols="12" sm="10">
                                            <b-row>
                                                <b-col cols="12" sm="3">
                                                    <b-form-checkbox
                                                        id="checkbox-1"
                                                        v-model="approximate"
                                                        name="checkbox-1"
                                                        value="yes"
                                                        unchecked-value="no"
                                                    >Approximate match</b-form-checkbox>
                                                </b-col>
                                                <b-col
                                                    cols="12"
                                                    sm="9"
                                                    style="margin-top: -.5rem !important"
                                                    v-if="approximate === 'yes'"
                                                >
                                                    <b-dropdown
                                                        id="dropdown-1"
                                                        text="100%"
                                                        class="mr-1"
                                                    >
                                                        <b-dropdown-item
                                                            v-for="value in approximateValues"
                                                            @click="selectApproximate(value)"
                                                            :key="value"
                                                        >{{ value }}%</b-dropdown-item>
                                                    </b-dropdown>or more
                                                </b-col>
                                            </b-row>
                                        </b-col>
                                    </b-row>
                                    <b-row id="method" v-if="report != 'collocation'">
                                        <b-col cols="12" sm="2">Search Terms</b-col>
                                        <b-col cols="12" sm="3" lg="2" id="method-buttons">
                                            <b-form-group>
                                                <b-form-radio-group
                                                    id="btn-radios-3"
                                                    v-model="method"
                                                    :options="methodOptions"
                                                    buttons
                                                    stacked
                                                    size="sm"
                                                    name="radio-btn-stacked"
                                                ></b-form-radio-group>
                                            </b-form-group>
                                        </b-col>
                                        <b-col cols="12" sm="7" lg="8">
                                            <b-row>
                                                <b-col sm="8" md="5">
                                                    <b-input-group
                                                        size="sm"
                                                        append="words in the same sentence"
                                                    >
                                                        <b-form-input v-model="arg_proxy"></b-form-input>
                                                    </b-input-group>
                                                </b-col>
                                                <b-col sm="4" md="7"></b-col>
                                                <b-col sm="8" md="5">
                                                    <b-input-group
                                                        size="sm"
                                                        append="words in the same sentence"
                                                    >
                                                        <b-form-input v-model="arg_phrase"></b-form-input>
                                                    </b-input-group>
                                                </b-col>
                                            </b-row>
                                        </b-col>
                                    </b-row>
                                    <b-row
                                        v-for="localField in metadataDisplayFiltered"
                                        :key="localField.value"
                                    >
                                        <b-col cols="12" class="pb-2">
                                            <div
                                                class="input-group"
                                                :id="localField.value + '-group'"
                                            >
                                                <div class="input-group-prepend">
                                                    <span
                                                        class="input-group-text"
                                                    >{{localField.label}}</span>
                                                </div>
                                                <input
                                                    type="text"
                                                    class="form-control"
                                                    autocomplete="off"
                                                    :name="localField.value"
                                                    :placeholder="localField.example"
                                                    v-model="metadataValues[localField.value]"
                                                    @input="onChange(localField.value)"
                                                    @keydown.down="onArrowDown(localField.value)"
                                                    @keydown.up="onArrowUp(localField.value)"
                                                    @keyup.enter="onEnter(localField.value)"
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
                                            </div>
                                        </b-col>
                                    </b-row>
                                    <b-row id="collocation-options" v-if="report === 'collocation'">
                                        <b-col cols="12">
                                            <b-row>
                                                <b-col cols="3" sm="2">Word Filtering</b-col>
                                                <b-col cols="3" sm="2">
                                                    <b-form-input
                                                        name="filter_frequency"
                                                        placeholder="100"
                                                        v-model="filter_frequency"
                                                    ></b-form-input>
                                                </b-col>
                                                <b-col cols="6">
                                                    <b-form-group>
                                                        <b-form-radio-group
                                                            id="btn-radios-3"
                                                            v-model="colloc_filter_choice"
                                                            :options="collocationOptions"
                                                            buttons
                                                            stacked
                                                            size="sm"
                                                            name="radio-btn-stacked"
                                                        ></b-form-radio-group>
                                                    </b-form-group>
                                                </b-col>
                                            </b-row>
                                        </b-col>
                                    </b-row>
                                    <b-row id="time-series-options" v-if="report === 'time_series'">
                                        <b-col cols="12" sm="2">Date range:</b-col>
                                        <b-col cols="12" sm="10">
                                            from
                                            <input
                                                type="text"
                                                name="start_date"
                                                id="start_date"
                                                style="width:35px;"
                                                v-model="start_date"
                                            />
                                            to
                                            <input
                                                type="text"
                                                name="end_date"
                                                id="end_date"
                                                style="width:35px;"
                                                v-model="end_date"
                                            />
                                        </b-col>
                                    </b-row>
                                    <b-row id="date_range" v-if="report == 'time_series'">
                                        <b-col cols="12" sm="2">Year interval:</b-col>
                                        <b-col cols="12" sm="10">
                                            every
                                            <input
                                                type="text"
                                                name="year_interval"
                                                id="year_interval"
                                                style="width:35px; text-align: center;"
                                                v-model="year_interval"
                                            />&nbsp;years
                                        </b-col>
                                    </b-row>
                                    <b-row
                                        id="sort-options"
                                        v-if="report === 'concordance' || report === 'bibliography'"
                                    >
                                        <b-col cols="12" style="margin-top: 10px;">
                                            <b-row>
                                                <b-col cols="3" sm="2">Sort results by</b-col>
                                                <b-col cols="6" sm="4">
                                                    <b-form-select
                                                        v-model="sort_by"
                                                        :options="sortValues"
                                                        class="mb-3"
                                                    >
                                                        <option>Sort results by</option>
                                                    </b-form-select>
                                                </b-col>
                                            </b-row>
                                        </b-col>
                                    </b-row>
                                    <b-row
                                        id="results_per_page"
                                        v-if="report != 'collocation' && report != 'time_series'"
                                    >
                                        <b-col cols="12" sm="2">Results per page:</b-col>
                                        <b-col cols="12" sm="10">
                                            <b-form-group>
                                                <b-form-radio-group
                                                    id="btn-radios-3"
                                                    v-model="results_per_page"
                                                    :options="resultsPerPageOptions"
                                                    buttons
                                                    size="sm"
                                                    name="radio-btn"
                                                ></b-form-radio-group>
                                            </b-form-group>
                                        </b-col>
                                    </b-row>
                                </div>
                            </transition>
                        </div>
                    </b-form>
                </b-card>
            </b-col>
        </b-row>
        <div class="d-flex justify-content-center position-relative" v-if="searching">
            <b-spinner
                variant="secondary"
                style="width: 8rem; height: 8rem; position: absolute; z-index: 50; top: 30px;"
            ></b-spinner>
        </div>
        <b-modal
            id="search-tips"
            size="lg"
            scrollable
            title="Search Syntax"
            hide-header-close
            ok-only
        >
            <div class="p-2">
                PhiloLogic4's query syntax has 5 basic operators:
                <ul class="mt-2">
                    <li>
                        the plain token, essentially, any word at all, split on space, e.g.
                        <span
                            class="code-block"
                        >token</span>
                    </li>
                    <li>
                        the quoted token--a string in double quotes, which may contain a space, e.g.
                        <span
                            class="code-block"
                        >"token"</span>
                    </li>
                    <li>
                        the range--two tokens separated by a dash, e.g.
                        <span class="code-block">a-f</span>
                    </li>
                    <li>
                        boolean OR, represented grep-style as
                        <span class="code-block">|</span>, e.g.
                        <span class="code-block">token | word</span>
                    </li>
                    <li>
                        boolean NOT, represented SQL-style as
                        <span class="code-block">NOT</span>, e.g.
                        <span class="code-block">token.* NOT tokens</span>
                    </li>
                </ul>This syntax is the same, but interpreted slightly differently, for the two different types of text query fields: word search
                and metadata search.
                <h5 style="margin-top: 20px;">Word Searches</h5>Full-text word search is unique in having the concept of a "term", which is either a single plain/quoted term, or a group
                of plain/quoted terms joined by
                <span
                    class="code-block"
                >|</span>, optionally followed by
                <span class="code-block">NOT</span> and another term-like filter expression:
                <ol class="mt-2">
                    <li>
                        plain terms are evaluated without regard to accent. They are currently sensitive to case, to allow for named entity search--this
                        is currently implemented only for Greek, however. Regexes are permitted.
                    </li>
                    <li>quoted terms are case and accent sensitive. Regexes are permitted.</li>
                    <li>the range is not operational. In the future, stub this out to make hyphenated search terms less of a pain to escape.</li>
                    <li>
                        <span class="code-block">OR</span> can conjoin plain and quoted tokens, and precedes evaluation of phrase distance.
                    </li>
                    <li>
                        <span class="code-block">NOT</span> is a filter on a preceding term, but cannot stand alone:
                        <span
                            class="code-block"
                        >a.* NOT abalone</span> is legal,
                        <span class="code-block">NOT a.*</span> is illegal
                    </li>
                </ol>

                <h5 style="margin-top: 20px;">Metadata Searches</h5>Metadata search does not support phrases, but supports more sophisticated Boolean searching:
                <ol class="mt-2">
                    <li>plain tokens separated by spaces have an implied AND between them, but are treated as position-independent tokens.</li>Regexes are permitted, but will not span over the bounds of a token.
                    <li>quoted tokens must now match against the ENTIRE metadata string value in the database, including spaces and punctuations.</li>It will not match a single term within a larger string, no matter how precise. Regexes are permitted
                    <li>range allows for numeric and string ranges on all metadata fields.</li>
                    <li>
                        <span class="code-block">OR</span> can still be used to conjoin plain tokens, preceding the implied Boolean AND, as well
                        as quoted tokens.
                    </li>
                    <li>
                        <span class="code-block">NOT</span> is still available as both a filter, or a stand-alone negation:
                        <span
                            class="code-block"
                        >contrat NOT social</span> is legal, so is
                        <span class="code-block">NOT rousseau</span>
                    </li>
                </ol>

                <h5 style="margin-top: 20px;">Regexp syntax</h5>Basic regexp syntax, adapted from the
                <a
                    href="http://www.gnu.org/software/findutils/manual/html_node/find_html/egrep-regular-expression-syntax.html#egrep-regular-expression-syntax"
                >egrep regular expression syntax</a>:
                <ol class="mt-2">
                    <li>
                        The character
                        <span class="code-block">.</span> matches any single character except newline.
                    </li>
                    <li>
                        Bracket expressions can match sets or ranges of characters:
                        <span
                            class="code-block"
                        >[aeiou]</span> or
                        <span class="code-block">[a-z]</span>,
                        but will only match a single character unless followed by one of the quantifiers below.
                    </li>
                    <li>
                        <span class="code-block">*</span> indicates that the regular expression should match zero or more occurrences of the previous
                        character or bracketed group.
                    </li>
                    <li>
                        <span class="code-block">+</span> indicates that the regular expression should match one or more occurrences of the previous
                        character or bracketed group.
                    </li>
                    <li>
                        <span class="code-block">?</span> indicates that the regular expression should match zero or one occurrence of the previous
                        character or bracketed group.
                    </li>
                </ol>Thus,
                <span class="code-block">.*</span> is an approximate "match anything" wildcard operator, rather than the more traditional
                (but less precise)
                <span
                    class="code-block"
                >*</span> in many other search engines.
            </div>
        </b-modal>
    </b-container>
</template>

<script>
import { mapFields } from "vuex-map-fields";
import { EventBus } from "../main.js";

export default {
    name: "SearchForm",
    computed: {
        // When using nested data structures, the string
        // after the last dot (e.g. `firstName`) is used
        // for defining the name of the computed property.
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
            // "formData.metadataFields",
            "formData.start_date",
            "formData.end_date",
            "formData.year_interval",
            "formData.sort_by",
            "formData.results_per_page",
            "formData.start",
            "formData.end",
            "formData.byte",
            "searching"
        ]),
        formData() {
            return this.$store.state.formData;
        },
        sortValues() {
            let sortValues = [
                {
                    value: "rowid",
                    text: "select"
                }
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
                let localMetadataDisplay = this.copyObject(
                    this.metadataDisplay
                );
                localMetadataDisplay.splice(this.headIndex, 1);
                return localMetadataDisplay;
            }
        }
    },
    data() {
        return {
            dictionary: this.$philoConfig.dictionary,
            headIndex: 0,
            formOpen: false,
            searchOptionsButton: "Show search options",
            approximateValues: [50, 60, 70, 80, 90],
            methodOptions: [
                { text: "Within", value: "proxy" },
                { text: "Exactly", value: "phrase" },
                { text: "In the same sentence", value: "cooc" }
            ],
            metadataDisplay: [],
            metadataValues: {},
            collocationOptions: [
                { text: "Average TF-IDF", value: "tfidf" },
                { text: "Most Frequent Terms", value: "frequency" },
                { text: "Stopwords", value: "stopwords" },
                { text: "No Filtering", value: "nofilter" }
            ],
            selectedSortValues: "rowid",
            resultsPerPageOptions: [25, 100, 500, 1000],
            autoCompleteResults: { q: [] },
            arrowCounters: { q: -1 },
            isOpen: false,
            showTips: false
        };
    },
    created() {
        this.reports = this.buildReports();
        for (let metadataField of this.$philoConfig.metadata) {
            let metadataObj = {
                label: metadataField[0].toUpperCase() + metadataField.slice(1),
                value: metadataField,
                example: this.$philoConfig.search_examples[metadataField]
            };
            if (metadataField in this.$philoConfig.metadata_aliases) {
                metadataObj.label = this.$philoConfig.metadata_aliases[
                    metadataField
                ];
            }
            this.metadataDisplay.push(metadataObj);
            if (this.formData[metadataField] != "") {
                this.metadataValues[metadataField] = this.formData[
                    metadataField
                ];
            }
            this.$set(this.autoCompleteResults, metadataField, []);
            this.$set(this.arrowCounters, metadataField, -1);
            if (metadataField == "head") {
                this.headIndex = this.metadataDisplay.length - 1;
            }
        }
        EventBus.$on("metadataUpdate", metadata => {
            for (let field in metadata) {
                this.metadataValues[field] = metadata[field];
            }
            for (let metadataField of this.$philoConfig.metadata) {
                this.$set(this.autoCompleteResults, metadataField, []);
                this.$set(this.arrowCounters, metadataField, -1);
            }
        });
    },
    methods: {
        buildReports() {
            let reports = [];
            for (let value of this.$philoConfig.search_reports) {
                let label = value.replace("_s", "-s");
                label = label.charAt(0).toUpperCase() + label.slice(1);
                reports.push({
                    value: value,
                    label: label
                });
            }
            return reports;
        },
        buildMetadataFieldDisplay() {
            for (let metadataField of this.$philoConfig.metadata) {
                let metadataObj = {
                    label:
                        metadataField[0].toUpperCase() + metadataField.slice(1),
                    value: metadataField,
                    example: this.$philoConfig.search_examples[metadataField]
                };
                if (metadataField in this.$philoConfig.metadata_aliases) {
                    metadataObj.label = this.$philoConfig.metadata_aliases[
                        metadataField
                    ];
                }
                this.metadataValues[metadataField] = "";
                this.metadataDisplay.push(metadataObj);
            }
        },
        generateSortValues() {
            let sortValues = [
                {
                    value: ["rowid"],
                    label: "select"
                }
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
                sortValues.push({ label: label.join(", "), value: fields });
            }
            return sortValues;
        },
        onSubmit() {
            this.q = this.q.trim();
            if (this.q.length == 0) {
                this.report = "bibliography";
            }
            if (
                this.report == "textNavigation" ||
                this.report == "tableOfContents"
            ) {
                this.report = "concordance";
            }
            this.start = "";
            this.end = "";
            this.byte = "";
            this.formOpen = false;
            this.debug(this, this.$store.state.formData);
            this.$router.push(this.paramsToRoute(this.$store.state.formData));
        },
        onReset() {
            this.$store.commit(
                "setDefaultFields",
                this.$parent.defaultFieldValues
            );
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
            this.report = report;
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
            // Let's warn the parent that a change was made
            if (field == "q") {
                let currentQueryTerm = this.$route.query.q;
                if (this.q.length > 1 && this.q != currentQueryTerm) {
                    this.$http
                        .get(`${this.$dbUrl}/scripts/autocomplete_term.py`, {
                            params: { term: this.q }
                        })
                        .then(response => {
                            this.autoCompleteResults.q = response.data;
                            this.isLoading = false;
                        });
                }
            } else {
                this.$store.commit("updateFormDataField", {
                    key: field,
                    value: this.metadataValues[field]
                });
                let currentFieldValue = this.$route.query[field];
                if (
                    this.metadataValues[field].length > 1 &&
                    this.metadataValues[field] != currentFieldValue
                ) {
                    this.$http
                        .get(
                            `${this.$dbUrl}/scripts/autocomplete_metadata.py`,
                            {
                                params: {
                                    term: this.metadataValues[field],
                                    field: field
                                }
                            }
                        )
                        .then(response => {
                            this.autoCompleteResults[field] = response.data;
                        })
                        .catch(error => {
                            this.debug(this, error);
                        });
                }
            }
            let popup = document.querySelector(`#autocomplete-${field}`);
            const clearAutocomplete = e => {
                if (e.target !== popup) {
                    this.autoCompleteResults[field] = [];
                }
                window.removeEventListener("click", clearAutocomplete);
            };
            window.addEventListener("click", clearAutocomplete);
        },
        onArrowDown(field) {
            console.log(field);
            if (
                this.arrowCounters[field] <
                this.autoCompleteResults[field].length
            ) {
                this.arrowCounters[field] = this.arrowCounters[field] + 1;
            }
            if (this.arrowCounters[field] > 5) {
                let container = document.getElementById(
                    `autocomplete-${field}`
                );
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
            let result = this.autoCompleteResults[field][
                this.arrowCounters[field]
            ];
            this.setResult(result, field);
        },
        handleClickOutside(evt) {
            if (!this.$el.contains(evt.target)) {
                this.isOpen = false;
                for (let field in this.arrowCounters) {
                    this.arrowCounters[field] = 0;
                }
            }
        },
        setResult(result, field) {
            if (typeof result != "undefined") {
                let update = {};
                if (result.startsWith('"')) {
                    result = result.slice(1);
                }
                if (result.endsWith('"')) {
                    result = result.slice(0, result.length - 1);
                }
                let selected = `"${result.replace(/<[^>]+>/g, "")}"`;
                update[field] = selected;
                if (field == "q") {
                    this.q = selected;
                } else {
                    this.metadataValues[field] = selected;
                    this.$store.commit("updateFormDataField", {
                        key: field,
                        value: selected
                    });
                }
            }
            this.autoCompleteResults[field] = [];
            this.arrowCounters[field] = 0;
        },
        autoCompletePosition(field) {
            let parent = document.getElementById(`${field}-group`);
            let input = parent.querySelector("input");
            let childOffset = input.offsetLeft - parent.offsetLeft;
            return `left: ${childOffset}px; width: ${input.offsetWidth}px`;
        }
    }
};
</script>

<style scoped>
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

#method,
.metadata_fields.row,
#time_series_num.row,
#date_range.row,
#results_per_page.row,
#collocation-options > div,
#time-series-options > div {
    padding-top: 10px;
    padding-bottom: 10px;
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

@media (max-width: 768px) {
    #collocation-options .row {
        margin-left: -15px;
    }
}

/*Dico layout changes*/

#search_elements {
    border-top-width: 0px;
}

/*Responsiveness*/

@media (min-width: 1201px) {
    #initial-form,
    #search-elements {
        /* left: 100px; */
        right: 100px;
    }
}

@media (max-width: 1200px) {
    #initial-form,
    #search-elements {
        /* left: 70px; */
        right: 70px;
    }
}

@media (max-width: 992px) {
    #search-buttons {
        padding-top: 15px;
    }
    #search_terms > div:nth-of-type(2),
    #head-search-container .metadata_fields div:nth-of-type(2) {
        padding-right: 20px;
        padding-left: 20px;
    }
    #head-search-container #metadata-fields #initial-form,
    #search-elements {
        /* left: 40px; */
        right: 40px;
    }
    #philologic_response {
        margin-top: 170px;
    }
    #search-elements {
        margin-top: 148px;
    }
    #search-elements.dico {
        margin-top: 217px;
    }
    .dico-margin {
        margin-top: 245px !important;
    }
}

@media (max-width: 768px) {
    #right-act-on-report .btn-group {
        float: left !important;
    }
    #search-elements {
        padding-right: 20px;
        margin-top: 160px;
    }
    #search-elements.dico {
        margin-top: 248px;
    }
    #philologic_response {
        margin-top: 180px;
    }
    #initial-form,
    #search-elements {
        left: 0px;
        right: 0px;
    }
    #kwic,
    #time_series {
        display: none;
    }
    .dico-margin {
        margin-top: 270px !important;
    }
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
li {
    list-style-type: disc;
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