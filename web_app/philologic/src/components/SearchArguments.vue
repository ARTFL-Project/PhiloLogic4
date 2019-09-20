<template>
    <div id="search-arguments" class="p-3">
        <div v-if="q !== ''">
            Searching database for
            <span v-if="approximate == 'yes'">
                <b>{{ q }}</b> and the following similar terms:
            </span>
            <span v-if="approximate.length == 0 || approximate == 'no'"></span>
            <b-button
                variant="outline-secondary"
                pill
                size="sm"
                class="term-groups"
                v-for="(group, index) in description.termGroups"
                :key="index"
            >
                <a href @click.prevent="getQueryTerms(group, index)">{{ group }}</a>
                <span class="close-pill" @click="removeTerm(index)">X</span>
            </b-button>
            {{ queryArgs.proximity }}
            <b-card no-body variant="outline-secondary" id="query-terms" style="display: none;">
                <b-button size="sm" class="close" @click="closeTermsList()">
                    <span aria-hidden="true">&times;</span>
                    <span class="sr-only">Close</span>
                </b-button>
                <h4>The search terms query expanded to the following {{ words.length }} terms:</h4>
                <h6 v-if="words.length > 100">100 most frequent terms displayed</h6>
                <b-button
                    size="sm"
                    style="margin:10px 0px"
                    v-if="wordListChanged"
                    @click="rerunQuery()"
                >Rerun query with the current modifications</b-button>
                <b-row id="query-terms-list">
                    <b-col cols="3" v-for="word in words" :key="word">
                        <b-card no-body class="query-terms-element">
                            {{ word }}
                            <b-button
                                size="sm"
                                class="close"
                                @click="removeFromTermsList(word, groupIndexSelected)"
                            >
                                <span aria-hidden="true">&times;</span>
                                <span class="sr-only">Close</span>
                            </b-button>
                        </b-card>
                    </b-col>
                </b-row>
            </b-card>
        </div>
        <div style="margin-top: 5px;">
            Bibliography criteria:
            <span
                class="metadata-args rounded-pill"
                v-for="metadata in queryArgs.biblio"
                :key="metadata.key"
            >
                <span class="metadata-label">{{ metadata.alias }}</span>
                <span class="remove-metadata" @click="removeMetadata(metadata.key, restart)">X</span>
                <span class="metadata-value">{{ metadata.value }}</span>
            </span>
            <b v-if="queryArgs.biblio.length === 0">None</b>
        </div>
        <div v-if="currentReport === 'time_series'">
            {{ resultsLength || '...' }} occurrences of the term(s) between
            <span
                class="biblio-criteria"
            >
                <span class="metadata-args rounded-pill">
                    <span class="remove-metadata" @click="removeMetadata('start_date', restart)">X</span>
                    <span class="metadata-value">{{ start_date }}</span>
                </span>
            </span>&nbsp; and
            <span class="biblio-criteria">
                <span class="metadata-args rounded-pill">
                    <span class="remove-metadata" @click="removeMetadata('end_date', restart)">X</span>
                    <span class="metadata-value">{{ end_date }}</span>
                </span>
            </span>
        </div>
        <div
            style="margin-top: 10px;"
            v-if="currentReport === 'collocation'"
        >Displaying the top 100 collocates for {{ resultsLength || '...' }} occurrences</div>
    </div>
</template>
<script>
import { mapFields } from "vuex-map-fields";
import { EventBus } from "../main.js";

