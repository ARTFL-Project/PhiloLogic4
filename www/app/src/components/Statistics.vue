<template>
    <b-container fluid class="mt-4">
        <b-card no-body class="shadow">
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

export default {
    name: "statistics",
    components: { citations },
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
            console.log(
                this.$store.state.formData,
                this.paramsFilter({ ...this.$store.state.formData })
            );
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