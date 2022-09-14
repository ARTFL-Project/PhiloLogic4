<template>
    <div id="results-summary-container" class="mt-4 ms-2 me-2">
        <div class="card shadow-sm px-3 py-2">
            <div id="initial_report">
                <div id="description">
                    <button
                        type="button"
                        class="btn btn-secondary btn-sm"
                        style="margin-top: -0.5rem; margin-right: -1rem"
                        id="export-results"
                        data-bs-toggle="modal"
                        data-bs-target="#export-modal"
                    >
                        Export results
                    </button>
                    <div class="modal fade" tabindex="-1" id="export-modal" title="Export Results">
                        <export-results></export-results>
                    </div>
                    <search-arguments :result-start="descriptionStart" :result-end="descriptionEnd"></search-arguments>
                    <div v-if="['concordance', 'kwic', 'bibliography'].includes(report)">
                        <div id="result-stats" class="pb-2">
                            {{ resultsLength }} total occurrences
                            <span v-if="fieldSummary.length > 0">
                                spread across
                                <div class="d-inline-block" style="position: relative" v-if="!hitlistStatsDone">
                                    <div
                                        class="spinner-border text-secondary"
                                        role="status"
                                        style="
                                            position: absolute;
                                            width: 2rem;
                                            height: 2rem;
                                            z-index: 50;
                                            bottom: -0.75rem;
                                        "
                                    >
                                        <span class="visually-hidden">Loading...</span>
                                    </div>
                                </div>
                                <span v-if="hitlistStatsDone">
                                    <span v-for="(stat, statIndex) in statsDescription" :key="stat.field">
                                        <router-link
                                            :to="`/aggregation?${stat.link}&group_by=${stat.field}`"
                                            class="stat-link"
                                            v-if="stat.link.length > 0"
                                            >{{ stat.count }} {{ stat.label }}(s)</router-link
                                        >
                                        <span v-else>{{ stat.count }} {{ stat.label }}(s)</span>
                                        <span v-if="statIndex != statsDescription.length - 1">&nbsp;and&nbsp;</span>
                                    </span>
                                </span>
                            </span>
                        </div>
                        <div id="search-hits">
                            <b v-if="resultsLength > 0"
                                >Displaying hits {{ descriptionStart }}-{{ descriptionEnd }} of {{ resultsLength }}</b
                            >
                            <b v-else>No results for your query</b>
                            <span>
                                from these
                                <button
                                    type="button"
                                    class="btn rounded-pill btn-outline-secondary btn-sm"
                                    style="margin-top: -0.05rem"
                                    data-bs-toggle="modal"
                                    data-bs-target="#results-bibliography"
                                >
                                    titles
                                </button>
                            </span>
                        </div>
                        <div class="modal fade" tabindex="-1" id="results-bibliography">
                            <results-bibliography></results-bibliography>
                        </div>
                    </div>
                    <div v-if="report == 'aggregation' && groupByLabel">
                        <div id="result-stats" class="pb-2" v-if="resultsLength > 0">
                            {{ resultsLength }} total occurrences spread across {{ groupLength }}
                            {{ groupByLabel.toLowerCase() }}(s)
                        </div>
                        <div id="result-stats" class="pb-2" v-else>
                            <b>No results for your query</b>
                        </div>
                    </div>
                    <div v-if="['collocation', 'time_series'].includes(report)">
                        <div
                            class="progress ms-3 me-3 mb-3"
                            :max="resultsLength"
                            show-progress
                            variant="secondary"
                            v-if="runningTotal != resultsLength"
                        >
                            <div
                                class="progress-bar"
                                role="progressbar"
                                aria-valuemin="0"
                                aria-valuemax="100"
                                :style="`width: ${((runningTotal / resultsLength) * 100).toFixed(2)}%`"
                            >
                                {{ Math.floor((runningTotal / resultsLength) * 100) }}%
                            </div>
                        </div>
                        <div v-if="report == 'collocation'">
                            <span>
                                <span tooltip tooltip-title="Click to display filtered words">
                                    The
                                    <a
                                        href
                                        @click="toggleFilterList($event)"
                                        v-if="colloc_filter_choice === 'frequency'"
                                        >{{ filter_frequency }} most common words</a
                                    >
                                    <a
                                        href
                                        @click="toggleFilterList($event)"
                                        v-if="colloc_filter_choice === 'stopwords'"
                                        >most common function words</a
                                    >
                                    are being filtered from this report.
                                </span>
                            </span>
                            <div class="card ps-3 pe-3 pb-3 shadow-lg" id="filter-list" v-if="showFilteredWords">
                                <button
                                    type="button"
                                    class="btn btn-secondary"
                                    id="close-filter-list"
                                    @click="toggleFilterList($event)"
                                >
                                    &times;
                                </button>
                                <div class="row mt-4">
                                    <div class="col" v-for="wordGroup in splittedFilterList" :key="wordGroup[0]">
                                        <div class="list-group list-group-flush">
                                            <div class="list-group-item" v-for="word in wordGroup" :key="word">
                                                {{ word }}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div
            class="row d-none d-sm-block mt-4 mb-3"
            id="act-on-report"
            v-if="report == 'concordance' || report == 'kwic'"
        >
            <div class="col col-sm-7 col-lg-8" v-if="['concordance', 'kwic'].includes(report)">
                <div class="btn-group" role="group" id="report_switch">
                    <button
                        type="button"
                        class="btn btn-secondary"
                        :class="{ active: report === 'concordance' }"
                        @click="switchReport('concordance')"
                    >
                        <span class="d-none d-sm-none d-md-inline">{{ reportSwitch.concordance.labelBig }}</span>
                        <span class="d-inline d-sm-inline d-md-none">{{ reportSwitch.concordance.labelSmall }}</span>
                    </button>
                    <button
                        type="button"
                        class="btn btn-secondary"
                        :class="{ active: report === 'kwic' }"
                        @click="switchReport('kwic')"
                    >
                        <span class="d-none d-sm-none d-md-inline">{{ reportSwitch.kwic.labelBig }}</span>
                        <span class="d-inline d-sm-inline d-md-none">{{ reportSwitch.kwic.labelSmall }}</span>
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import searchArguments from "./SearchArguments";
import ResultsBibliography from "./ResultsBibliography";
import ExportResults from "./ExportResults";
import { Modal } from "bootstrap";

