<template>
    <div id="concordanceKwic-container" class="mt-4 ml-4 mr-4">
        <div id="philo-view" v-if="authorized">
            <b-card no-body class="shadow-sm">
                <div id="initial_report">
                    <div
                        id="description"
                        v-if="typeof(results) != 'undefined'"
                        class="pb-3 velocity-opposites-transition-fadeIn"
                    >
                        <b-button
                            variant="outline-primary"
                            size="sm"
                            id="export-results"
                            data-target="#export-dialog"
                        >Export results</b-button>
                        <search-arguments></search-arguments>
                        <div id="search-hits" class="pl-3">{{ hits }}</div>
                    </div>
                    <button
                        type="button"
                        class="btn btn-primary pull-right hidden-xs"
                        style="margin-top: -33px; margin-right: 15px;"
                        v-if="!showFacetedBrowsing && philoConfig.facets.length < 1"
                        @click="showFacets() "
                    >Show Facets</button>
                </div>
            </b-card>
            <b-row class="d-xs-none mt-4" id="act-on-report">
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
    props: ["results"],
    computed: {
        ...mapFields([
            "formData.report",
            "formData.results_per_page",
            "formData.first_kwic_sorting_option",
            "formData.second_kwic_sorting_option",
            "formData.third_kwic_sorting_option",
            "resultsLength"
        ])
    },
    data() {
        return {
            philoConfig: this.$philoConfig,
            showFacetedBrowsing: false,
            authorized: true,
            hits: 0,
            start: 0,
            end: 0,
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
        this.resultsLength = this.results.results_length;
        this.hits = this.buildDescription();
        this.updateTotalResults();
        var vm = this;
        EventBus.$on("urlUpdate", function() {
            vm.hits = vm.buildDescription();
        });
    },
    methods: {
        buildDescription() {
            let start = this.results.description.start;
            let end = this.results.description.end;
            let resultsPerPage = this.results.description.results_per_page;
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
            var vm = this;
            this.$http
                .get(
                    "http://anomander.uchicago.edu/philologic/frantext0917/scripts/get_total_results.py",
                    {
                        params: this.paramsFilter(this.$store.state.formData)
                    }
                )
                .then(function(response) {
                    vm.resultsLength = response.data;
                    vm.hits = vm.buildDescription();
                    EventBus.$emit("totalResultsDone");
                })
                .catch(function(error) {
                    console.log(error);
                });
        },
        switchReport(reportName) {
            this.report = reportName;
            this.first_kwic_sorting_option = "";
            this.second_kwic_sorting_option = "";
            this.third_kwic_sorting_option = "";
            this.results_per_page = 25;
            this.$router.push(this.paramsToRoute(this.$store.state.formData));
            EventBus.$emit("urlUpdate");
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