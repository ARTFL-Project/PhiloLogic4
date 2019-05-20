<template>
    <div id="concordanceKwic-container" class="mt-4 ml-4 mr-4">
        <div id="philo-view" v-if="authorized">
            <b-card no-body>
                <div id="initial_report">
                    <div
                        id="description"
                        v-if="typeof(results) != 'undefined'"
                        class="velocity-opposites-transition-fadeIn"
                    >
                        <button
                            type="button"
                            id="export-results"
                            class="btn btn-default btn-xs pull-right hidden-xs"
                            data-toggle="modal"
                            data-target="#export-dialog"
                        >Export results</button>
                        <search-arguments></search-arguments>
                        <!--<results-description
                            description="{{ description }}"
                            query-status="{{ loading }}"
                        ></results-description>-->
                    </div>
                    <div class="row hidden-xs" id="act-on-report">
                        <!-- <concordance-kwic-switch
                            report="{{ report }}"
                            v-if="report !== 'bibliography'"
                        ></concordance-kwic-switch>-->
                    </div>
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
            authorized: true
        };
    },
    methods: {
        showFacets() {

        }
    }
};
</script>

<style scoped>
#description {
    position: relative;
}
#export-results {
    position: absolute;
    right: 0;
}
</style>