<template>
    <div class="container-fluid mt-4">
        <b-row id="toc-report-title" class="text-center pt-4">
            <b-col offset="2" cols="8">
                <h5>
                    <span
                        class="citation"
                        v-for="(citation, citeIndex) in textNavigationCitation"
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
                                v-if="citeIndex != textNavigationCitation.length - 1"
                            >&#9679;</span>
                        </span>
                        <span v-if="!citation.href">
                            <span v-html="citation.prefix"></span>
                            <span :style="citation.style">{{ citation.label }}</span>
                            <span v-html="citation.suffix"></span>
                            <span
                                class="separator"
                                v-if="citeIndex != textNavigationCitation.length - 1"
                            >&#9679;</span>
                        </span>
                    </span>
                </h5>
            </b-col>
        </b-row>
        <div class="text-center">
            <b-row>
                <b-col
                    cols="12"
                    sm="10"
                    md="8"
                    lg="6"
                    xl="4"
                    offset-sm="1"
                    offset-md="2"
                    offset-lg="3"
                    offset-xl="4"
                >
                    <b-card
                        no-body
                        class="mt-4 p-4 d-inline-block text-justify shadow"
                        style="width: 100%"
                    >
                        <button
                            id="show-header"
                            class="btn btn-primary"
                            v-if="philoConfig.header_in_toc"
                            @click="showHeader()"
                        >{{ headerButton }}</button>
                        <div
                            id="tei-header"
                            class="panel panel-default tei-header velocity-opposites-transition-slideDownIn"
                            data-velocity-opts="{duration: 200}"
                            v-if="teiHeader"
                            v-html="teiHeader | unsafe"
                        ></div>
                        <div id="toc-report" class="text-content-area" loading="loading">
                            <div
                                id="toc-content"
                                infinite-scroll="getMoreItems()"
                                infinite-scroll-distance="4"
                            >
                                <div v-for="(element, elIndex) in tocObject.toc" :key="elIndex">
                                    <div :class="'toc-' + element.philo_type">
                                        <span :class="'bullet-point-' + element.philo_type"></span>
                                        <router-link
                                            :to="'/' + element.href"
                                            class="toc-section"
                                        >{{ element.label }}</router-link>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </b-card>
                </b-col>
            </b-row>
        </div>
        <!-- <access-control v-if="!authorized"></access-control> -->
    </div>
</template>
<script>
import { mapFields } from "vuex-map-fields";
import searchArguments from "./SearchArguments";
import { EventBus } from "../main.js";

export default {
    name: "tableOfContents",
    components: {
        searchArguments
    },
    computed: {
        ...mapFields({
            report: "formData.report",
            textNavigationCitation: "textNavigationCitation"
        })
    },
    data() {
        return {
            philoConfig: this.$philoConfig,
            authorized: true,
            displayLimit: 50,
            loading: true,
            tocObject: {}
        };
    },
    created() {
        this.fetchToC();
    },
    methods: {
        fetchToC() {
            this.loading = true;
            var vm = this;
            this.$http
                .get(
                    "http://anomander.uchicago.edu/philologic/test/reports/table_of_contents.py",
                    { params: { philo_id: vm.$route.params.pathInfo } }
                )
                .then(function(response) {
                    vm.loading = false;
                    vm.tocObject = response.data;
                    vm.textNavigationCitation = response.data.citation;
                })
                .catch(function(response) {
                    vm.loading = false;
                    console.log(response);
                });

            vm.headerButton = "Show Header";
            vm.teiHeader = false;
        },
        showHeader() {
            if (angular.isString(vm.teiHeader)) {
                vm.teiHeader = false;
                vm.headerButton = "Show Header";
            } else {
                var UrlString = {
                    script: "get_header.py",
                    philo_id: vm.philoID
                };
                request.script(UrlString).then(function(response) {
                    vm.teiHeader = response.data;
                    vm.headerButton = "Hide Header";
                });
            }
        },
        getMoreItems() {
            this.displayLimit += 200;
        }
    }
};
</script>
<style scoped>
.separator {
    padding: 5px;
    font-size: 60%;
    display: inline-block;
    vertical-align: middle;
}
.toc-section {
    font-size: 1.05rem;
}
</style>
