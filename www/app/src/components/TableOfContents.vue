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
                    <div class="card mt-4 mb-4 p-4 d-inline-block shadow" style="width: 100%; text-align: justify">
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
                            <div id="toc-content" v-scroll="handleScroll">
                                <div v-for="(element, elIndex) in tocElements.slice(0, displayLimit)" :key="elIndex">
                                    <div :class="'toc-' + element.philo_type">
                                        <span :class="'bullet-point-' + element.philo_type"></span>
                                        <citations :citation="element.citation"></citations>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
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
            displayLimit: 200,
            teiHeader: "",
            tocObject: {},
            tocElements: [],
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
                    this.tocElements = response.data.toc;
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
        handleScroll() {
            let scrollPosition = document.getElementById("toc-content").getBoundingClientRect().bottom - 200;
            if (scrollPosition < window.innerHeight) {
                console.log("adding more");
                this.displayLimit += 200;
            }
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
