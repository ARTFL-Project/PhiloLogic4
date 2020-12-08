<template>
    <div id="results-summary-container" class="mt-4 ml-2 mr-2">
        <b-card no-body class="shadow-sm px-3 py-2">
            <div id="initial_report">
                <div id="description">
                    <b-button variant="outline-primary" size="sm" id="export-results" v-b-modal.export-modal
                        >Export results</b-button
                    >
                    <b-modal id="export-modal" title="Export Results" hide-footer>
                        <export-results></export-results>
                    </b-modal>
                    <search-arguments :result-start="descriptionStart" :result-end="descriptionEnd"></search-arguments>
                    <div v-if="['concordance', 'kwic', 'bibliography'].includes(report)">
                        <div id="result-stats" class="pb-2">
                            {{ resultsLength }} total occurrences spread across
                            <div class="d-inline-block" style="position: relative" v-if="!hitlistStatsDone">
                                <b-spinner
                                    variant="secondary"
                                    style="position: absolute; width: 2rem; height: 2rem; z-index: 50; bottom: -0.75rem"
                                ></b-spinner>
                            </div>
                            <span v-if="hitlistStatsDone">
                                <span v-for="(stat, statIndex) in statsDescription" :key="stat.field">
                                    <router-link :to="`/aggregation?${stat.link}&group_by=${stat.field}`"
                                        >{{ stat.count }} {{ stat.label }}(s)</router-link
                                    >
                                    <span v-if="statIndex != statsDescription.length - 1">&nbsp;and&nbsp;</span>
                                </span>
                            </span>
                        </div>
                        <div id="search-hits">
                            <b v-if="resultsLength > 0"
                                >Displaying hits {{ descriptionStart }}-{{ descriptionEnd }} of {{ resultsLength }}</b
                            >
                            <b v-else>No results for your query</b>
                            <span v-if="report != 'bibliography'">
                                from these
                                <b-button
                                    pill
                                    size="sm"
                                    variant="outline-secondary"
                                    style="margin-top: -0.05rem"
                                    v-b-modal.results-bibliography
                                    >titles</b-button
                                >
                            </span>
                        </div>
                    </div>
                    <div v-if="report == 'aggregation'">
                        <div id="result-stats" class="pb-2" v-if="resultsLength > 0">
                            {{ resultsLength }} total occurrences spread across {{ aggregationCache.results.length }}
                            {{ groupByLabel.toLowerCase() }}(s)
                        </div>
                        <div id="result-stats" class="pb-2" v-else>
                            <b>No results for your query</b>
                        </div>
                    </div>
                    <div v-if="report == 'collocation'">
                        <b-progress
                            :max="resultsLength"
                            show-progress
                            variant="secondary"
                            class="ml-3 mr-3 mb-3"
                            v-if="runningTotal != resultsLength"
                        >
                            <b-progress-bar
                                :value="runningTotal"
                                :label="`${((runningTotal / resultsLength) * 100).toFixed(2)}%`"
                            ></b-progress-bar>
                        </b-progress>
                        <div>
                            <span>
                                <span tooltip tooltip-title="Click to display filtered words">
                                    The
                                    <a href @click="toggleFilterList()" v-if="colloc_filter_choice === 'frequency'"
                                        >{{ filter_frequency }} most common words</a
                                    >
                                    <a href @click="toggleFilterList()" v-if="colloc_filter_choice === 'stopwords'"
                                        >Common function words</a
                                    >
                                    <a href @click="toggleFilterList()" v-if="colloc_filter_choice === 'tfidf'"
                                        >{{ filter_frequency }} most highly weighted terms across the corpus</a
                                    >
                                    are being filtered from this report.
                                </span>
                            </span>
                            <b-card no-body id="filter-list" class="pl-3 pr-3 pb-3 shadow-lg" v-if="showFilteredWords">
                                <b-button id="close-filter-list" @click="toggleFilterList()"> &times; </b-button>
                                <b-row class="mt-4">
                                    <b-col v-for="wordGroup in splittedFilterList" :key="wordGroup[0]">
                                        <b-list-group flush>
                                            <b-list-group-item v-for="word in wordGroup" :key="word">{{
                                                word
                                            }}</b-list-group-item>
                                        </b-list-group>
                                    </b-col>
                                </b-row>
                            </b-card>
                        </div>
                    </div>
                    <div v-if="report == 'time_series'">
                        <b-progress
                            :max="resultsLength"
                            show-progress
                            variant="secondary"
                            class="ml-3 mr-3 mb-3"
                            v-if="runningTotal != resultsLength"
                        >
                            <b-progress-bar
                                :value="runningTotal"
                                :label="`${((runningTotal / resultsLength) * 100).toFixed(2)}%`"
                            ></b-progress-bar>
                        </b-progress>
                        {{ this.runningTotal }} {{ this.resultsLength }}
                    </div>
                </div>
                <b-button
                    variant="outline-secondary"
                    v-if="!showFacetedBrowsing && facets.length < 1"
                    @click="showFacets()"
                    >Show Facets</b-button
                >
            </div>
            <b-modal size="xl" scrollable hide-footer title="Results Bibliography" id="results-bibliography">
                <results-bibliography :results="results"></results-bibliography>
            </b-modal>
        </b-card>
        <b-row class="d-xs-none mt-4 mb-3" id="act-on-report" v-if="report == 'concordance' || report == 'kwic'">
            <b-col sm="7" lg="8" v-if="['concordance', 'kwic'].includes(report)">
                <b-button-group id="report_switch">
                    <b-button :class="{ active: report === 'concordance' }" @click="switchReport('concordance')">
                        <span class="d-xs-none d-sm-none d-md-inline">{{ reportSwitch.concordance.labelBig }}</span>
                        <span class="d-xs-inline d-sm-inline d-md-none">{{ reportSwitch.concordance.labelSmall }}</span>
                    </b-button>
                    <b-button :class="{ active: report === 'kwic' }" @click="switchReport('kwic')">
                        <span class="d-xs-none d-sm-none d-md-inline">{{ reportSwitch.kwic.labelBig }}</span>
                        <span class="d-xs-inline d-sm-inline d-md-none">{{ reportSwitch.kwic.labelSmall }}</span>
                    </b-button>
                </b-button-group>
            </b-col>
        </b-row>
    </div>
