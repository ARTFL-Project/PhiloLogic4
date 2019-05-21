<template>
    <div id="search-arguments" class="p-3">
        <div v-if="queryArgs.queryTerm !== ''">
            <span v-if="queryArgs.approximate">
                Searching database for
                <b>{{ originalQuery }}</b> and the following similar terms:
            </span>
            <span v-if="!queryArgs.approximate">
                Searching database for
                <span
                    v-if="typeof(termGroups) === 'undefined'"
                >{{ queryArgs.queryTerm }}</span>
            </span>
            <b-button
                variant="outline-secondary"
                pill
                size="sm"
                class="term-groups"
                v-for="(group, index) in termGroups"
                :key="index"
            >
                <a href @click.prevent="getQueryTerms(group, index)">{{ group }}</a>
                <span style="position: absolute; right: 3px; top: 5px" @click="removeTerm(index)">X</span>
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
                class="biblio-criteria"
                v-for="metadata in queryArgs.biblio"
                :key="metadata.key"
                style="margin: 1px"
            >
                {{ metadata.alias }} :
                <b>{{ metadata.value }}</b>
                <span
                    class="glyphicon glyphicon-remove-circle"
                    @click="removeMetadata(metadata.key, formData, restart)"
                ></span>
            </span>
            <b v-if="queryArgs.biblio.length === 0">None</b>
        </div>
        <div v-if="queryArgs.report === 'time_series'">
            {{ timeSeries.resultsLength || '...' }} occurrences of the term(s) between
            <span
                class="biblio-criteria"
            >
                <b>{{ startDate }}</b>
                <span
                    class="glyphicon glyphicon-remove-circle"
                    @click="removeMetadata('start_date', formData, restart)"
                ></span>
            </span>&nbsp; and
            <span class="biblio-criteria">
                <b>{{ endDate }}</b>
                <span
                    class="glyphicon glyphicon-remove-circle"
                    @click="removeMetadata('end_date', formData, restart)"
                ></span>
            </span>
        </div>
        <div
            style="margin-top: 10px;"
            v-if="queryArgs.report === 'collocation'"
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
            "formData.approximate",
            "formData.approximate_ratio"])
    },
    data() {
        return {
            philoConfig: this.$philoConfig,
            queryArgs: {},
            queryTermGroups: [],
            termGroups: [],
            words: [],
            wordListChanged: false,
        }
    },
    created() {
        this.fetchSearchArgs()
        var vm = this
        EventBus.$on("urlUpdate", function () {
            vm.fetchSearchArgs()
        })
    },
    methods: {
        fetchSearchArgs() {
            let queryParams = { ...this.$route.query }
            if ('q' in queryParams) {
                this.queryArgs.queryTerm = queryParams.q;
            } else {
                this.queryArgs.queryTerm = '';
            }
            this.queryArgs.biblio = this.buildCriteria(queryParams);

            if ('q' in queryParams) {
                let method = queryParams.method;
                if (typeof (method) === 'undefined') {
                    method = 'proxy';
                }
                if (queryParams.q.split(' ').length > 1) {
                    if (method === "proxy") {
                        if (typeof (queryParams.arg_proxy) !== 'undefined' || queryParams.arg_proxy) {
                            this.queryArgs.proximity = 'within ' + queryParams.arg_proxy + ' words';
                        } else {
                            this.queryArgs.proximity = '';
                        }
                    } else if (method === 'phrase') {
                        if (typeof (queryParams.arg_proxy) !== 'undefined' || queryParams.arg_phrase) {
                            this.queryArgs.proximity = 'within exactly ' + queryParams.arg_phrase + ' words';
                        } else {
                            this.queryArgs.proximity = ''
                        }
                    } else if (method === 'cooc') {
                        this.queryArgs.proximity = 'in the same sentence';
                    }
                } else {
                    this.queryArgs.proximity = '';
                }
            }
            if (queryParams.approximate == "yes") {
                this.queryArgs.approximate = true;
            } else {
                this.queryArgs.approximate = false;
            }


            this.$http.get("http://anomander.uchicago.edu/philologic/test/scripts/get_term_groups.py", { params: this.paramsFilter({ ...this.$route.query }) })
                .then(response => {
                    this.termGroups = response.data.term_groups
                    this.originalQuery = response.data.original_query
                    this.queryTermGroups.group = this.copyObject(this.termGroups)
                    this.termGroupsCopy = this.copyObject(this.termGroups)
                })
                .catch(error => {
                    this.loading = false;
                    this.error = error.toString();
                    console.log(error);
                });
        },
        buildCriteria(queryParams) {
            let queryArgs = this.copyObject(queryParams)
            let biblio = []
            if (queryArgs.report === "time_series") {
                delete queryParams[this.philoConfig.time_series_year_field];
            }
            let config = this.philoConfig;
            let facets = [];
            for (let i = 0; i < config.facets.length; i++) {
                let alias = Object.keys(config.facets[i])[0];
                let facet = config.facets[i][alias];
                if (typeof (facet) == "string") {
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
            return biblio
        },
        removeMetadata(metadata, queryParams, restart) {
            delete queryParams[metadata];
            if (!queryParams.q) {
                queryParams.report = 'bibliography';
            }
            queryParams.start = 0;
            queryParams.end = 0;
            if (this.report === "concordance" || this.report === "kwic" || this.report === "bibliography") {
                this.$router.push(`http://anomander.uchicago.edu/philologic/test/${this.paramsToUrl(queryParams)}`);
            } else if (queryParams.report === "collocation" || queryParams.report === "time_series") {
                this.$router.push(`http://anomander.uchicago.edu/philologic/test/${this.paramsToUrl(queryParams)}`);
                // $rootthis.formData = queryParams;
                restart = true;
            }
        },
        getQueryTerms(group, index) {
            console.log("haaa")
            var vm = this
            this.groupIndexSelected = index
            this.$http.get("http://anomander.uchicago.edu/philologic/test/scripts/get_query_terms.py", { params: { q: group, approximate: 0, ...this.paramsFilter(this.$route.query) } })
                .then(function (response) {
                    vm.words = response.data;
                    document.querySelector('#query-terms').style.display = "block"
                }).catch(error => {
                    this.error = error.toString();
                    console.log(error);
                });
        },
        closeTermsList() {
            document.querySelector('#query-terms').style.display = "none"
        },
        removeFromTermsList(word, groupIndex) {
            var index = this.words.indexOf(word);
            this.words.splice(index, 1);
            this.wordListChanged = true;
            if (this.termGroupsCopy[groupIndex].indexOf(' NOT ') !== -1) { // if there's already a NOT in the clause add an OR
                this.termGroupsCopy[groupIndex] += ' | ' + word.trim();
            } else {
                this.termGroupsCopy[groupIndex] += ' NOT ' + word.trim();
            }
            this.q = this.termGroupsCopy.join(' ');
            this.approximate = "no";
            this.approximate_ratio = "";
        },
        rerunQuery() {
            this.$router.push(this.paramsToRoute(this.$store.state.formData))
            EventBus.$emit("urlUpdate")
        },
        removeTerm(index) {
            this.termGroups.splice(index, 1)
            this.queryTermGroups.group = this.copyObject(this.termGroups)
            this.$store.state.formData.q = this.termGroups.join(' ')
            if (this.termGroups.length === 0) {
                this.$store.state.formData.report = "bibliography"
            }
            this.$store.state.formData.start = 0
            this.$store.state.formData.end = 0
            this.$router.push(this.paramsToRoute(this.$store.state.formData))
            EventBus.$emit("urlUpdate")
        }
    }

}
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
    padding: 3px 20px 3px 3px;
    margin: 5px 5px 5px 0px;
    white-space: inherit;
}
</style>