import { mapFields } from "vuex-map-fields";

export default {
    name: "ResultsSummary",
    components: {
        searchArguments,
        ResultsBibliography,
        ExportResults,
    },
    props: ["description", "runningTotal", "filterList", "groupLength"],
    computed: {
        ...mapFields([
            "formData.report",
            "formData.results_per_page",
            "formData.first_kwic_sorting_option",
            "formData.second_kwic_sorting_option",
            "formData.third_kwic_sorting_option",
            "formData.start",
            "formData.end",
            "formData.group_by",
            "formData.colloc_filter_choice",
            "formData.filter_frequency",
            "currentReport",
            "resultsLength",
            "aggregationCache",
            "totalResultsDone",
        ]),
        splittedFilterList: function () {
            let arrayLength = this.filterList.length;
            let chunkSize = arrayLength / 5;
            let splittedList = [];
            for (let index = 0; index < arrayLength; index += chunkSize) {
                let myChunk = this.filterList.slice(index, index + chunkSize);
                splittedList.push(myChunk);
            }
            return splittedList;
        },
    },
    inject: ["$http"],
    data() {
        return {
            facets: this.$philoConfig.facets,
            fieldSummary: this.$philoConfig.results_summary,
            hits: "",
            descriptionStart: 1,
            descriptionEnd: this.$store.state.formData.results_per_page,
            statsDescription: [],
            resultsPerPage: 0,
            hitlistStatsDone: false,
            reportSwitch: {
                concordance: {
                    labelBig: "View occurrences with context",
                    labelSmall: "Concordance",
                },
                kwic: {
                    labelBig: "View occurrences line by line (KWIC)",
                    labelSmall: "Keyword in context",
                },
            },
            showBiblio: false,
            groupByLabel:
                this.$route.query.group_by in this.$philoConfig.metadata_aliases
                    ? this.$philoConfig.metadata_aliases[this.$route.query.group_by]
                    : this.$route.query.group_by,
            showFilteredWords: false,
            currentQuery: {},
        };
    },
    created() {
        this.currentQuery = {
            ...this.$store.state.formData,
            start: "",
            end: "",
            first_kwic_sorting_option: "",
            second_kwic_sorting_option: "",
            third_kwic_sorting_option: "",
        };
        this.updateDescriptions();
    },
    watch: {
        $route: "updateDescriptions",
    },
    methods: {
        updateDescriptions() {
            let modalEl = document.getElementById("results-bibliography");
            if (modalEl) {
                // hide modal if open
                let modal = Modal.getOrCreateInstance(modalEl);
                modal.hide();
            }
            this.buildDescription();
            this.updateTotalResults();
            if (["concordance", "kwic", "bibliography"].includes(this.report)) {
                let newQuery = {
                    ...this.$store.state.formData,
                    start: "",
                    end: "",
                    first_kwic_sorting_option: "",
                    second_kwic_sorting_option: "",
                    third_kwic_sorting_option: "",
                };
                if (!this.deepEqual(newQuery, this.currentQuery) || Object.keys(this.statsDescription).length == 0) {
                    this.getHitListStats();
                    this.currentQuery = newQuery;
                }
            }
        },
        buildDescription() {
            let start;
            let end;
            if (
                typeof this.description == "undefined" ||
                this.description.start === "" ||
                this.description.start == 0
            ) {
                start = 1;
                end = parseInt(this.results_per_page);
            } else {
                start = this.description.start || this.$route.query.start || 1;
                end = this.end || parseInt(this.results_per_page);
            }
            if (end > this.resultsLength) {
                end = this.resultsLength;
            }
            let resultsPerPage = parseInt(this.results_per_page);
            let description;
            if (this.resultsLength && end <= resultsPerPage && end <= this.resultsLength) {
                this.descriptionStart = start;
                this.descriptionEnd = end;
            } else if (this.resultsLength) {
                if (resultsPerPage > this.resultsLength) {
                    this.descriptionStart = start;
                    this.descriptionEnd = this.resultsLength;
                } else {
                    this.descriptionStart = start;
                    this.descriptionEnd = end;
                }
            }
            return description;
        },
        updateTotalResults() {
            let params = { ...this.$store.state.formData };
            if (this.report == "time_series") {
                params.year = `${this.start_date || this.$philoConfig.time_series_start_end_date.start_date}-${
                    this.end_date || this.$philoConfig.time_series_start_end_date.end_date
                }`;
            }
            this.totalResultsDone = false;
            this.$http
                .get(`${this.$dbUrl}/scripts/get_total_results.py`, {
                    params: this.paramsFilter(params),
                })
                .then((response) => {
                    this.resultsLength = response.data;
                    this.hits = this.buildDescription();
                    this.totalResultsDone = true;
                })
                .catch((error) => {
                    this.debug(this, error);
                });
        },
        getHitListStats() {
            this.hitlistStatsDone = false;
            this.$http
                .get(`${this.$dbUrl}/scripts/get_hitlist_stats.py`, {
                    params: this.paramsFilter({ ...this.$store.state.formData }),
                })
                .then((response) => {
                    this.hitlistStatsDone = true;
                    let statsDescription = [];
                    for (let stat of response.data.stats) {
                        let label = "";
                        if (stat.field in this.$philoConfig.metadata_aliases) {
                            label = this.$philoConfig.metadata_aliases[stat.field].toLowerCase();
                        } else {
                            label = stat.field;
                        }
                        let link = "";
                        if (stat.link_field) {
                            link = this.paramsToUrlString({
                                ...this.$store.state.formData,
                                report: "aggregation",
                                start: "",
                                end: "",
                                group_by: "",
                            });
                            if (link.length == 0) {
                                link = "/aggregation?";
                            }
                        }
                        statsDescription.push({
                            label: label,
                            field: stat.field,
                            count: stat.count,
                            link: link,
                        });
                    }
                    this.statsDescription = statsDescription;
                })
                .catch((error) => {
                    this.debug(this, error);
                });
        },
        switchReport(reportName) {
            this.report = reportName;
            this.first_kwic_sorting_option = "";
            this.second_kwic_sorting_option = "";
            this.third_kwic_sorting_option = "";
            this.results_per_page = 25;
            this.$router.push(this.paramsToRoute({ ...this.$store.state.formData }));
        },
        showFacets() {},
        showResultsBiblio() {
            if (!this.showBiblio) {
                this.showBiblio = true;
            } else {
                this.showBiblio = false;
            }
        },
        toggleFilterList(event) {
            event.preventDefault();
            if (this.showFilteredWords == true) {
                this.showFilteredWords = false;
            } else {
                this.showFilteredWords = true;
            }
        },
    },
};
</script>

<style this d>
#description {
    position: relative;
}
#export-results {
    position: absolute;
    right: 0;
    padding: 0.125rem 0.25rem;
    font-size: 0.8rem !important;
}
#results-bibliography .modal-header {
    padding-bottom: 0.5rem;
}
#results-bibliography .modal-header button {
    padding: 0.5rem;
}
#results-bibliography .modal-header h5 {
    line-height: 1;
}
#close-filter-list {
    width: fit-content;
    float: right;
    padding: 0 0.2rem;
    position: absolute;
    right: 0;
}
#filter-list .list-group-item {
    border-width: 0px;
    padding: 0.1rem;
}
.stat-link {
    text-decoration: none;
}
</style>