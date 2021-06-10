<template>
    <div class="container-fluid mt-4">
        <div class="row text-center pt-4" id="toc-report-title">
            <div class="col-8 offset-2">
                <h5>
                    <citations :citation="textNavigationCitation"></citations>
                </h5>
            </div>
        </div>
        <div class="text-center">
            <div class="row">
                <div class="col-12">
                    <div class="card mt-4 mb-4 p-4 d-inline-block text-justify shadow" style="width: 100%">
                        <button
                            id="show-header"
                            class="btn btn-outline-secondary mb-2"
                            v-if="philoConfig.header_in_toc"
                            @click="toggleHeader()"
                        >
                            {{ headerButton }}
                        </button>
                        <div class="card shadow-sm" no-body id="tei-header" v-if="showHeader" v-html="teiHeader"></div>
                        <div id="toc-report" class="text-content-area">
                            <div id="toc-content" infinite-scroll="getMoreItems()" infinite-scroll-distance="4">
                                <div v-for="(element, elIndex) in tocObject.toc" :key="elIndex">
                                    <div :class="'toc-' + element.philo_type">
                                        <span :class="'bullet-point-' + element.philo_type"></span>
                                        <router-link :to="element.href" class="toc-section">{{
                                            element.label
                                        }}</router-link>
                                        <citations :citation="element.citation"></citations>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <!-- <access-control v-if="!authorized"></access-control> -->
    </div>
</template>
<script>
import { mapFields } from "vuex-map-fields";
import citations from "./Citations";

export default {
    name: "tableOfContents",
    components: {
        citations,
    },
    inject: ["$http"],
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
