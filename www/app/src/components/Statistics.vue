<template>
    <b-container fluid class="mt-4">
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
                </div>
            </div>
        </b-card>
        <b-card no-body class="shadow mt-4">
            <b-list-group flush>
                <b-list-group-item
                    v-for="(result, resultIndex) in statisticsResults.slice(description.start, description.end)"
                    :key="resultIndex"
                >
                    <b-button
                        variant="outline-secondary"
                        size="sm"
                        class="d-inline-block"
                        v-b-toggle="`break-up-${resultIndex}`"
                        v-if="result.break_up_field"
                    >+</b-button>
                    <citations
                        :citation="buildCitationObject(groupedByField, statsConfig.field_citation, result.metadata_fields)"
                    ></citations>
                    : {{result.count}} occurrence(s)
                    <b-collapse :id="`break-up-${resultIndex}`">
                        <b-list-group class="ml-4" v-if="result.break_up_field">
                            <b-list-group-item
                                v-for="(value, key) in result.break_up_field"
                                :key="key"
                            >
                                {{ value.count }}:
                                <citations
                                    :citation="buildCitationObject(statsConfig.break_up_field, statsConfig.break_up_field_citation, value.metadata_fields)"
                                ></citations>
                            </b-list-group-item>
                        </b-list-group>
                    </b-collapse>
                </b-list-group-item>
            </b-list-group>
        </b-card>
        <pages v-if="resultsLength > 0"></pages>
    </b-container>
</template>
<script>
import { mapFields } from "vuex-map-fields";
import citations from "./Citations";
import searchArguments from "./SearchArguments";
import { EventBus } from "../main.js";

export default {
    name: "statistics",
    components: { citations, searchArguments },
    computed: {
        ...mapFields([
            "formData.report",
            "formData.q",
            "formData.results_per_page",
            "resultsLength",
            "description",
            "statisticsResults"
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
            groupedByField: this.$route.query.group_by
        };
    },
    created() {
        this.report = "statistics";
        this.fetchData();
    },
    methods: {
        fetchData() {
            this.loading = true;
            this.$http
                .get(`${this.$dbUrl}/reports/statistics.py`, {
                    params: this.paramsFilter({ ...this.$store.state.formData })
                })
                .then(response => {
                    this.statisticsResults = response.data.results;
                    this.resultsLength = this.statisticsResults.length;
                    this.$store.commit("updateDescription", {
                        ...this.description,
                        start: 1,
                        end: 25,
                        results_per_page: this.results_per_page
                    });
                    this.searching = false;
                    EventBus.$emit("resultsDone");
                })
                .catch(error => {
                    this.loading = false;
                    this.debug(this, error);
                });
        },
        buildCitationObject(fieldToLink, citationObject, metadataFields) {
            let citations = [];
            for (let citation of citationObject) {
                let label = metadataFields[citation.field];
                if (label == null || label.length == 0) {
                    continue;
                }
                if (citation["field"] == fieldToLink) {
                    let queryParams = this.copyObject(
                        this.$store.state.formData
                    );
                    queryParams[fieldToLink] = `"${label}"`;
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
        }
    }
};
</script>