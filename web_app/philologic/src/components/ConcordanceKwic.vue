<template>
    <div id="concordanceKwic-container" class="mt-4 ml-4 mr-4">
        <div id="philo-view" v-if="authorized">
            <b-card no-body>
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
                    <b-row class="hidden-xs" id="act-on-report">
                        <b-col sm="7" lg="8" v-if="report !== 'bibliography'">
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
                    <button
                        type="button"
                        class="btn btn-primary pull-right hidden-xs"
                        style="margin-top: -33px; margin-right: 15px;"
                        v-if="!showFacetedBrowsing && philoConfig.facets.length < 1"
                        @click=" showFacets() "
                    >Show Facets</button>
                </div>
            </b-card>
        </div>
        <access-control v-if="!authorized"></access-control>
    </div>
</template>

<script>
import searchArguments from "./SearchArguments"
import { EventBus } from "../main.js";

import { mapFields } from "vuex-map-fields";

export default {
    name: "conckwic",
    components: {
        searchArguments
    },
    props: [
        "results"
    ],
    computed: {
        ...mapFields([
            "formData.report"])
    },
    data() {
        return {
            philoConfig: this.$philoConfig,
            showFacetedBrowsing: false,
            authorized: true,
            hits: 0,
            resultsLength: 0,
            start: 0,
            end: 0,
            resultsPerPage: 0,
            reportSwitch: {
                concordance: {
                    labelBig: "View occurrences with context",
                    labelSmall: "Concordance",
                },
                kwic: {
                    labelBig: "View occurrences line by line (KWIC)",
                    labelSmall: "Keyword in context",
                }
            }
        };
    },
    created() {
        this.hits = this.buildDescription()
        var vm = this
        EventBus.$on("urlUpdate", function () {
            vm.buildDescription()
        })
    },
    methods: {
        buildDescription() {
            let resultsLength = this.results.results_length
            let start = this.results.description.start
            let end = this.results.description.end
            let resultsPerPage = this.results.description.results_per_page
            if (resultsLength && end <= resultsPerPage && end <= resultsLength) {
                var description = 'Hits ' + start + ' - ' + end + ' of ' + resultsLength
            } else if (resultsLength) {
                if (resultsPerPage > resultsLength) {
                    var description = 'Hits ' + start + ' - ' + resultsLength + ' of ' + resultsLength
                } else {
                    var description = 'Hits ' + start + ' - ' + end + ' of ' + resultsLength
                }
            } else {
                var description = 'No results for your query.'
            }
            return description
        },
        switchReport(reportName) {
            this.report = reportName
            this.$router.push(this.paramsToRoute(this.$store.state.formData))
            EventBus.$emit("urlUpdate")
        },
        showFacets() {

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