export default {
    name: "searchArguments",
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
            "description"
        ]),
        formData() {
            return this.$store.state.formData;
        }
    },
    data() {
        return {
            queryArgs: {},
            words: [],
            wordListChanged: false,
            restart: false
        };
    },
    created() {
        this.fetchSearchArgs();
        EventBus.$on("resultsDone", () => {
            this.fetchSearchArgs();
        });
    },
    methods: {
        fetchSearchArgs() {
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
                        if (
                            typeof queryParams.arg_proxy !== "undefined" ||
                            queryParams.arg_proxy
                        ) {
                            this.queryArgs.proximity =
                                "within " + queryParams.arg_proxy + " words";
                        } else {
                            this.queryArgs.proximity = "";
                        }
                    } else if (method === "phrase") {
                        if (
                            typeof queryParams.arg_proxy !== "undefined" ||
                            queryParams.arg_phrase
                        ) {
                            this.queryArgs.proximity =
                                "within exactly " +
                                queryParams.arg_phrase +
                                " words";
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
                .get(
                    "http://anomander.uchicago.edu/philologic/frantext0917/scripts/get_term_groups.py",
                    { params: this.paramsFilter({ ...this.$route.query }) }
                )
                .then(response => {
                    this.$store.commit("updateDescription", {
                        ...this.description,
                        termGroups: response.data.term_groups
                    });
                    this.originalQuery = response.data.original_query;
                })
                .catch(error => {
                    this.loading = false;
                    this.error = error.toString();
                    console.log(error);
                });
        },
        buildCriteria() {
            let queryArgs = {};
            for (let field of this.$philoConfig.metadata) {
                if (this.formData[field].length > 0) {
                    queryArgs[field] = this.formData[field];
                }
            }
            let biblio = [];
            if (queryArgs.report === "time_series") {
                delete queryParams[this.$philoConfig.time_series_year_field];
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
            this.$store.commit("updateMetadataField", {
                key: metadata,
                value: ""
            });
            if (this.q.length == 0) {
                this.report = "bibliography";
            }
            this.start = "";
            this.end = "";
            if (
                this.report === "concordance" ||
                this.report === "kwic" ||
                this.report === "bibliography"
            ) {
                this.$router.push(
                    this.paramsToRoute(this.$store.state.formData)
                );
            } else if (
                this.report === "collocation" ||
                this.report === "time_series"
            ) {
                this.$router.push(
                    this.paramsToRoute(this.$store.state.formData)
                );
            }
        },
        getQueryTerms(group, index) {
            this.groupIndexSelected = index;
            this.$http
                .get(
                    "http://anomander.uchicago.edu/philologic/frantext0917/scripts/get_query_terms.py",
                    {
                        params: {
                            q: group,
                            approximate: 0,
                            ...this.paramsFilter(this.$route.query)
                        }
                    }
                )
                .then(response => {
                    this.words = response.data;
                    document.querySelector("#query-terms").style.display =
                        "block";
                })
                .catch(error => {
                    this.error = error.toString();
                    console.log(error);
                });
        },
        closeTermsList() {
            document.querySelector("#query-terms").style.display = "none";
        },
        removeFromTermsList(word, groupIndex) {
            var index = this.words.indexOf(word);
            this.words.splice(index, 1);
            this.wordListChanged = true;
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
            this.$router.push(this.paramsToRoute(this.$store.state.formData));
        },
        removeTerm(index) {
            let queryTermGroup = this.copyObject(this.description.termGroups);
            queryTermGroup.splice(index, 1);
            this.q = queryTermGroup.join(" ");
            if (queryTermGroup.length === 0) {
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
                termGroups: queryTermGroup
            });
            this.$router.push(this.paramsToRoute(this.$store.state.formData));
        }
    }
};
</script>
<style thisd>
#search-arguments {
    line-height: 180%;
}
#query-terms {
    position: absolute;
    z-index: 100;
    padding: 20px 15px 0px 15px;
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
}
.close {
    position: absolute;
    right: 0;
}
.term-groups {
    display: inline-block;
    position: relative;
    padding: 3px 20px 3px 10px;
    margin: 5px 5px 5px 0px;
    white-space: inherit;
}
.term-groups:hover {
    background-color: #e9ecef;
    color: initial;
}
.close-pill {
    position: absolute;
    right: 5px;
    top: 4px;
}
.close-pill:hover {
    color: #000;
}
.metadata-args {
    border: 1px solid #ddd;
    display: inline-block !important;
    margin-top: 20px;
    margin-right: 5px;
}
.metadata-label {
    background-color: #e9ecef;
    border: solid #ddd;
    border-width: 0 1px 0 0;
    border-top-left-radius: 50rem;
    border-bottom-left-radius: 50rem;
    float: left;
    line-height: 29px;
    padding: 0 5px 0 10px;
}
.metadata-value {
    -webkit-box-decoration-break: clone;
    box-decoration-break: clone;
    line-height: 29px;
    padding: 6px 10px 10px;
}
.remove-metadata {
    float: right;
    padding-right: 5px;
    padding-left: 5px;
    border-left: #ddd solid 1px;
}
.remove-metadata:hover {
    background-color: #e9ecef;
    cursor: pointer;
    border-top-right-radius: 50rem;
    border-bottom-right-radius: 50rem;
}
</style>
