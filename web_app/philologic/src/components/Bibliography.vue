<template>
    <div>
        <conckwic :results="results" v-if="Object.keys(results).length"></conckwic>
        <b-row class="mr-2">
            <b-col
                cols="12"
                md="7"
                xl="8"
                v-if="!philoConfig.dictionary_bibliography || results.result_type == 'doc'"
            >
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
                                <input
                                    type="checkbox"
                                    style="margin-left:10px; margin-right: 10px;"
                                    @click="addToSearch(result.metadata_fields.title)"
                                    v-if="resultType == 'doc' && philoConfig.metadata.indexOf('title') !== -1"
                                >
                                <span class="philologic_cite">
                                    <span
                                        class="citation"
                                        v-for="(citation, citeIndex) in result.citation"
                                        :key="citeIndex"
                                    >
                                        <span v-if="citation.href">
                                            <span v-html="citation.prefix"></span>
                                            <router-link
                                                :to="'/' + citation.href"
                                                :style="citation.style"
                                            >{{ citation.label }}</router-link>
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
                    </b-row>
                </b-card>
            </b-col>
            <b-col
                cols="12"
                md="7"
                xl="8"
                v-if="philoConfig.dictionary_bibliography || results.result_type != 'doc'"
            ></b-col>
            <b-col md="5" xl="4">
                <facets></facets>
            </b-col>
        </b-row>
        <pages></pages>
    </div>
    <!-- <ol
        id="bibliographic-results"
        class="text-content-area"
        ng-if="philoConfig.dictionary_bibliography && result.result_type != 'doc'"
    >
        <li class="biblio-occurrence panel panel-default" ng-repeat="group in ::results.results">
            <h3 style="margin: 0; padding: 0px 10px; text-align: center; font-variant: small-caps;">
                <i>{{ ::group[0].metadata_fields.title }}</i>
            </h3>
            <ol style="margin-top: 10px;">
                <li style="margin-top: 0;" ng-repeat="result in ::group">
                    <input
                        type="checkbox"
                        style="margin-left:10px"
                        ng-click="addToSearch(result.citation.title.label)"
                        ng-if="results.doc_level && philoConfig.metadata.indexOf('title') !== -1"
                    >
                    <span style="padding-left: 10px;">{{ ::result.position }}.</span>
                    <span class="philologic_cite">
                        <span class="citation" ng-repeat="citation in result.citation">
                            <span ng-if="citation.href">
                                <span ng-bind-html="citation.prefix"></span>
                                <a
                                    ng-href="{{ ::citation.href }}"
                                    ng-style="citation.style"
                                >{{ ::citation.label }}</a>
                                <span ng-bind-html="citation.suffix"></span>
                                <span ng-bind-html="citation.separator" ng-if="!$last"></span>
                            </span>
                            <span ng-if="!citation.href">
                                <span ng-bind-html="citation.prefix"></span>
                                <span ng-style="citation.style">{{ ::citation.label }}</span>
                                <span ng-bind-html="citation.suffix"></span>
                                <span ng-bind-html="citation.separator" ng-if="!$last"></span>
                            </span>
                        </span>
                    </span>
                    <div
                        class="philologic_context text-content-area"
                        select-word
                        position="{{ result.position }}"
                    >
                        <div
                            style="padding: 0px 15px 0px 30px;"
                            ng-bind-html="result.context | unsafe"
                        ></div>
                    </div>
                </li>
            </ol>
        </li>
    </ol>-->
</template>
<script>
import { mapFields } from "vuex-map-fields";
import { EventBus } from "../main.js";
import conckwic from "./ConcordanceKwic";
import facets from "./Facets";
import pages from "./Pages";

export default {
    name: "bibliography",
    components: {
        conckwic,
        facets,
        pages
    },
    computed: {
        ...mapFields([
            "formData.report",
            "formData.q",
            "formData.arg_proxy",
            "formData.arg_phrase",
            "formData.method",
            "formData.start",
            "formData.end",
            "formData.approximate",
            "formData.approximate_ratio",
            "formData.metadataFields"
        ])
    },
    data() {
        return {
            philoConfig: this.$philoConfig,
            results: {},
            resultType: "doc",
            metadataAddition: []
        };
    },
    created() {
        this.report = "bibliography";
        this.fetchResults();
        var vm = this;
        EventBus.$on("urlUpdate", function() {
            vm.fetchResults();
        });
    },
    methods: {
        fetchResults() {
            this.results = {};
            this.searchParams = { ...this.$store.state.formData };
            this.$http
                .get(
                    "http://anomander.uchicago.edu/philologic/frantext0917/reports/bibliography.py",
                    { params: this.paramsFilter(this.searchParams) }
                )
                .then(response => {
                    this.results = response.data;
                    this.resultType = this.results.result_type;
                })
                .catch(error => {
                    this.loading = false;
                    this.error = error.toString();
                    console.log(error);
                });
        },
        addToSearch(titleValue) {
            let title = '"' + titleValue + '"';
            let itemIndex = this.metadataAddition.indexOf(title);
            if (itemIndex === -1) {
                this.metadataAddition.push(title);
            } else {
                this.metadataAddition.splice(itemIndex, 1);
            }
            let newTitleValue = this.metadataAddition.join(" | ");
            this.$store.commit("updateMetadata", {
                title: newTitleValue
            });
            EventBus.$emit("metadataUpdate", { title: newTitleValue });
        }
    }
};
</script>
<style scoped>
</style>

