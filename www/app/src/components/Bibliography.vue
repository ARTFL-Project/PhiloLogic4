<template>
    <b-container fluid>
        <conckwic :results="results.results" v-if="Object.keys(results).length"></conckwic>
        <b-row class="mt-4">
            <b-col cols="12" md="7" xl="8" v-if="!philoConfig.dictionary_bibliography || results.result_type == 'doc'">
                <transition-group tag="div" v-on:before-enter="beforeEnter" v-on:enter="enter">
                    <b-card
                        no-body
                        class="philologic-occurrence ml-2 mr-2 mb-4 shadow-sm"
                        v-for="(result, index) in results.results"
                        :key="result.philo_id.join('-')"
                    >
                        <b-row class="citation-container">
                            <b-col cols="12" sm="10" md="11">
                                <span class="cite" :data-id="result.philo_id.join(' ')">
                                    <span class="number">{{ results.description.start + index }}</span>
                                    <input
                                        type="checkbox"
                                        class="ml-3 mr-2"
                                        @click="addToSearch(result.metadata_fields.title)"
                                        v-if="resultType == 'doc' && philoConfig.metadata.indexOf('title') !== -1"
                                    />
                                    <citations :citation="result.citation"></citations>
                                </span>
                            </b-col>
                        </b-row>
                    </b-card>
                </transition-group>
            </b-col>
            <b-col cols="12" md="7" xl="8" v-if="philoConfig.dictionary_bibliography && results.result_type != 'doc'">
                <b-card
                    no-body
                    class="philologic-occurrence ml-2 mr-2 mb-4 shadow-sm"
                    v-for="(group, groupKey) in results.results"
                    :key="groupKey"
                >
                    <b-list-group flush>
                        <b-list-group-item v-for="(result, index) in group" :key="index">
                            <div class="citation-dico-container">
                                <span class="cite" :data-id="result.philo_id.join(' ')">
                                    <span class="number" style="margin-left: -1.25rem; margin-top: -5rem">{{
                                        results.description.start + index
                                    }}</span>
                                    <citations :citation="result.citation"></citations>
                                </span>
                            </div>
                            <div
                                class="philologic_context text-content-area pt-4 px-1 text-justify"
                                select-word
                                :position="result.position"
                            >
                                <div v-html="result.context"></div>
                            </div>
                        </b-list-group-item>
                    </b-list-group>
                </b-card>
            </b-col>
            <b-col md="5" xl="4">
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
    name: "bibliography",
    components: {
        citations,
        conckwic,
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
    data() {
        return {
            philoConfig: this.$philoConfig,
            results: {},
            resultType: "doc",
            metadataAddition: [],
        };
    },
    created() {
        this.report = "bibliography";
        this.currentReport = "bibliography";
        this.fetchResults();
        EventBus.$on("urlUpdate", () => {
            this.fetchResults();
        });
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
                        this.$store.commit("updateDescription", {
                            ...this.description,
                            start: this.results.description.start,
                            end: this.results.description.end,
                            results_per_page: this.results.description.results_per_page,
                        });
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
            EventBus.$emit("metadataUpdate", { title: newTitleValue });
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
