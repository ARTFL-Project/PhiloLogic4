<template>
    <div>
        <conckwic v-if="description.end != 0"></conckwic>
        <b-row class="mr-2">
            <b-col cols="12" md="7" xl="8">
                <transition-group tag="div" v-on:before-enter="beforeEnter" v-on:enter="enter">
                    <b-card
                        no-body
                        class="philologic-occurrence ml-4 mr-4 mb-4 shadow-sm"
                        v-for="(result, index) in results.results"
                        :key="result.philo_id.join('-')"
                        :data-index="index"
                    >
                        <b-row class="citation-container">
                            <b-col cols="12" sm="10" md="11">
                                <span class="cite">
                                    <span class="number">{{ description.start + index }}</span>
                                    <citations :citation="result.citation"></citations>
                                </span>
                            </b-col>
                            <b-col sm="2" md="1" class="hidden-xs">
                                <button
                                    id="more-context"
                                    class="btn btn-primary more-context"
                                    @click="moreContext(index)"
                                >More</button>
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
            <b-col md="5" xl="4">
                <facets></facets>
            </b-col>
        </b-row>
        <pages v-if="resultsLength > 0"></pages>
    </div>
</template>

<script>
import { mapFields } from "vuex-map-fields";
import citations from "./Citations";
import conckwic from "./ConcordanceKwic";
import facets from "./Facets";
import pages from "./Pages";
import { EventBus } from "../main.js";
import Velocity from "velocity-animate";

export default {
    name: "concordance",
    components: {
        citations,
        conckwic,
        facets,
        pages
    },
    computed: {
        ...mapFields([
            "formData.report",
            "resultsLength",
            "searching",
            "currentReport",
            "description"
        ])
    },
    data() {
        return {
            philoConfig: this.$philoConfig,
            results: {},
            searchParams: {}
        };
    },
    created() {
        this.report = "concordance";
        this.currentReport = "concordance";
        this.fetchResults();
        EventBus.$on("urlUpdate", () => {
            if (this.report == "concordance") {
                this.fetchResults();
            }
        });
    },
    beforeDestroy() {
        EventBus.$off("urlUpdate");
    },
    methods: {
        fetchResults() {
            this.results = {};
            this.searchParams = { ...this.$store.state.formData };
            this.searching = true;
            this.$http
                .get(
                    "http://anomander.uchicago.edu/philologic/frantext0917/reports/concordance.py",
                    { params: this.paramsFilter(this.searchParams) }
                )
                .then(response => {
                    this.results = response.data;
                    this.resultsLength = response.data.results_length;
                    this.$store.commit("updateDescription", {
                        ...this.description,
                        start: this.results.description.start,
                        end: this.results.description.end,
                        results_per_page: this.results.description
                            .results_per_page
                    });
                    this.searching = false;
                    EventBus.$emit("resultsDone");
                })
                .catch(error => {
                    this.searching = false;
                    this.error = error.toString();
                    console.log(error);
                });
        },
        moreContext(index) {
            let button = event.srcElement;
            let parentNode = button.parentNode.parentNode.parentNode;
            let defaultNode = parentNode.querySelector(".default-length");
            let moreNode = parentNode.querySelector(".more-length");
            let resultNumber = this.results.description.start + index - 1;
            let localParams = { hit_num: resultNumber, ...this.searchParams };
            if (button.innerHTML == "More") {
                if (moreNode.innerHTML.length == 0) {
                    this.$http(
                        "http://anomander.uchicago.edu/philologic/frantext0917/scripts/get_more_context.py",
                        { params: this.paramsFilter(localParams) }
                    )
                        .then(response => {
                            let moreText = response.data;
                            moreNode.innerHTML = moreText;
                            defaultNode.style.display = "none";
                            moreNode.style.display = "block";
                            button.innerHTML = "Less";
                        })
                        .catch(error => {
                            this.loading = false;
                            this.error = error.toString();
                            console.log(error);
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
        beforeEnter: function(el) {
            el.style.opacity = 0;
        },
        enter: function(el, done) {
            var delay = el.dataset.index * 100;
            setTimeout(function() {
                Velocity(el, { opacity: 1 }, { complete: done });
            }, delay);
        }
    }
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
    right: 15px;
}
.more_context,
.citation-container {
    border-bottom: solid 1px #eee !important;
}
.number {
    background-color: rgb(78, 93, 108);
    color: #fff;
    padding: 7px;
    display: inline-block;
    margin-left: -10px;
    margin-top: -10px;
    margin-right: 5px;
}
.hit_n {
    vertical-align: 5px;
    /*align numbers*/
}
.cite {
    padding-left: 0.6em;
    padding-top: 7px;
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
