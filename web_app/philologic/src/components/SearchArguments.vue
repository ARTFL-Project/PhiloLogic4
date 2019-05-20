<template>
    <div id="search_arguments">
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
            <div
                class="btn btn-default term-groups"
                v-for="(group, index) in termGroups"
                :key="index"
            >
                <a href @click="getQueryTerms(group, index)">{{ group }}</a>
                <span
                    class="glyphicon glyphicon-remove-circle"
                    style="position: absolute; right: 3px; top: 5px"
                    @click="removeTerm(index)"
                ></span>
            </div>
            {{ queryArgs.proximity }}
            <div
                id="query-terms"
                class="panel panel-default velocity-opposites-transition-fadeIn"
                style="display: none;"
                data-velocity-opts="{duration: 200}"
            >
                <button type="button" class="close" @click="closeTermsList()">
                    <span aria-hidden="true">&times;</span>
                    <span class="sr-only">Close</span>
                </button>
                <h4
                    class="panel-title"
                >The search terms query expanded to the following {{ words.length }} terms:</h4>
                <h6 v-if="words.length > 100">100 most frequent terms displayed</h6>
                <button
                    type="button"
                    class="btn btn-primary btn-sm velocity-transition-fadeIn"
                    style="margin:10px 0px"
                    v-if="wordListChanged"
                    @click="rerunQuery()"
                >Rerun query with the current modifications</button>
                <ol id="query-terms-list" class="row">
                    <li class="col-xs-6" v-for="word in words" :key="word">
                        <div class="panel panel-default">
                            {{ word }}
                            <button
                                type="button"
                                class="close"
                                style="margin-top: 4px"
                                @click="removeFromTermsList(word, groupIndexSelected)"
                            >
                                <span aria-hidden="true">&times;</span>
                                <span class="sr-only">Close</span>
                            </button>
                        </div>
                    </li>
                </ol>
            </div>
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
export default {
    name: "searchArguments",
    data() {
        return {
            philoConfig: this.$philoConfig,
            queryArgs: {}
        }
    },
    created() {
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
    },
    methods: {
        buildCriteria(queryParams) {
            let queryArgs = JSON.parse(JSON.stringify(queryParams));
            let biblio = []
            if (queryArgs.report === "time_series") {
                delete queryParams[philoConfig.time_series_year_field];
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
                    for (value of facets) {
                        if (facets.indexOf(value) < 0) {
                            facets.push(value);
                        }
                    };
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
            // let request = URL.report(queryParams);
            if (queryParams.report === "concordance" || queryParams.report === "kwic" || queryParams.report === "bibliography") {
                this.$router.push(`http://anomander.uchicago.edu/philologic/test/${this.paramsToUrl(queryParams)}`);
            } else if (queryParams.report === "collocation" || queryParams.report === "time_series") {
                this.$router.push(`http://anomander.uchicago.edu/philologic/test/${this.paramsToUrl(queryParams)}`);
                // $rootScope.formData = queryParams;
                // restart = true;
            }
        }
    }

}
</script>
<style scoped>
</style>
