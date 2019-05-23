<template>
    <div id="facet-search" class="d-xs-none" loading="loading">
        <b-card
            no-body
            title="Title"
            header-tag="header"
            id="facet-panel-wrapper"
            class="shadow-sm"
        >
            <h6 slot="header" class="mb-0 text-center">
                Browse by facet
                <!-- <b-button class="close-box" @click="hideFacets()">x</b-button> -->
            </h6>
            <b-list-group flush id="select-facets" v-if="showFacetSelection">
                <span class="dropdown-header text-center">Frequency by</span>
                <b-list-group-item
                    v-for="facet in facets"
                    :key="facet.alias"
                    @click="getFacet(facet)"
                    class="facet-selection"
                >{{ facet.alias }}</b-list-group-item>
            </b-list-group>
            <hr v-if="showFacetSelection">
            <b-list-group flush v-if="showFacetSelection">
                <span class="dropdown-header text-center">Collocates of query term(s)</span>
                <b-list-group-item
                    @click="getFacet(collocationFacet)"
                    v-if="report !== 'bibliography'"
                    class="facet-selection"
                >{{ collocationFacet.alias }}</b-list-group-item>
            </b-list-group>
            <div
                class="m-2 text-center"
                style="width: 100%; font-size: 90%; opacity: 0.8; cursor: pointer"
                v-if="!showFacetSelection"
                @click="showFacetOptions()"
            >Show Options</div>
        </b-card>
        <b-card no-body id="facet-results" class="mt-3 shadow-sm" v-if="showFacetResults">
            <h6 slot="header" class="mb-0 text-center">
                <span>Frequency by {{selectedFacet.alias}}</span>
                <b-button
                    size="sm"
                    variant="outline-secondary"
                    class="close-box"
                    @click="hideFacets()"
                >x</b-button>
            </h6>
            <b-button-group
                id="frequency-selection"
                v-if="percent == 100 && report !== 'bibliography' && facet.type === 'facet'"
            >
                <b-button
                    size="sm"
                    :class="{'active': showingRelativeFrequencies === false}"
                    @click="displayAbsoluteFrequencies()"
                >Absolute Frequency</b-button>
                <b-button
                    size="sm"
                    :class="{'active': showingRelativeFrequencies}"
                    @click="displayRelativeFrequencies()"
                >Relative Frequency</b-button>
            </b-button-group>
            <div
                class="m-2 text-center"
                style="opacity: 0.5"
            >Top 500 results for {{ selectedFacet.alias }}</div>
            <!-- <progress-bar
                progress="{{ percent }}"
                class="velocity-opposites-transition-slideDownIn"
                data-velocity-opts="{duration:400}"
            ></progress-bar>-->
            <b-list-group flush>
                <b-list-group-item
                    v-for="result in facetResults"
                    :key="result.label"
                    @click="facetClick(result)"
                >
                    <b-row>
                        <b-col cols="8">
                            <span
                                class="sidebar-text text-content-area"
                                href
                                @click="facetClick(result.metadata)"
                                v-if="facet.facet !== 'all_collocates'"
                            >
                                <span>{{ result.label }}</span>
                            </span>
                            <span
                                class="sidebar-text text-content-area"
                                href
                                @click="collocationToConcordance(result.label)"
                                v-if="facet.facet === 'all_collocates'"
                            >
                                <span>{{ result.label }}</span>
                            </span>
                            <div
                                style="line-height: 70%; padding-bottom: 15px; font-size: 85%;"
                                v-if="showingRelativeFrequencies"
                            >
                                <div style="opacity: .8">
                                    {{ fullResults.unsorted[result.label].count }} actual {{ occurrence(fullResults.unsorted[result.label].count) }}
                                    in {{ fullRelativeFrequencies[result.label].total_count }} words
                                </div>
                            </div>
                        </b-col>
                        <b-col cols="4">
                            <span class="sidebar-count text-right">{{ result.count }}</span>
                        </b-col>
                    </b-row>
                </b-list-group-item>
            </b-list-group>
        </b-card>
    </div>
