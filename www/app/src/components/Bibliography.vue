<template>
    <div class="container-fluid">
        <results-summary :results="results.results" :description="results.description"></results-summary>
        <div class="row mt-4" style="padding-right: 0.5rem">
            <div
                class="col-12 col-md-7 col-xl-8"
                v-if="!philoConfig.dictionary_bibliography || results.result_type == 'doc'"
            >
                <transition-group tag="div" v-on:before-enter="beforeEnter" v-on:enter="enter">
                    <div
                        class="card philologic-occurrence mx-2 mb-4 shadow-sm"
                        v-for="(result, index) in results.results"
                        :key="result.philo_id.join('-')"
                    >
                        <div class="row citation-container">
                            <div class="col-12 col-sm-10 col-md-11">
                                <span class="cite" :data-id="result.philo_id.join(' ')">
                                    <span class="number">{{ results.description.start + index }}</span>
                                    <input
                                        type="checkbox"
                                        class="ms-3 me-2"
                                        @click="addToSearch(result.metadata_fields.title)"
                                        v-if="resultType == 'doc' && philoConfig.metadata.indexOf('title') !== -1"
                                    />
                                    <citations :citation="result.citation"></citations>
                                </span>
                            </div>
                        </div>
                    </div>
                </transition-group>
            </div>
            <div
                class="col-12 col-md-7 col-xl-8"
                v-if="philoConfig.dictionary_bibliography && results.result_type != 'doc'"
            >
                <div class="list-group" flush v-for="(group, groupKey) in results.results" :key="groupKey">
                    <div
                        class="list-group-item p-0"
                        v-for="(result, index) in group"
                        :key="index"
                        style="border-width: 0"
                    >
                        <div class="card philologic-occurrence mx-2 mb-4 shadow-sm">
                            <div class="citation-dico-container">
                                <span class="cite" :data-id="result.philo_id.join(' ')">
                                    <span class="number">{{ results.description.start + index }}</span>
                                    <citations :citation="result.citation"></citations>
                                </span>
                            </div>
                            <div
                                class="philologic_context text-content-area pt-2 px-2 text-justify"
                                select-word
                                :position="result.position"
                            >
                                <div v-html="result.context"></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col" md="5" xl="4">
                <facets></facets>
            </div>
        </div>
        <pages></pages>
    </div>
</template>
<script>
import { mapFields } from "vuex-map-fields";
import { emitter } from "../main.js";
import citations from "./Citations";
import ResultsSummary from "./ResultsSummary";
import facets from "./Facets";
import pages from "./Pages";
import Velocity from "velocity-animate";

export default {
    name: "bibliography",
    components: {
        citations,
        ResultsSummary,
        facets,
        pages,
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
            "formData.metadataFields",
            "description",
            "currentReport",
        ]),
    },
    inject: ["$http"],
    data() {
        return {
            philoConfig: this.$philoConfig,
            results: {},
            resultType: "doc",
            metadataAddition: [],
            unbindEmitter: null,
        };
    },
    created() {
        this.report = "bibliography";
        this.currentReport = "bibliography";
        this.fetchResults();
        this.unbindEmitter = emitter.on("urlUpdate", () => {
            if (this.report == "bibliography") {
                this.fetchResults();
            }
        });
    },
    beforeUnmount() {
        this.unbindEmitter();
    },
    methods: {
        fetchResults() {
            this.results = {};
            this.searchParams = { ...this.$store.state.formData };
            this.$http
                .get(`${this.$dbUrl}/reports/bibliography.py`, {
                    params: this.paramsFilter(this.searchParams),
                })
                .then((response) => {
                    if (!this.philoConfig.dictionary_bibliography || response.data.doc_level) {
                        this.results = response.data;
                        this.resultType = this.results.result_type;
                    } else {
                        this.results = this.dictionaryBibliography(response.data);
                        console.log(this.results);
                    }
                })
                .catch((error) => {
                    this.loading = false;
                    this.error = error.toString();
                    this.debug(this, error);
                });
        },
        dictionaryBibliography(data) {
            let groupedResults = [];
            let currentTitle = data.results[0].metadata_fields.title;
            let titleGroup = [];
            for (let i = 0; i < data.results.length; i += 1) {
                if (data.results[i].metadata_fields.title !== currentTitle) {
                    groupedResults.push(titleGroup);
                    titleGroup = [];
                    currentTitle = data.results[i].metadata_fields.title;
                }
                data.results[i].position = i + 1;
                titleGroup.push(data.results[i]);
                if (i + 1 == data.results.length) {
                    groupedResults.push(titleGroup);
                }
            }
            data.results = groupedResults;
            return data;
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
            this.$store.commit("updateFormDataField", {
                key: "title",
                value: newTitleValue,
            });
            emitter.emit("metadataUpdate", { title: newTitleValue });
        },
        beforeEnter: function (el) {
            el.style.opacity = 0;
        },
        enter: function (el, done) {
            var delay = el.dataset.index * 100;
            setTimeout(function () {
                Velocity(el, { opacity: 1 }, { complete: done });
            }, delay);
        },
    },
};
</script>
<style scoped>
.citation-container {
    border-width: 0 !important;
}
.citation-dico-container {
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
}
</style>