</template>

<script>
import searchArguments from "./SearchArguments";
import ResultsBibliography from "./ResultsBibliography";
import ExportResults from "./ExportResults";
import { EventBus } from "../main.js";

import { mapFields } from "vuex-map-fields";

export default {
    name: "ResultsSummary",
    components: {
        searchArguments,
        ResultsBibliography,
        ExportResults,
    },
    props: ["results", "description", "runningTotal"],
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
        ]),
    },
    data() {
        return {
            facets: this.$philoConfig.facets,
            showFacetedBrowsing: false,
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
        };
    },
    created() {
        this.buildDescription();
        if (["concordance", "kwic", "bibliography"].includes(this.report)) {
            this.updateTotalResults();
            this.getHitListStats();
        }
        if (this.report == "time_series") {
            this.updateTotalResults();
        }
    },
    watch: {
        $route: "buildDescription",
    },
    methods: {
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
                start = this.description.start || 1;
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
        buildStatsDescription(stats) {
            let statsDescription = [];
            for (let stat of stats) {
                let label = "";
                if (stat.field in this.$philoConfig.metadata_aliases) {
                    label = this.$philoConfig.metadata_aliases[stat.field].toLowerCase();
                } else {
                    label = stat.field;
                }
                statsDescription.push({
                    label: label,
                    field: stat.field,
                    count: stat.count,
                    link: this.paramsToUrlString({
                        ...this.$store.state.formData,
                        report: "aggregation",
                        start: "",
                        end: "",
                        group_by: "",
                    }),
                });
            }
            return statsDescription;
        },
        updateTotalResults() {
            let params = { ...this.$store.state.formData };
            if (this.report == "time_series") {
                params.year = `${this.start_date || this.$philoConfig.time_series_start_end_date.start_date}-${
                    this.end_date || this.$philoConfig.time_series_start_end_date.end_date
                }`;
            }
            this.$http
                .get(`${this.$dbUrl}/scripts/get_total_results.py`, {
                    params: this.paramsFilter(params),
                })
                .then((response) => {
                    this.resultsLength = response.data;
                    this.hits = this.buildDescription();
                    EventBus.$emit("totalResultsDone");
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
                    this.statsDescription = this.buildStatsDescription(response.data.stats);
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
</style>