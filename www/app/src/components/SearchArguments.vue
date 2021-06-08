<template>
    <div id="search-arguments" class="pb-2">
        <div v-if="currentWordQuery !== ''">
            Searching database for the term(s)
            <span v-if="approximate == 'yes'">
                <b>{{ currentWordQuery }}</b> and the following similar terms:
            </span>
            <span v-if="approximate.length == 0 || approximate == 'no'"></span>
            <span class="rounded-pill term-groups" v-for="(group, index) in wordGroups" :key="index">
                <a class="term-group-word" href @click.prevent="getQueryTerms(group, index)">{{ group }}</a>
                <span class="close-pill" @click="removeTerm(index)">X</span>
            </span>
            {{ queryArgs.proximity }}
            <div class="card outline-secondary shadow" id="query-terms" style="display: none">
                <button type="button" class="btn btn-secondary btn-sm close" @click="closeTermsList()">
                    <span aria-hidden="true">&times;</span>
                </button>
                <h6 class="pe-4">The search terms query expanded to the following {{ words.length }} terms:</h6>
                <h6 v-if="words.length > 100">100 most frequent terms displayed</h6>
                <button
                    type="button"
                    class="btn btn-secondary btn-sm"
                    style="margin: 10px 0px"
                    v-if="wordListChanged"
                    @click="rerunQuery()"
                >
                    Rerun query with the current modifications
                </button>
                <div class="row" id="query-terms-list">
                    <div class="col-3" v-for="word in words" :key="word">
                        <button class="rounded-pill term-groups">
                            <span class="px-2">{{ word.replace(/"/g, "") }}</span>
                            <span class="close-pill pe-1" @click="removeFromTermsList(word, groupIndexSelected)"
                                >X</span
                            >
                        </button>
                    </div>
                </div>
            </div>
        </div>
        <div>
            Bibliography criteria:
            <span class="metadata-args rounded-pill" v-for="metadata in queryArgs.biblio" :key="metadata.key">
                <span class="metadata-label">{{ metadata.alias }}</span>
                <span class="metadata-value">{{ metadata.value }}</span>
                <span class="remove-metadata" @click="removeMetadata(metadata.key, restart)">X</span>
            </span>
            <b v-if="queryArgs.biblio.length === 0">None</b>
        </div>
        <div v-if="queryReport === 'time_series'">
            {{ resultsLength }} occurrences of the term(s) between
            <span class="biblio-criteria">
                <span class="metadata-args rounded-pill">
                    <span class="metadata-value">{{ start_date }}</span>
                    <span class="remove-metadata" @click="removeMetadata('start_date', restart)">X</span>
                </span> </span
            >&nbsp; and
            <span class="biblio-criteria">
                <span class="metadata-args rounded-pill">
                    <span class="metadata-value">{{ end_date }}</span>
                    <span class="remove-metadata" @click="removeMetadata('end_date', restart)">X</span>
                </span>
            </span>
        </div>
        <div style="margin-top: 10px" v-if="queryReport === 'collocation'">
            Displaying the top 100 collocates for {{ resultsLength }} occurrences
        </div>
    </div>
</template>
<script>
import { mapFields } from "vuex-map-fields";
import { EventBus } from "../main.js";

export default {
    name: "searchArguments",
    props: ["resultStart", "resultEnd"],
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
            "formData.start_date",
            "formData.end_date",
            "currentReport",
            "resultsLength",
            "description",
        ]),
        formData() {
            return this.$store.state.formData;
        },
        wordGroups() {
            return this.description.termGroups;
        },
    },
    data() {
        return {
            currentWordQuery: typeof this.$route.query.q == "undefined" ? "" : this.$route.query.q,
            queryArgs: {},
            words: [],
            wordListChanged: false,
            restart: false,
            queryReport: this.$route.name,
            termGroupsCopy: [],
        };
    },
    created() {
        this.fetchSearchArgs();
        EventBus.$on("resultsDone", () => {
            this.fetchSearchArgs();
        });
    },
    watch: {
        // call again the method if the route changes
        $route: "fetchSearchArgs",
    },
    methods: {
        fetchSearchArgs() {
            this.queryReport = this.$route.name;
            this.currentWordQuery = typeof this.$route.query.q == "undefined" ? "" : this.$route.query.q;
            let queryParams = { ...this.$store.state.formData };
            if ("q" in queryParams) {
                this.queryArgs.queryTerm = queryParams.q;
            } else {
                this.queryArgs.queryTerm = "";
            }
            this.queryArgs.biblio = this.buildCriteria();

            if ("q" in queryParams) {
                let method = queryParams.method;
                if (typeof method === "undefined") {
                    method = "proxy";
                }
                if (queryParams.q.split(" ").length > 1) {
                    if (method === "proxy") {
                        if (typeof queryParams.arg_proxy !== "undefined" || queryParams.arg_proxy) {
                            this.queryArgs.proximity = "within " + queryParams.arg_proxy + " words";
                        } else {
                            this.queryArgs.proximity = "";
                        }
                    } else if (method === "phrase") {
                        if (typeof queryParams.arg_proxy !== "undefined" || queryParams.arg_phrase) {
                            this.queryArgs.proximity = "within exactly " + queryParams.arg_phrase + " words";
                        } else {
                            this.queryArgs.proximity = "";
                        }
                    } else if (method === "cooc") {
                        this.queryArgs.proximity = "in the same sentence";
                    }
                } else {
                    this.queryArgs.proximity = "";
                }
            }
            if (queryParams.approximate == "yes") {
                this.queryArgs.approximate = true;
            } else {
                this.queryArgs.approximate = false;
            }
            this.$http
                .get(`${this.$dbUrl}/scripts/get_term_groups.py`, {
                    params: this.paramsFilter({ ...this.$route.query }),
                })
                .then((response) => {
                    this.$store.commit("updateDescription", {
                        ...this.description,
                        start: this.resultStart,
                        end: this.resultEnd,
                        results_per_page: this.formData.results_per_page,
                        termGroups: response.data.term_groups,
                    });
                    this.originalQuery = response.data.original_query;
                })
                .catch((error) => {
                    this.loading = false;
                    this.error = error.toString();
                    this.debug(this, error);
                });
        },
        buildCriteria() {
            let queryArgs = {};
            for (let field of this.$philoConfig.metadata) {
                if (field in this.$route.query && this.formData[field].length > 0) {
                    queryArgs[field] = this.formData[field];
                }
            }
            let biblio = [];
            if (queryArgs.report === "time_series") {
                delete queryArgs[this.$philoConfig.time_series_year_field];
            }
            let config = this.$philoConfig;
            let facets = [];
            for (let i = 0; i < config.facets.length; i++) {
                let alias = Object.keys(config.facets[i])[0];
                let facet = config.facets[i][alias];
                if (typeof facet == "string") {
                    facets.push(facet);
                } else {
                    //facets.push(facet)
                    for (let value of facets) {
                        if (facets.indexOf(value) < 0) {
                            facets.push(value);
                        }
                    }
                }
            }
            for (let k in queryArgs) {
                if (config.available_metadata.indexOf(k) >= 0) {
                    if (this.report == "time_series" && k == "year") {
                        continue;
                    }
                    let v = queryArgs[k];
                    let alias = k;
                    if (v) {
                        if (k in config.metadata_aliases) {
                            alias = config.metadata_aliases[k];
                        }
                        biblio.push({ key: k, alias: alias, value: v });
                    }
                }
            }
            return biblio;
        },
        removeMetadata(metadata) {
            if (this.q.length == 0 && this.currentReport != "aggregation") {
                this.report = "bibliography";
            }
            this.start = "";
            this.end = "";
            let localParams = this.copyObject(this.formData);
            localParams[metadata] = "";
            this.$router.push(this.paramsToRoute(localParams));
        },
        getQueryTerms(group, index) {
            this.groupIndexSelected = index;
            this.$http
                .get(`${this.$dbUrl}/scripts/get_query_terms.py`, {
                    params: {
                        q: group,
                        approximate: 0,
                        ...this.paramsFilter(this.$route.query),
                    },
                })
                .then((response) => {
                    this.words = response.data;
                    document.querySelector("#query-terms").style.display = "block";
                })
                .catch((error) => {
                    this.error = error.toString();
                    this.debug(this, error);
                });
        },
        closeTermsList() {
            document.querySelector("#query-terms").style.display = "none";
        },
        removeFromTermsList(word, groupIndex) {
            var index = this.words.indexOf(word);
            this.words.splice(index, 1);
            this.wordListChanged = true;
            if (this.termGroupsCopy.length == 0) {
                this.termGroupsCopy = this.copyObject(this.wordGroups);
            }
            if (this.termGroupsCopy[groupIndex].indexOf(" NOT ") !== -1) {
                // if there's already a NOT in the clause add an OR
                this.termGroupsCopy[groupIndex] += " | " + word.trim();
            } else {
                this.termGroupsCopy[groupIndex] += " NOT " + word.trim();
            }
            this.q = this.termGroupsCopy.join(" ");
            this.approximate = "no";
            this.approximate_ratio = "";
        },
        rerunQuery() {
            this.$router.push(this.paramsToRoute({ ...this.$store.state.formData, q: this.q }));
        },
        removeTerm(index) {
            let queryTermGroup = this.copyObject(this.description.termGroups);
            queryTermGroup.splice(index, 1);
            this.q = queryTermGroup.join(" ");
            if (queryTermGroup.length === 0 && this.currentReport != "aggregation") {
                this.report = "bibliography";
            }
            this.start = 0;
            this.end = 0;
            if (queryTermGroup.length == 1) {
                this.method = "proxy";
                this.arg_proxy = "";
                this.arg_phrase = "";
            }
            this.$store.commit("updateDescription", {
                ...this.description,
                termGroups: queryTermGroup,
            });
            this.$router.push(this.paramsToRoute({ ...this.$store.state.formData }));
        },
    },
};
</script>
<style scoped>
#search-arguments {
    line-height: 180%;
}
#query-terms {
    position: absolute;
    z-index: 100;
    padding: 10px 15px 0px 15px;
    box-shadow: 0px 0.2em 8px 0.01em rgba(0, 0, 0, 0.1);
}

