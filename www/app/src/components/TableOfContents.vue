<template>
    <div class="container-fluid mt-4">
        <b-row id="toc-report-title" class="text-center pt-4">
            <b-col offset="2" cols="8">
                <h5>
                    <citations :citation="textNavigationCitation"></citations>
                </h5>
            </b-col>
        </b-row>
        <div class="text-center">
            <b-row>
                <b-col cols="12">
                    <b-card no-body class="mt-4 mb-4 p-4 d-inline-block text-justify shadow" style="width: 100%">
                        <b-button
                            id="show-header"
                            class="mb-2"
                            variant="outline-secondary"
                            v-if="philoConfig.header_in_toc"
                            @click="toggleHeader()"
                            >{{ headerButton }}</b-button
                        >
                        <b-card no-body id="tei-header" class="shadow-sm" v-if="showHeader" v-html="teiHeader"></b-card>
                        <div id="toc-report" class="text-content-area">
                            <div id="toc-content" infinite-scroll="getMoreItems()" infinite-scroll-distance="4">
                                <div v-for="(element, elIndex) in tocObject.toc" :key="elIndex">
                                    <div :class="'toc-' + element.philo_type">
                                        <span :class="'bullet-point-' + element.philo_type"></span>
                                        <router-link :to="'/' + element.href" class="toc-section">{{
                                            element.label
                                        }}</router-link>
                                        <citations :citation="element.citation"></citations>
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
import citations from "./Citations";
import searchArguments from "./SearchArguments";

export default {
    name: "tableOfContents",
    components: {
        citations,
        searchArguments,
    },
    computed: {
        ...mapFields({
            report: "formData.report",
            textNavigationCitation: "textNavigationCitation",
            searching: "searching",
        }),
    },
    data() {
        return {
            philoConfig: this.$philoConfig,
            authorized: true,
            displayLimit: 50,
            teiHeader: "",
            tocObject: {},
            showHeader: false,
            headerButton: "Show Header",
        };
    },
    created() {
        this.fetchToC();
    },
    methods: {
        fetchToC() {
            this.searching = true;
            this.$http
                .get(`${this.$dbUrl}/reports/table_of_contents.py`, {
                    params: { philo_id: this.$route.params.pathInfo },
                })
                .then((response) => {
                    this.searching = false;
                    this.tocObject = response.data;
                    this.textNavigationCitation = response.data.citation;
                })
                .catch((error) => {
                    this.searching = false;
                    this.debug(this, error);
                });
        },
        toggleHeader() {
            if (!this.showHeader) {
                if (this.teiHeader.length == 0) {
                    this.$http
                        .get(`${this.$dbUrl}/scripts/get_header.py`, {
                            params: {
                                philo_id: this.$route.params.pathInfo,
                            },
                        })
                        .then((response) => {
                            this.teiHeader = response.data;
                            this.headerButton = "Hide Header";
                            this.showHeader = true;
                        })
                        .catch((error) => {
                            this.debug(this, error);
                        });
                } else {
                    this.headerButton = "Hide Header";
                    this.showHeader = true;
                }
            } else {
                this.headerButton = "Show Header";
                this.showHeader = false;
            }
        },
        getMoreItems() {
            this.displayLimit += 200;
        },
    },
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
#tei-header {
    white-space: pre;
    font-family: monospace;
    font-size: 120%;
    overflow-x: scroll;
    padding: 10px;
    background-color: rgb(253, 253, 253);
    margin: 10px;
}
</style>