</template>
<script>
import { mapFields } from "vuex-map-fields";
import { EventBus } from "../main.js";

export default {
    name: "facets",
    computed: {
        ...mapFields([
            "formData.report",
            "formData.q",
            "formData.start",
            "formData.end",
            "formData.metadataFields"
        ])
    },
    data() {
        return {
            philoConfig: this.$philoConfig,
            facets: [],
            queryArgs: {},
            showFacetSelection: true,
            showFacetResults: false,
            collocationFacet: {
                facet: "all_collocates",
                alias: "in the same sentence",
                type: "collocationFacet"
            },
            percent: 0,
            percentComplete: 0,
            loading: false,
            moreResults: false,
            done: true,
            facet: {},
            selectedFacet: {},
            showingRelativeFrequencies: false,
            fullResults: {},
            relativeFrequencies: [],
            absoluteFrequencies: [],
            interrupt: false,
            selected: ""
        };
    },
    created() {
        this.facets = this.populateFacets();
        var vm = this;
        EventBus.$on("urlUpdate", function() {
            vm.facetResults = [];
            vm.fullResults = {};
            vm.showFacetSelection = true;
            vm.showFacetResults = false;
        });
    },
    methods: {
        populateFacets() {
            let facetConfig = this.philoConfig.facets;
            let facets = [];
            let alias;
            for (let i = 0; i < facetConfig.length; i++) {
                let facet = facetConfig[i];
                if (facet in this.philoConfig.metadata_aliases) {
                    alias = this.philoConfig.metadata_aliases[facet];
                } else {
                    alias = facet;
                }
                facets.push({
                    facet: facet,
                    alias: alias,
                    type: "facet"
                });
            }
            return facets;
        },
        getFacet(facetObj) {
            this.relativeFrequencies = [];
            this.absoluteFrequencies = [];
            this.showingRelativeFrequencies = false;
            this.facet = facetObj;
            this.selectedFacet = facetObj;
            this.selected = facetObj.alias;
            let urlString = this.paramsToUrlString({
                ...this.$store.state.formData,
                frequency_field: facetObj.alias
            });
            if (
                typeof sessionStorage[urlString] !== "undefined" &&
                this.philoConfig.production === true
            ) {
                this.loading = true;
                this.fullResults = JSON.parse(sessionStorage[urlString]);
                this.facetResults = this.fullResults.sorted.slice(0, 500);
                this.loading = false;
                this.percent = 100;
                this.showFacetResults = true;
                this.showFacetSelection = false;
            } else {
                // store the selected field to check whether to kill the ajax calls in populate_sidebar
                // document.querySelector('#select-facets').data('selected', facetObj.alias);
                // angular.element('#select-facets').data('interrupt', false);
                this.done = false;
                let fullResults = {};
                this.loading = true;
                this.moreResults = true;
                this.percent = 0;
                let queryParams = this.copyObject(this.$store.state.formData);
                if (facetObj.type === "facet") {
                    queryParams.frequency_field = facetObj.facet;
                } else if (facetObj.type === "collocationFacet") {
                    queryParams.report = "collocation";
                }
                var vm = this;
                this.populateSidebar(vm, facetObj, fullResults, 0, queryParams);
            }
        },
        populateSidebar(vm, facet, fullResults, start, queryParams) {
            if (vm.moreResults) {
                if (facet.type !== "collocationFacet") {
                    var promise = vm.$http.get(
                        "http://anomander.uchicago.edu/philologic/test/scripts/get_frequency.py",
                        {
                            params: vm.paramsFilter(queryParams)
                        }
                    );
                } else {
                    var promise = vm.$http.get(
                        "http://anomander.uchicago.edu/philologic/test/",
                        {
                            params: vm.paramsToRoute(queryParams)
                        }
                    );
                }
                vm.showFacetSelection = false;
                promise
                    .then(response => {
                        var results = response.data.results;
                        vm.moreResults = response.data.more_results;
                        vm.resultsLength = response.data.results_length;
                        if (!vm.interrupt && vm.selected == facet.alias) {
                            if (facet.type === "collocationFacet") {
                                var merge = vm.mergeResults(
                                    fullResults.unsorted,
                                    response.data.collocates
                                );
                            } else {
                                var merge = vm.mergeResults(
                                    fullResults.unsorted,
                                    results
                                );
                            }
                            vm.facetResults = merge.sorted.slice(0, 500);
                            vm.loading = false;
                            vm.showFacetResults = true;
                            fullResults = merge;
                            if (response.data.hits_done < vm.resultsLength) {
                                vm.percentComplete =
                                    (response.data.hits_done /
                                        vm.resultsLength) *
                                    100;
                                vm.percent = Math.floor(vm.percentComplete);
                            }
                            start = response.data.hits_done;
                            vm.populateSidebar(
                                vm,
                                facet,
                                fullResults,
                                start,
                                queryParams
                            );
                        } else {
                            // vm won't affect the full collocation report which can't be interrupted when on the page
                            vm.interrupt = false;
                        }
                    })
                    .catch(response => {
                        vm.loading = false;
                    });
            } else {
                vm.percent = 100;
                vm.fullResults = fullResults;
                let urlString = vm.paramsToUrlString({
                    ...queryParams,
                    frequency_field: vm.selectedFacet.alias
                });
                vm.saveToLocalStorage(urlString, fullResults);
            }
        },
        roundToTwo(num) {
            return +(Math.round(num + "e+2") + "e-2");
        },
        getRelativeFrequencies(hitsDone) {
            var relativeResults = {};
            for (var label in this.fullResults.unsorted) {
                var resultObj = this.fullResults.unsorted[label];
                relativeResults[label] = {
                    count: this.roundToTwo(
                        (resultObj.count / resultObj.total_word_count) * 10000
                    ),
                    url: resultObj.url,
                    label: label,
                    total_count: resultObj.total_word_count
                };
            }
            this.fullRelativeFrequencies = relativeResults;
            var sortedRelativeResults = this.sortResults(
                this.fullRelativeFrequencies
            );
            this.facetResults = this.copyObject(
                sortedRelativeResults.slice(0, 500)
            );
            this.showingRelativeFrequencies = true;
            this.loading = false;
            this.percent = 100;
        },
        displayRelativeFrequencies() {
            this.loading = true;
            if (this.relativeFrequencies.length == 0) {
                this.absoluteFrequencies = this.copyObject(this.facetResults);
                this.percent = 0;
                this.fullRelativeFrequencies = {};
                this.getRelativeFrequencies(this, 0);
            } else {
                this.absoluteFrequencies = this.copyObject(this.facetResults);
                this.facetResults = this.relativeFrequencies;
                this.showingRelativeFrequencies = true;
                this.loading = false;
            }
        },
        displayAbsoluteFrequencies() {
            this.loading = true;
            this.relativeFrequencies = this.copyObject(this.facetResults);
            this.facetResults = this.absoluteFrequencies;
            this.showingRelativeFrequencies = false;
            this.loading = false;
        },
        collocationToConcordance(word) {
            this.q = `${this.q} "${word}"`;
            this.start = "";
            this.end = "";
            this.report = "concordance";
            this.$router.push(this.paramsToRoute(this.$store.state.formData));
        },
        showFacetOptions() {
            this.showFacetSelection = true;
        },
        hideFacets() {
            this.showFacetResults = false;
            this.showFacetSelection = true;
        },
        occurrence(count) {
            if (count == 1) {
                return "occurrence";
            } else {
                return "occurrences";
            }
        },
        facetClick(metadata) {
            this.$store.commit("updateMetadata", {
                metadata
            });
            this.$router.push(this.paramsToRoute(this.$store.state.formData));
        }
    }
};
</script>
<style thisd>
.close-box {
    position: absolute;
    padding: 0px 5px;
    top: 0;
    right: 0;
}
.list-group-item {
    position: relative;
    padding: 0.5rem 1.25rem;
}
.sidebar-text {
    cursor: pointer;
}
.sidebar-count {
    width: 100%;
    display: inline-block;
}
.facet-selection {
    width: 100%;
    cursor: pointer;
}
.facet-selection:hover {
    font-weight: 700;
}
</style>

