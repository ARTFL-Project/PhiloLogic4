<template>
    <div class="container-fluid mt-4">
        <results-summary :results="aggregationResults"></results-summary>
        <div class="card shadow mt-4 ms-2 me-2" v-if="resultsLength">
            <div class="list-group" flush>
                <div
                    class="list-group-item pt-3 pb-3"
                    v-for="(result, resultIndex) in aggregationResults.slice(0, lastResult)"
                    :key="resultIndex"
                >
                    <button
                        type="button"
                        class="btn btn-outline-secondary btn-sm d-inline-block"
                        style="padding: 0 0.25rem; margin-right: 0.5rem"
                        :id="`button-${resultIndex}`"
                        @click="toggleBreakUp(resultIndex)"
                        v-if="result.break_up_field.length > 0"
                    >
                        &plus;
                    </button>
                    <span class="badge rounded-pill bg-secondary" style="font-size: 100%">{{ result.count }}</span>
                    <citations :citation="result.citation"></citations>
                    <span class="d-inline-block ps-1" v-if="breakUpFields[resultIndex].results.length"
                        >across {{ breakUpFields[resultIndex].results.length }} {{ breakUpFieldName }}(s)</span
                    >
                    <div class="list-group ms-4 mt-2" v-if="breakUpFields[resultIndex].show">
                        <div
                            class="list-group-item"
                            v-for="(value, key) in breakUpFields[resultIndex].results"
                            :key="key"
                        >
                            <span class="badge rounded-pill bg-secondary">{{ value.count }}</span>
                            <citations
                                :citation="
                                    buildCitationObject(
                                        statsConfig.break_up_field,
                                        statsConfig.break_up_field_citation,
                                        value.metadata_fields
                                    )
                                "
                            ></citations>
                        </div>
                    </div>
                </div>
                <infinite-loading :identifier="infiniteId" @infinite="infiniteHandler">
                    <div slot="no-more"></div>
                    <div slot="no-results"></div>
                </infinite-loading>
            </div>
        </div>
    </div>
</template>
<script>
import { mapFields } from "vuex-map-fields";
import citations from "./Citations";
import ResultsSummary from "./ResultsSummary";
import InfiniteLoading from "vue-infinite-loading";

export default {
    name: "aggregation",
    components: { citations, ResultsSummary, InfiniteLoading },
    computed: {
        ...mapFields(["formData.report", "resultsLength", "aggregationCache", "searching", "currentReport"]),
        statsConfig() {
            for (let fieldObject of this.$philoConfig.stats_report_config) {
                if (fieldObject.field == this.$route.query.group_by) {
                    return fieldObject;
                }
            }
            return null;
        },
    },
    data() {
        return {
            results: [],
            loading: false,
            aggregationResults: [],
            lastResult: 50,
            infiniteId: 0,
            groupedByField: this.$route.query.group_by,
            breakUpFields: [],
            breakUpFieldName: "",
        };
    },
    created() {
        this.report = "aggregation";
        this.currentReport = "aggregation";
        this.fetchData();
    },
    watch: {
        // call again the method if the route changes
        $route: "fetchData",
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
                this.breakUpFields = this.aggregationResults.map((results) => ({
                    show: false,
                    results: results.break_up_field,
                }));
                this.resultsLength = this.aggregationCache.totalResults;
            } else {
                this.searching = true;
                this.$http
                    .get(`${this.$dbUrl}/reports/aggregation.py`, {
                        params: this.paramsFilter({
                            ...this.$store.state.formData,
                        }),
                    })
                    .then((response) => {
                        this.infiniteId += 1;
                        this.aggregationResults = Object.freeze(this.buildStatResults(response.data.results));
                        this.lastResult = 50;
                        this.breakUpFields = this.aggregationResults.map((results) => ({
                            show: false,
                            results: results.break_up_field,
                        }));
                        this.breakUpFieldName =
                            this.$philoConfig.metadata_aliases[response.data.break_up_field] ||
                            response.data.break_up_field;
                        if (typeof this.breakUpFieldName != "undefined" || this.breakUpFieldName != null) {
                            this.breakUpFieldName = this.breakUpFieldName.toLowerCase();
                        }
                        this.resultsLength = response.data.total_results;
                        this.searching = false;
                    })
                    .catch((error) => {
                        this.searching = false;
                        this.debug(this, error);
                    });
            }
        },
        infiniteHandler($state) {
            if (this.aggregationResults.length > this.lastResult) {
                this.lastResult += 50;
                $state.loaded();
            } else {
                $state.complete();
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
                        end: "25",
                    };

                    if (label == null || label.length == 0) {
                        queryParams[fieldToLink] = "NULL";
                        label = "N/A";
                    } else {
                        queryParams[fieldToLink] = `"${label}"`;
                    }
                    let link = this.paramsToRoute({
                        ...queryParams,
                        report: "concordance",
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
                document.getElementById(`button-${resultIndex}`).innerHTML = "&plus;";
            } else {
                this.breakUpFields[resultIndex].show = true;
                document.getElementById(`button-${resultIndex}`).innerHTML = "&minus;";
            }
        },
    },
};
</script>
<style scoped>
#description {
    position: relative;
}
#export-results {
    position: absolute;
    right: 0;
    padding: 0.125rem 0.25rem;
    font-size: 0.8rem !important;
}
</style>