<template>
    <b-container fluid class="mt-4">
        <conckwic :results="aggregationResults"></conckwic>
        <b-card no-body class="shadow mt-4 ml-4 mr-4">
            <b-list-group flush>
                <virtual-list :size="55" :remain="25">
                    <b-list-group-item
                        v-for="(result, resultIndex) in aggregationResults"
                        :key="resultIndex"
                        class="pt-3 pb-3"
                    >
                        <b-button
                            variant="outline-secondary"
                            size="sm"
                            class="d-inline-block"
                            style="padding: 0 0.25rem; margin-right: .5rem"
                            :id="`button-${resultIndex}`"
                            @click="toggleBreakUp(resultIndex)"
                            v-if="result.break_up_field.length > 0"
                        >&plus;</b-button>
                        <b-badge variant="secondary" pill style="font-size: 100%">{{ result.count }}</b-badge>
                        <citations :citation="result.citation"></citations>
                        <span
                            class="d-inline-block pl-1"
                            v-if="breakUpFields[resultIndex].results.length"
                        >across {{ breakUpFields[resultIndex].results.length }} {{ breakUpFieldName }}(s)</span>
                        <b-list-group class="ml-4" v-if="breakUpFields[resultIndex].show">
                            <b-list-group-item
                                v-for="(value, key) in breakUpFields[resultIndex].results"
                                :key="key"
                            >
                                <b-badge variant="secondary" pill>{{ value.count }}</b-badge>
                                <citations
                                    :citation="buildCitationObject(statsConfig.break_up_field, statsConfig.break_up_field_citation, value.metadata_fields)"
                                ></citations>
                            </b-list-group-item>
                        </b-list-group>
                    </b-list-group-item>
                </virtual-list>
            </b-list-group>
        </b-card>
    </b-container>
</template>
<script>
import { mapFields } from "vuex-map-fields";
import citations from "./Citations";
import searchArguments from "./SearchArguments";
import conckwic from "./ConcordanceKwic";
import virtualList from "vue-virtual-scroll-list";

export default {
    name: "aggregation",
    components: { citations, searchArguments, conckwic, virtualList },
    computed: {
        ...mapFields([
            "formData.report",
            "resultsLength",
            "aggregationCache",
            "searching",
            "currentReport"
        ]),
        statsConfig() {
            for (let fieldObject of this.$philoConfig.stats_report_config) {
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
            aggregationResults: [],
            groupedByField: this.$route.query.group_by,
            breakUpFields: [],
            breakUpFieldName: ""
        };
    },
    created() {
        this.report = "aggregation";
        this.currentReport = "aggregation";
        this.fetchData();
    },
    watch: {
        // call again the method if the route changes
        $route: "fetchData"
    },
    methods: {
        fetchData() {
            if (
                this.deepEqual(
                    { ...this.aggregationCache.query, start: "", end: "" },
                    { ...this.$route.query, start: "", end: "" }
                )
            ) {
                this.aggregationResults = this.aggregationCache.results;
                this.breakUpFields = this.aggregationResults.map(results => ({
                    show: false,
                    results: results.break_up_field
                }));
                this.resultsLength = this.aggregationCache.totalResults;
            } else {
                this.searching = true;
                this.$http
                    .get(`${this.$dbUrl}/reports/aggregation.py`, {
                        params: this.paramsFilter({
                            ...this.$store.state.formData
                        })
                    })
                    .then(response => {
                        this.aggregationResults = this.buildStatResults(
                            response.data.results
                        );
                        this.breakUpFields = this.aggregationResults.map(
                            results => ({
                                show: false,
                                results: results.break_up_field
                            })
                        );
                        this.breakUpFieldName = response.data.break_up_field;
                        this.resultsLength = response.data.total_results;
                        this.searching = false;
                        this.aggregationCache = {
                            results: response.data.results,
                            query: this.$route.query,
                            totalResults: response.data.results.total_results
                        };
                    })
                    .catch(error => {
                        this.searching = false;
                        this.debug(this, error);
                    });
            }
        },
        buildStatResults(results) {
            let resultsWithCiteObject = [];
            for (let result of results) {
                result.citation = this.buildCitationObject(
                    this.groupedByField,
                    this.statsConfig.field_citation,
                    result.metadata_fields
                );
                resultsWithCiteObject.push(result);
            }
            return resultsWithCiteObject;
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