#query-terms > button:first-child {
    position: absolute;
    right: 2px;
    top: 0;
}

#query-terms-list {
    margin: 10px -5px;
    max-height: 400px;
    max-width: 800px;
    overflow-y: scroll;
}

.query-terms-element {
    padding: 0px 20px 0px 5px;
    text-align: center;
    width: fit-content;
}
.close {
    position: absolute;
    right: 0;
}
.term-groups {
    display: inline-block;
    position: relative;
    border: 1px solid #ddd;
    line-height: 2;
    padding: 0 25px 0 0;
    margin: 5px 5px 5px 0px;
    white-space: inherit;
    background-color: #fff;
}
.term-group-word {
    display: inline-block;
    border-radius: 50rem 0 0 50rem !important;
    height: 100%;
    width: 100%;
    padding-left: 0.5rem;
}
.term-group-word:hover {
    background-color: #e9ecef;
    color: initial;
}
.close-pill {
    position: absolute;
    right: 0;
    top: 0;
    padding-left: 0.5rem;
    width: 1.6rem;
    border-radius: 0 50rem 50rem 0 !important;
    display: inline-block;
    border-left: solid 1px #888;
}
.metadata-args {
    border: 1px solid #ddd;
    display: inline-flex !important;
    margin-right: 5px;
    border-radius: 50rem;
    width: fit-content;
    line-height: 2;
    margin-bottom: 0.5rem;
}
.metadata-label {
    background-color: #e9ecef;
    border: solid #ddd;
    border-width: 0 1px 0 0;
    border-top-left-radius: 50rem;
    border-bottom-left-radius: 50rem;
    padding: 0 0.5rem;
}
.metadata-value {
    -webkit-box-decoration-break: clone;
    box-decoration-break: clone;
    padding: 0 0.5rem;
}
.remove-metadata {
    padding-right: 5px;
    padding-left: 5px;
    border-left: #ddd solid 1px;
    border-top-right-radius: 50rem;
    border-bottom-right-radius: 50rem;
    padding: 0 0.5rem;
}
.remove-metadata:hover,
.close-pill:hover {
    background-color: #e9ecef;
    cursor: pointer;
}
.rounded-pill a {
    margin-right: 0.5rem;
    text-decoration: none;
}
.metadata-label,
.metadata-value,
.remove-metadata {
    display: flex;
    align-items: center;
}
</style>
