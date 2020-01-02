<template>
    <div id="concordanceKwic-container" class="mt-4 ml-4 mr-4">
        <b-card no-body class="shadow-sm pb-3">
            <div id="initial_report">
                <div id="description">
                    <b-button
                        variant="outline-primary"
                        size="sm"
                        id="export-results"
                        v-b-modal.export-modal
                    >Export results</b-button>
                    <b-modal id="export-modal" title="Export Results" hide-footer>
                        <export-results></export-results>
                    </b-modal>
                    <search-arguments></search-arguments>
                    <div id="result-stats" class="pl-3 pb-3">
                        {{ resultsLength }} total occurrences spread across
                        <span
                            v-for="(stat, statIndex) in statsDescription"
                            :key="stat.field"
                        >
                            <router-link
                                :to="`/statistics?${stat.link}&group_by=${stat.field}`"
                            >{{stat.count}} {{stat.label}}(s)</router-link>
                            <span v-if="statIndex != statsDescription.length-1">&nbsp;and&nbsp;</span>
                        </span>
                    </div>
                    <div id="search-hits" class="pl-3">
                        <b>{{ hits }}</b>
                        <span v-if="report != 'bibliography'">
                            from these
                            <b-button
                                pill
                                size="sm"
                                variant="outline-secondary"
                                style="margin-top: -.05rem;"
                                @click="showResultsBiblio"
                            >titles</b-button>
                        </span>
                    </div>
                </div>
                <b-button
                    variant="outline-secondary"
                    v-if="!showFacetedBrowsing && facets.length < 1"
                    @click="showFacets() "
                >Show Facets</b-button>
            </div>
            <results-bibliography :results="results" v-if="showBiblio && resultsLength > 0"></results-bibliography>
        </b-card>
        <b-row class="d-xs-none mt-4 mb-3" id="act-on-report">
            <b-col sm="7" lg="8" v-if="report != 'bibliography'">
                <b-button-group id="report_switch">
                    <b-button
                        :class="{'active':  report === 'concordance'}"
                        @click="switchReport('concordance')"
                    >
                        <span
                            class="d-xs-none d-sm-none d-md-inline"
                        >{{ reportSwitch.concordance.labelBig }}</span>
                        <span
                            class="d-xs-inline d-sm-inline d-md-none"
                        >{{ reportSwitch.concordance.labelSmall }}</span>
                    </b-button>
                    <b-button :class="{'active':  report === 'kwic'}" @click="switchReport('kwic')">
                        <span
                            class="d-xs-none d-sm-none d-md-inline"
                        >{{ reportSwitch.kwic.labelBig }}</span>
                        <span
                            class="d-xs-inline d-sm-inline d-md-none"
                        >{{ reportSwitch.kwic.labelSmall }}</span>
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
    name: "conckwic",
    components: {
        searchArguments,
        ResultsBibliography,
        ExportResults
    },
    props: ["results"],
    computed: {
        ...mapFields([
            "formData.report",
            "formData.results_per_page",
            "formData.first_kwic_sorting_option",
            "formData.second_kwic_sorting_option",
            "formData.third_kwic_sorting_option",
            "resultsLength",
            "description"
        ])
    },
    data() {
        return {
            facets: this.$philoConfig.facets,
            showFacetedBrowsing: false,
            hits: "",
            statsDescription: [],
            resultsPerPage: 0,
            reportSwitch: {
                concordance: {
                    labelBig: "View occurrences with context",
                    labelSmall: "Concordance"
                },
                kwic: {
                    labelBig: "View occurrences line by line (KWIC)",
                    labelSmall: "Keyword in context"
                }
            },
            showBiblio: false
        };
    },
    created() {
        this.hits = this.buildDescription();
        this.updateTotalResults();
        EventBus.$on("resultsDone", () => {
            this.hits = this.buildDescription();
            this.updateTotalResults();
        });
    },
    beforeDestroy() {
        EventBus.$off("resultsDone");
    },
    methods: {
        buildDescription() {
            let start = this.description.start;
            let end = this.description.end;
            let resultsPerPage = this.description.results_per_page;
            let description;
            if (
                this.resultsLength &&
                end <= resultsPerPage &&
                end <= this.resultsLength
            ) {
                description =
                    "Displaying hits " +
                    start +
                    " - " +
                    end +
                    " of " +
                    this.resultsLength;
            } else if (this.resultsLength) {
                if (resultsPerPage > this.resultsLength) {
                    description =
                        "Displaying hits " +
                        start +
                        " - " +
                        this.resultsLength +
                        " of " +
                        this.resultsLength;
                } else {
                    description =
                        "Displaying hits " +
                        start +
                        " - " +
                        end +
                        " of " +
                        this.resultsLength;
                }
            } else {
                description = "No results for your query.";
            }
            return description;
        },
        buildStatsDescription(stats) {
            let statsDescription = [];
            for (let stat of stats) {
                let label = "";
                if (stat.field in this.$philoConfig.metadata_aliases) {
                    label = this.$philoConfig.metadata_aliases[
                        stat.field
                    ].toLowerCase();
                } else {
                    label = stat.field;
                }
                statsDescription.push({
                    label: label,
                    field: stat.field,
                    count: stat.count,
                    link: this.paramsToUrlString({
                        ...this.$store.state.formData,
                        report: "statistics"
                    })
                });
            }
            return statsDescription;
        },
        updateTotalResults() {
            this.$http
                .get(`${this.$dbUrl}/scripts/get_hitlist_stats.py`, {
                    params: this.paramsFilter(this.$store.state.formData)
                })
                .then(response => {
                    this.resultsLength = response.data.total_results;
                    this.statsDescription = this.buildStatsDescription(
                        response.data.stats
                    );
                    this.hits = this.buildDescription();
                    EventBus.$emit("totalResultsDone");
                })
                .catch(error => {
                    this.debug(this, error);
                });
        },
        switchReport(reportName) {
            this.report = reportName;
            this.first_kwic_sorting_option = "";
            this.second_kwic_sorting_option = "";
            this.third_kwic_sorting_option = "";
            this.results_per_page = 25;
            this.$router.push(this.paramsToRoute(this.$store.state.formData));
        },
        showFacets() {},
        showResultsBiblio() {
            if (!this.showBiblio) {
                this.showBiblio = true;
            } else {
                this.showBiblio = false;
            }
        }
    }
};
</script>

<style this d>
#description {
    position: relative;
}
#export-results {
    position: absolute;
    right: 0;
}
</style>