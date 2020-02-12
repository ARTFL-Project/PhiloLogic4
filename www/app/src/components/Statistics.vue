<template>
    <b-container fluid class="mt-4">
        <conckwic v-if="description.end != 0" :results="statisticsResults"></conckwic>
        <b-card no-body class="shadow mt-4 ml-4 mr-4">
            <b-list-group flush>
                <b-list-group-item
                    v-for="(result, resultIndex) in statisticsResults.slice(start, end)"
                    :key="resultIndex"
                >
                    <b-button
                        variant="outline-secondary"
                        size="sm"
                        class="d-inline-block"
                        :id="`button-${resultIndex}`"
                        @click="toggleBreakUp(resultIndex)"
                        v-if="result.break_up_field"
                    >&plus;</b-button>
                    <citations
                        :citation="buildCitationObject(groupedByField, statsConfig.field_citation, result.metadata_fields)"
                    ></citations>
                    : {{result.count}} occurrence(s)
                    <b-list-group class="ml-4" v-if="breakUpFields[resultIndex].show">
                        <b-list-group-item
                            v-for="(value, key) in breakUpFields[resultIndex].results"
                            :key="key"
                        >
                            {{ value.count }}:
                            <citations
                                :citation="buildCitationObject(statsConfig.break_up_field, statsConfig.break_up_field_citation, value.metadata_fields)"
                            ></citations>
                        </b-list-group-item>
                    </b-list-group>
                </b-list-group-item>
            </b-list-group>
        </b-card>
        <pages></pages>
    </b-container>
</template>
<script>
import { mapFields } from "vuex-map-fields";
import citations from "./Citations";
import searchArguments from "./SearchArguments";
import { EventBus } from "../main.js";
import pages from "./Pages";
import conckwic from "./ConcordanceKwic";

export default {
    name: "statistics",
    components: { citations, searchArguments, pages, conckwic },
    computed: {
        ...mapFields([
            "formData.report",
            "formData.q",
            "formData.results_per_page",
            "formData.start",
            "formData.end",
            "description",
            "resultsLength",
            "statisticsCache"
        ]),
        statsConfig() {
            for (let fieldObject of this.$philoConfig.stats_report_config
                .fields) {
                if (fieldObject.field == this.$route.query.group_by) {
                    return fieldObject;
                }
            }
        }
    },
    data() {
        return {
            results: [],
            loading: false,
            statisticsResults: [],
            groupedByField: this.$route.query.group_by,
            breakUpFields: []
        };
    },
    created() {
        this.report = "statistics";
        this.fetchData();
    },
    watch: {
        // call again the method if the route changes
        $route: "fetchData"
    },
    methods: {
        fetchData() {
            this.searching = true;
            if (
                this.deepEqual(
                    { ...this.statisticsCache.query, start: "", end: "" },
                    { ...this.$route.query, start: "", end: "" }
                )
            ) {
                this.statisticsResults = this.statisticsCache.results;
                this.breakUpFields = this.statisticsResults
                    .slice(this.start, this.end)
                    .map(results => ({
                        show: false,
                        results: results.break_up_field
                    }));
                this.resultsLength = this.statisticsResults.length;
                this.$store.commit("updateDescription", {
                    ...this.description,
                    start: this.start,
                    end: this.end,
                    results_per_page: this.results_per_page
                });
                EventBus.$emit("totalResultsDone");
            } else {
                if (isNaN(this.start) || this.start == "") {
                    this.start = 1;
                    this.end = parseInt(this.results_per_page);
                }
                if (isNaN(this.end) || this.end == "") {
                    this.end = 25;
                }
                this.$http
                    .get(`${this.$dbUrl}/reports/statistics.py`, {
                        params: this.paramsFilter({
                            ...this.$store.state.formData
                        })
                    })
                    .then(response => {
                        this.statisticsResults = response.data.results;
                        this.breakUpFields = this.statisticsResults
                            .slice(this.start, this.end)
                            .map(results => ({
                                show: false,
                                results: results.break_up_field
                            }));
                        this.resultsLength = this.statisticsResults.length;
                        this.$store.commit("updateDescription", {
                            ...this.description,
                            start: this.start,
                            end: this.end,
                            results_per_page: this.results_per_page
                        });
                        this.searching = false;
                        this.statisticsCache = {
                            results: response.data.results,
                            query: this.$route.query,
                            totalResults: response.data.results.total_results
                        };
                        EventBus.$emit("totalResultsDone");
                    })
                    .catch(error => {
                        this.searching = false;
                        this.debug(this, error);
                    });
            }
        },
        buildCitationObject(fieldToLink, citationObject, metadataFields) {
            let citations = [];
            for (let citation of citationObject) {
                let label = metadataFields[citation.field];
                if (label == null || label.length == 0) {
                    if (citation["field"] != fieldToLink) {
                        continue;
                    }
                }
                if (citation["field"] == fieldToLink) {
                    let queryParams = {
                        ...this.$store.state.formData,
                        start: "0",
                        end: "25"
                    };

                    if (label == null || label.length == 0) {
                        queryParams[fieldToLink] = "NULL";
                        label = "N/A";
                    } else {
                        queryParams[fieldToLink] = `"${label}"`;
                    }
                    let link = this.paramsToRoute({
                        ...queryParams,
                        report: "concordance"
                    });
                    citations.push({ ...citation, href: link, label: label });
                } else {
                    citations.push({ ...citation, href: "", label: label });
                }
            }
            return citations;
        },
        toggleBreakUp(resultIndex) {
            if (this.breakUpFields[resultIndex].show) {
                this.breakUpFields[resultIndex].show = false;
                document.getElementById(`button-${resultIndex}`).innerHTML =
                    "&plus;";
            } else {
                this.breakUpFields[resultIndex].show = true;
                document.getElementById(`button-${resultIndex}`).innerHTML =
                    "&minus;";
            }
        }
    }
};
</script>