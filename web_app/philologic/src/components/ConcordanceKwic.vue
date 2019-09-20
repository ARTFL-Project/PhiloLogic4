<template>
    <div id="concordanceKwic-container" class="mt-4 ml-4 mr-4">
        <div v-if="authorized">
            <b-card no-body class="shadow-sm">
                <div id="initial_report">
                    <div id="description" class="pb-3">
                        <b-button
                            variant="outline-primary"
                            size="sm"
                            id="export-results"
                            data-target="#export-dialog"
                        >Export results</b-button>
                        <search-arguments></search-arguments>
                        <div id="search-hits" class="pl-3">{{ hits }}</div>
                    </div>
                    <b-button
                        variant="outline-secondary"
                        v-if="!showFacetedBrowsing && facets.length < 1"
                        @click="showFacets() "
                    >Show Facets</b-button>
                </div>
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
                        <b-button
                            :class="{'active':  report === 'kwic'}"
                            @click="switchReport('kwic')"
                        >
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
        <access-control v-if="!authorized"></access-control>
    </div>
</template>

<script>
import searchArguments from "./SearchArguments";
import { EventBus } from "../main.js";

import { mapFields } from "vuex-map-fields";

export default {
    name: "conckwic",
    components: {
        searchArguments
    },
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
            authorized: true,
            hits: 0,
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
            }
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
            var description;
            if (
                this.resultsLength &&
                end <= resultsPerPage &&
                end <= this.resultsLength
            ) {
                description =
                    "Hits " + start + " - " + end + " of " + this.resultsLength;
            } else if (this.resultsLength) {
                if (resultsPerPage > this.resultsLength) {
                    description =
                        "Hits " +
                        start +
                        " - " +
                        this.resultsLength +
                        " of " +
                        this.resultsLength;
                } else {
                    description =
                        "Hits " +
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
        updateTotalResults() {
            this.$http
                .get(
                    "http://anomander.uchicago.edu/philologic/frantext0917/scripts/get_total_results.py",
                    {
                        params: this.paramsFilter(this.$store.state.formData)
                    }
                )
                .then(response => {
                    this.resultsLength = response.data;
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
        showFacets() {}
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