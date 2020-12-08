<template>
    <b-container fluid>
        <conckwic :results="results.results" :description="results.description"></conckwic>
        <div style="position: relative">
            <b-btn style="position: absolute; bottom: 1rem; right: 0.5rem" @click="toggleFacets()" v-if="!showFacets"
                >Show Facets</b-btn
            >
        </div>
        <b-row>
            <b-col cols="12" md="8" xl="8" :class="{ 'col-md-12': !showFacets }">
                <transition-group tag="div" v-on:before-enter="beforeEnter" v-on:enter="enter">
                    <b-card
                        no-body
                        class="philologic-occurrence ml-2 mr-2 mb-4 shadow-sm"
                        v-for="(result, index) in results.results"
                        :key="result.philo_id.join('-')"
                        :data-index="index"
                    >
                        <b-row no-gutters class="citation-container">
                            <b-col cols="12" sm="10" md="11">
                                <span class="cite">
                                    <span class="number">{{ description.start + index }}</span>
                                    <citations :citation="result.citation"></citations>
                                </span>
                            </b-col>
                            <b-col sm="2" md="1" class="d-none d-sm-inline-block">
                                <b-button class="more-context" @click="moreContext(index)">
                                    <span class="d-none d-lg-inline-block">More</span>
                                    <span class="d-lg-none">+</span>
                                </b-button>
                            </b-col>
                        </b-row>
                        <b-row>
                            <b-col
                                class="m-2 mt-3"
                                select-word
                                :position="results.description.start + index"
                                @keyup="dicoLookup($event, result.metadata_fields.year)"
                                tabindex="0"
                            >
                                <div class="default-length" v-html="result.context"></div>
                                <div class="more-length"></div>
                            </b-col>
                        </b-row>
                    </b-card>
                </transition-group>
            </b-col>
            <b-col md="4" xl="4" v-if="showFacets">
                <facets></facets>
            </b-col>
        </b-row>
        <pages></pages>
    </b-container>
</template>

<script>
import { mapFields } from "vuex-map-fields";
import { EventBus } from "../main.js";
import citations from "./Citations";
import conckwic from "./ConcordanceKwic";
import facets from "./Facets";
import pages from "./Pages";
import Velocity from "velocity-animate";

export default {
    name: "concordance",
    components: {
        citations,
        conckwic,
        facets,
        pages,
    },
    computed: {
        ...mapFields(["formData.report", "resultsLength", "searching", "currentReport", "description"]),
    },
    data() {
        return {
            philoConfig: this.$philoConfig,
            results: { description: { end: 0 } },
            searchParams: {},
            showFacets: true,
        };
    },
    created() {
        this.report = "concordance";
        this.currentReport = "concordance";
        this.fetchResults();
        EventBus.$on("toggleFacets", () => {
            this.toggleFacets();
        });
    },
    watch: {
        // call again the method if the route changes
        $route: "fetchResults",
    },
    methods: {
        fetchResults() {
            this.results = { description: { end: 0 } };
            this.searchParams = { ...this.$store.state.formData };
            this.searching = true;
            this.$http
                .get(`${this.$dbUrl}/reports/concordance.py`, {
                    params: this.paramsFilter(this.searchParams),
                })
                .then((response) => {
                    this.results = response.data;
                    this.$store.commit("updateResultsLength", parseInt(response.data.results_length));
                    this.searching = false;
                })
                .catch((error) => {
                    this.searching = false;
                    this.error = error.toString();
                    this.debug(this, error);
                });
        },
        moreContext(index) {
            let button = event.srcElement;
            let defaultNode = document.getElementsByClassName("default-length")[index];
            let moreNode = document.getElementsByClassName("more-length")[index];
            let resultNumber = this.results.description.start + index - 1;
            let localParams = { hit_num: resultNumber, ...this.searchParams };
            if (button.innerHTML == "More") {
                if (moreNode.innerHTML.length == 0) {
                    this.$http
                        .get(`${this.$dbUrl}/scripts/get_more_context.py`, {
                            params: this.paramsFilter(localParams),
                        })
                        .then((response) => {
                            let moreText = response.data;
                            moreNode.innerHTML = moreText;
                            defaultNode.style.display = "none";
                            moreNode.style.display = "block";
                            button.innerHTML = "Less";
                        })
                        .catch((error) => {
                            this.loading = false;
                            this.error = error.toString();
                            this.debug(this, error);
                        });
                } else {
                    defaultNode.style.display = "none";
                    moreNode.style.display = "block";
                    button.innerHTML = "Less";
                }
            } else {
                defaultNode.style.display = "block";
                moreNode.style.display = "none";
                button.innerHTML = "More";
            }
        },
        dicoLookup() {},
        beforeEnter: function (el) {
            el.style.opacity = 0;
        },
        enter: function (el, done) {
            let delay = el.dataset.index * 35;
            setTimeout(function () {
                Velocity(el, { opacity: 1 }, { complete: done });
            }, delay);
        },
        toggleFacets() {
            if (this.showFacets) {
                this.showFacets = false;
            } else {
                this.showFacets = true;
            }
        },
    },
};
</script>

<style>
.philologic-occurrence {
    left: 0;
    position: relative;
}
.separator {
    padding: 5px;
    font-size: 60%;
    display: inline-block;
    vertical-align: middle;
}
.more-context {
    position: absolute;
    right: 0;
}
.more_context,
.citation-container {
    border-bottom: solid 1px #eee !important;
}
.number {
    background-color: rgb(78, 93, 108);
    color: #fff;
    font-size: 1rem;
    line-height: 1.5;
    padding: 0.375rem 0.75rem;
    display: inline-block;
    margin-right: 5px;
    border-radius: 0.25rem;
    height: 100%;
}
.hit_n {
    vertical-align: 5px;
    /*align numbers*/
}
.cite {
    height: 38px;
    display: inline-block;
}
.philologic-doc {
    font-variant: small-caps;
    font-weight: 700;
}
.citation-separator {
    margin-left: 8px;
    padding-left: 8px;
    border-left: double 3px darkgray;
}
.page-display {
    margin-left: 8px;
    padding-left: 8px;
    border-left: double 3px darkgray;
}
.citation-small-caps {
    font-variant: small-caps;
}

/* Concordance styling for theater */
.xml-speaker {
    font-weight: 700;
}
.xml-sp + .xml-l,
.xml-sp + .xml-ab {
    display: inline;
}
.xml-stage {
    font-style: italic;
}
</style>
