<template>
    <div id="facet-search" class="hidden-xs col-sm-4" loading="loading">
        <b-card
            no-body
            title="Title"
            header-tag="header"
            id="facet-panel-wrapper"
            class="panel panel-default clearfix"
            :style="sidebarHeight"
        >
            <h6 slot="header" class="mb-0">
                Browse by facet
                <b-button class="btn btn-primary btn-sm close-box" @click="hideFacets()">X</b-button>
            </h6>Browse by facet
            <b-list-group flush id="select-facets" v-if="showFacetSelection">
                <b-list-group-item
                    v-for="facet in facets"
                    :key="facet.alias"
                    @click="getFacet(facet)"
                >{{ facet.alias }}</b-list-group-item>
                <hr>
            </b-list-group>
            <b-list-group>
                Collocates of query term(s)
                <b-list-group-item
                    @click="getFacet(collocationFacet)"
                    v-if="report !== 'bibliography'"
                >{{ collocationFacet.alias }}</b-list-group-item>
            </b-list-group>
        </b-card>
        <b-card no-body id="facet-results" class="p-2" v-if="showFacetResults">
            <b-button-group
                v-if="percent == 100 && report !== 'bibliography' && facet.type === 'facet'"
            >
                <b-button
                    :class="{'active': showingRelativeFrequencies === false}"
                    @click="displayAbsoluteFrequencies()"
                >Absolute Frequency</b-button>
                <b-button
                    :class="{'active': showingRelativeFrequencies}"
                    @click="displayRelativeFrequencies()"
                >Relative Frequency</b-button>
            </b-button-group>
            <h5 style="text-align: center;">Top 500 results for {{ selectedFacet.alias }}</h5>
            <!-- <progress-bar
                progress="{{ percent }}"
                class="velocity-opposites-transition-slideDownIn"
                data-velocity-opts="{duration:400}"
            ></progress-bar>-->
            <b-list-group>
                class="velocity-opposites-transition-fadeIn" data-velocity-opts="{duration:400}">
                <b-list-group-item
                    v-for="result in facetResults"
                    :key="result.label"
                    @click="facetClick(result)"
                >
                    <a
                        id="freq_sidebar_text"
                        class="text-content-area"
                        :href="result.url"
                        v-if="facet.facet !== 'all_collocates'"
                    >
                        <span>{{ result.label }}</span>
                    </a>
                    <a
                        id="freq_sidebar_text"
                        class="text-content-area"
                        href
                        @click="collocationToConcordance(result.label)"
                        v-if="facet.facet === 'all_collocates'"
                    >
                        <span>{{ result.label }}</span>
                    </a>
                    <span class="sidebar-count">{{ result.count }}</span>
                    <div
                        style="line-height: 70%; padding-bottom: 15px; padding-left: 5px; font-size: 85%;"
                        v-if="showingRelativeFrequencies"
                    >
                        <div style="opacity: .8">
                            {{ fullResults.unsorted[result.label].count }} actual {{ occurrence }}
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
            "formData.approximate",
            "formData.approximate_ratio"
        ]),
        occurrence() {
            if (this.fullResults.unsorted[result.label].count == 1) {
                return "occurrence"
            } else {
                return "occurrences"
            }
        }
    },
    data() {
        return {
            philoConfig: this.$philoConfig,
            facets: [],
            queryArgs: {},
            showFacetSelection: true,
            showFacetResults: false,
            collocationFacet = {
                facet: "all_collocates",
                alias: "in the same sentence",
                type: "collocationFacet"
            },
            percent: 0,
            loading: false,
            moreResults: false,
            done: true,
            facet: {},
            selectedFacet: {},
            showingRelativeFrequencies: false,
            fullResults: {},
            relativeFrequencies: [],
            absoluteFrequencies: []
        };
    },
    created() {
        this.populateFacets()
        this.fetchResults();
        var vm = this;
        EventBus.$on("urlUpdate", function() {
            vm.fetchResults();
        });
    },
    methods: {
        populateFacets() {
            let facetConfig = this.philoConfig.facets;
            let facets = [];
            for (let i = 0; i < facetConfig.length; i++) {
                let facet = facetConfig[i];
                if (facet in philoConfig.metadata_aliases) {
                    let alias = philoConfig.metadata_aliases[facet];
                } else {
                    let alias = facet;
                }
                facets.push({
                    facet: facet,
                    alias: alias,
                    type: 'facet'
                });
            }
            return facets;
        },
        fetchResults(){},
        getFacet(facetObj) {
            this.relativeFrequencies = []
            this.absoluteFrequencies = []
            this.showingRelativeFrequencies = false
            this.facet = facetObj;
            this.selectedFacet = facetObj;
            let urlString = this.paramsToUrlString({...this.$store.state.formData, frequency_field: facetObj.alias})
            if (typeof(sessionStorage[urlString]) !== "undefined" && this.philoConfig.production === true) {
                this.loading = true
                this.fullResults = JSON.parse(sessionStorage[urlString])
                this.facetResults = scope.fullResults.sorted.slice(0, 500)
                this.loading = false
                this.percent = 100
            } else {
                // store the selected field to check whether to kill the ajax calls in populate_sidebar
                // document.querySelector('#select-facets').data('selected', facetObj.alias);
                // angular.element('#select-facets').data('interrupt', false);
                this.done = false
                let fullResults = {};
                this.loading = true;
                this.moreResults = true;
                this.percent = 0;
                let queryParams = this.copyObj(this.$store.state.formData)
                if (facetObj.type === "facet") {
                    queryParams.script = "get_frequency.py";
                    queryParams.frequency_field = facetObj.facet;
                } else if (facetObj.type === "collocationFacet") {
                    queryParams.report = "collocation";
                } else {
                    queryParams.field = facetObj.facet;
                    queryParams.script = "get_word_frequency.py";
                }
                populateSidebar(scope, facetObj, fullResults, 0, queryParams);
            }
        }
    }
}
</script>
<style scoped>
</style>

