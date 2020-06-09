<template>
    <div id="facet-search" class="d-xs-none mr-2">
        <b-card
            no-body
            title="Title"
            header-tag="header"
            id="facet-panel-wrapper"
            class="shadow-sm"
        >
            <b-btn
                size="sm"
                style="position: absolute; top:0; right: 0; line-height: 1"
                @click="toggleFacets()"
            >x</b-btn>
            <h6 slot="header" class="mb-0 text-center">Browse by facet</h6>

            <transition name="slide-fade">
                <b-list-group flush id="select-facets" v-if="showFacetSelection">
                    <span class="dropdown-header text-center">Frequency by</span>
                    <b-list-group-item
                        v-for="facet in facets"
                        :key="facet.alias"
                        @click="getFacet(facet)"
                        class="facet-selection"
                    >{{ facet.alias }}</b-list-group-item>
                </b-list-group>
            </transition>
            <transition name="slide-fade">
                <b-list-group
                    flush
                    class="mt-1"
                    style="border-top: 0"
                    v-if="showFacetSelection && report != 'bibliography'"
                >
                    <span class="dropdown-header text-center">Collocates of query term(s)</span>
                    <b-list-group-item
                        @click="getFacet(collocationFacet)"
                        v-if="report !== 'bibliography'"
                        class="facet-selection"
                    >{{ collocationFacet.alias }}</b-list-group-item>
                </b-list-group>
            </transition>
            <transition name="options-slide">
                <div
                    class="m-2 text-center"
                    style="width: 100%; font-size: 90%; opacity: 0.8; cursor: pointer;"
                    v-if="!showFacetSelection"
                    @click="showFacetOptions()"
                >Show Options</div>
            </transition>
        </b-card>
        <div class="d-flex justify-content-center position-relative" v-if="loading">
            <b-spinner
                variant="secondary"
                style="width: 4rem; height: 4rem; position: absolute; z-index: 50; top: 10px;"
            ></b-spinner>
        </div>
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
                class="shadow-sm"
                size="sm"
                v-if="percent == 100 && report !== 'bibliography' && facet.type === 'facet'"
            >
                <b-button
                    variant="light"
                    :class="{'active': showingRelativeFrequencies === false}"
                    @click="displayAbsoluteFrequencies()"
                >Absolute Frequency</b-button>
                <b-button
                    variant="light"
                    :class="{'active': showingRelativeFrequencies}"
                    @click="displayRelativeFrequencies()"
                >Relative Frequency</b-button>
            </b-button-group>
            <div
                class="m-2 text-center"
                style="opacity: 0.5"
            >Top 500 results for {{ selectedFacet.alias }}</div>
            <b-progress
                :max="resultsLength"
                show-progress
                variant="secondary"
                class="ml-3 mr-3 mb-3"
                v-if="percent != 100"
            >
                <b-progress-bar
                    :value="runningTotal"
                    :label="`${((runningTotal / resultsLength) * 100).toFixed(2)}%`"
                ></b-progress-bar>
            </b-progress>
            <b-list-group flush>
                <b-list-group-item v-for="result in facetResults" :key="result.label">
                    <div>
                        <a
                            href
                            class="sidebar-text text-content-area"
                            v-if="facet.facet !== 'all_collocates'"
                            @click.prevent="facetClick(result.metadata)"
                        >{{ result.label }}</a>
                        <a
                            href
                            class="sidebar-text text-content-area"
                            v-else
                            @click.prevent="collocationToConcordance(result.label)"
                        >{{ result.label }}</a>
                        <b-badge variant="secondary" pill class="float-right">{{ result.count }}</b-badge>
                    </div>
                    <div
                        style="line-height: 70%; padding-bottom: 15px; font-size: 85%;"
                        v-if="showingRelativeFrequencies"
                    >
                        <div style="display: inline-block; opacity: .8">
                            {{ fullResults.unsorted[result.label].count }} actual {{ occurrence(fullResults.unsorted[result.label].count) }}
                            in {{ fullRelativeFrequencies[result.label].total_count }} words
                        </div>
                    </div>
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
            "fornData.method",
            "formData.start",
            "formData.end",
            "formData.metadataFields",
            "resultsLength"
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
            selected: "",
            runningTotal: 0
        };
    },
    created() {
        this.facets = this.populateFacets();
        EventBus.$on("urlUpdate", () => {
            this.facetResults = [];
            this.fullResults = {};
            this.showFacetSelection = true;
            this.showFacetResults = false;
        });
    },
    methods: {
        populateFacets() {
            let facetConfig = this.philoConfig.facets;
            let facets = [];
            let alias;
            for (let i = 0; i < facetConfig.length; i++) {
                let facet = facetConfig[i];
                if (!this.$philoConfig.metadata.includes(facet)) {
                    continue;
                }
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
            this.debug(this, this.$store.state.formData);
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
                this.populateSidebar(facetObj, fullResults, 0, queryParams);
            }
        },
        populateSidebar(facet, fullResults, start, queryParams) {
            var promise;
            if (this.moreResults) {
                if (facet.type !== "collocationFacet") {
                    promise = this.$http.get(
                        `${this.$dbUrl}/scripts/get_frequency.py`,
                        {
                            params: this.paramsFilter({
                                ...queryParams,
                                start: start.toString()
                            })
                        }
                    );
                } else {
                    promise = this.$http.get(
                        `${this.$dbUrl}/reports/collocation.py`,
                        {
                            params: this.paramsFilter({
                                ...queryParams,
                                start: start.toString()
                            })
                        }
                    );
                }
                this.showFacetSelection = false;
                promise
                    .then(response => {
                        var results = response.data.results;
                        this.moreResults = response.data.more_results;
                        var merge;
                        if (!this.interrupt && this.selected == facet.alias) {
                            if (facet.type === "collocationFacet") {
                                merge = this.mergeResults(
                                    fullResults.unsorted,
                                    response.data.collocates
                                );
                            } else {
                                merge = this.mergeResults(
                                    fullResults.unsorted,
                                    results
                                );
                            }
                            this.facetResults = merge.sorted.slice(0, 500);
                            this.loading = false;
                            this.showFacetResults = true;
                            fullResults = merge;
                            this.runningTotal = response.data.hits_done;
                            start = response.data.hits_done;
                            this.populateSidebar(
                                facet,
                                fullResults,
                                start,
                                queryParams
                            );
                        } else {
                            // this won't affect the full collocation report which can't be interrupted when on the page
                            this.interrupt = false;
                        }
                    })
                    .catch(error => {
                        this.debug(this, error);
                        this.loading = false;
                    });
            } else {
                this.loading = false;
                this.runningTotal = this.resultsLength;
                this.fullResults = fullResults;
                this.percent = 100;
                let urlString = this.paramsToUrlString({
                    ...queryParams,
                    frequency_field: this.selectedFacet.alias
                });
                this.saveToLocalStorage(urlString, fullResults);
            }
        },
        roundToTwo(num) {
            return +(Math.round(num + "e+2") + "e-2");
        },
        getRelativeFrequencies() {
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
                this.getRelativeFrequencies();
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
            this.$store.commit("updateFormDataField", {
                key: "method",
                value: "cooc"
            });
            this.start = "";
            this.end = "";
            this.report = "concordance";
            this.$router.push(
                this.paramsToRoute({ ...this.$store.state.formData })
            );
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
            this.$store.commit("updateFormDataField", {
                key: this.selectedFacet.facet,
                value: `"${metadata[this.selectedFacet.facet]}"`
            });
            this.$router.push(
                this.paramsToRoute({
                    ...this.$store.state.formData,
                    start: "0",
                    end: "0"
                })
            );
        },
        toggleFacets() {
            EventBus.$emit("toggleFacets");
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
.slide-fade-enter-active {
    transition: all 0.3s ease-out;
}
.slide-fade-leave-active {
    transition: all 0.3s ease-out;
}
.slide-fade-enter,
.slide-fade-leave-to {
    transform: translateY(-10px);
    height: 0;
    opacity: 0;
}
.options-slide-fade-enter-active {
    transition: all 0.3s ease-in;
}
.options-slide-fade-leave-active {
    transition: all 0.3s ease-in;
}
.options-slide-fade-enter,
.options-slide-fade-leave-to {
    opacity: 0;
}
</style>

