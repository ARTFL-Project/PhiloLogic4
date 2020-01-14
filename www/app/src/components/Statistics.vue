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
                <b-list-group-item v-for="result in results" :key="result.group_by_field">
                    <citations :citation="result.citation"></citations>
                    : {{result.count}} occurrences
                </b-list-group-item>
            </b-list-group>
        </b-card>
    </b-container>
</template>
<script>
import { mapFields } from "vuex-map-fields";
import citations from "./Citations";
import searchArguments from "./SearchArguments";

export default {
    name: "statistics",
    components: { citations, searchArguments },
    computed: {
        ...mapFields(["formData.report", "formData.q"])
    },
    data() {
        return {
            results: [],
            loading: false
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
                    this.results = response.data.results;
                })
                .catch(error => {
                    this.loading = false;
                    this.debug(this, error);
                });
        }
    }
};
</script>