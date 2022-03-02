<template>
    <div class="container-fluid">
        <results-summary :description="results.description"></results-summary>
        <div style="position: relative" v-if="!showFacets">
            <button
                type="button"
                class="btn btn-secondary"
                style="position: absolute; bottom: 1rem; right: 0.5rem"
                @click="toggleFacets()"
            >
                Show Facets
            </button>
        </div>
        <div class="row" style="padding-right: 0.5rem">
            <div class="col-12" :class="{ 'col-md-8': showFacets, 'col-xl-9': showFacets }">
                <transition-group tag="div" v-on:before-enter="beforeEnter" v-on:enter="enter">
                    <div
                        class="card philologic-occurrence ms-2 me-2 mb-4 shadow-sm"
                        v-for="(result, index) in results.results"
                        :key="result.philo_id.join('-')"
                        :data-index="index"
                    >
                        <div class="row citation-container g-0">
                            <div class="col-12 cpl-sm-10 col-md-11">
                                <span class="cite">
                                    <span class="number">{{ results.description.start + index }}</span>
                                    <citations :citation="result.citation"></citations>
                                </span>
                            </div>
                            <div class="col-sm-2 col-md-1 d-none d-sm-inline-block">
                                <button
                                    type="button"
                                    class="btn btn-secondary more-context"
                                    @click="moreContext(index, $event)"
                                >
                                    <span class="more d-none d-lg-inline-block">More</span>
                                </button>
                            </div>
                        </div>
                        <div class="row">
                            <div
                                class="col m-2 mt-3 concordance-text text-view"
                                :position="results.description.start + index"
                                @keyup="dicoLookup($event, result.metadata_fields.year)"
                            >
                                <div class="default-length" v-html="result.context"></div>
                                <div class="more-length"></div>
                            </div>
                        </div>
                    </div>
                </transition-group>
            </div>
            <div class="col col-md-4 col-xl-3" v-if="showFacets">
                <facets></facets>
            </div>
        </div>
        <pages></pages>
    </div>
</template>

<script>
import { computed } from "vue";
import { mapFields } from "vuex-map-fields";
import citations from "./Citations";
import ResultsSummary from "./ResultsSummary";
import facets from "./Facets";
import pages from "./Pages";
import Velocity from "velocity-animate";

export default {
    name: "concordance-report",
    components: {
        citations,
        ResultsSummary,
        facets,
        pages,
    },
    inject: ["$http"],
    provide() {
        return {
            results: computed(() => this.results.results),
        };
    },
    computed: {
        ...mapFields([
            "formData.report",
            "resultsLength",
            "searching",
            "currentReport",
            "description",
            "showFacets",
            "urlUpdate",
        ]),
    },
    data() {
        return {
            philoConfig: this.$philoConfig,
            results: { description: { end: 0 }, results: [] },
            searchParams: {},
            unbindUrlUpdate: null,
            start: 1,
        };
    },
    created() {
        this.report = "concordance";
        this.currentReport = "concordance";
        this.fetchResults();
    },
    watch: {
        urlUpdate() {
            if (this.report == "concordance") {
                this.fetchResults();
            }
        },
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
        moreContext(index, event) {
            let button = event.srcElement;
            if (button.tagName == "BUTTON") {
                button = button.querySelector("span");
            }
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
.concordance-text {
    text-align: justify;
}
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
    line-height: 1.8;
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
