<template>
    <div>
        <conckwic :results="results" v-if="Object.keys(results).length"></conckwic>
        <b-row class="mr-2">
            <b-col cols="12" md="7" xl="8">
                <b-card
                    no-body
                    class="philologic-occurrence ml-4 mr-4 mb-4 shadow-sm"
                    v-for="(result, index) in results.results"
                    :key="index"
                >
                    <b-row class="citation-container">
                        <b-col cols="12" sm="10" md="11">
                            <span class="cite" :data-id="result.philo_id.join(' ')">
                                <span class="result-number">{{ results.description.start + index }}</span>
                                <span class="philologic_cite">
                                    <span
                                        class="citation"
                                        v-for="(citation, citeIndex) in result.citation"
                                        :key="citeIndex"
                                    >
                                        <span v-if="citation.href">
                                            <span v-html="citation.prefix"></span>
                                            <a
                                                :href="citation.href"
                                                :style="citation.style"
                                            >{{ citation.label }}</a>
                                            <span v-html="citation.suffix"></span>
                                            <span
                                                class="separator"
                                                v-if="citeIndex != result.citation.length - 1"
                                            >&#9679;</span>
                                        </span>
                                        <span v-if="!citation.href">
                                            <span v-html="citation.prefix"></span>
                                            <span :style="citation.style">{{ citation.label }}</span>
                                            <span v-html="citation.suffix"></span>
                                            <span
                                                class="separator"
                                                v-if="citeIndex != result.citation.length - 1"
                                            >&#9679;</span>
                                        </span>
                                    </span>
                                </span>
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
            </b-col>
            <b-col md="5" xl="4">
                <facets></facets>
            </b-col>
        </b-row>
    </div>
</template>

<script>
import { mapFields } from "vuex-map-fields";
import conckwic from "./ConcordanceKwic";
import facets from "./Facets";
import { EventBus } from "../main.js";

export default {
    name: "concordance",
    components: {
        conckwic,
        facets
    },
    computed: {
        ...mapFields(["formData.report"])
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
        this.fetchResults();
        var vm = this;
        EventBus.$on("urlUpdate", function() {
            if (vm.report == "concordance") {
                vm.fetchResults();
            }
        });
    },
    methods: {
        fetchResults() {
            this.results = {};
            this.searchParams = { ...this.$store.state.formData };
            this.$http
                .get(
                    "http://anomander.uchicago.edu/philologic/test/reports/concordance.py",
                    { params: this.paramsFilter(this.searchParams) }
                )
                .then(response => {
                    this.results = response.data;
                })
                .catch(error => {
                    this.loading = false;
                    this.error = error.toString();
                    console.log(error);
                });
        },
        moreContext(index) {
            let parentNode = event.srcElement.parentNode.parentNode.parentNode;
            let defaultNode = parentNode.querySelector(".default-length");
            let moreNode = parentNode.querySelector(".more-length");
            let resultNumber = this.results.description.start + index - 1;
            let localParams = { hit_num: resultNumber, ...this.searchParams };
            this.$http(
                "http://anomander.uchicago.edu/philologic/test/scripts/get_more_context.py",
                { params: this.paramsFilter(localParams) }
            )
                .then(response => {
                    let moreText = response.data;
                    moreNode.innerHTML = moreText;
                    defaultNode.style.display = "none";
                    moreNode.style.display = "block";
                })
                .catch(error => {
                    this.loading = false;
                    this.error = error.toString();
                    console.log(error);
                });
            console.log(parentNode);
        },
        dicoLookup() {}
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
.result-number {
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
</style>
