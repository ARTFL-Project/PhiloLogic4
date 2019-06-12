<template>
    <div id="landing-page-container" class="mt-5">
        <b-container fluid v-if="authorized">
            <div
                class="landing-page-logo"
                :class="{'dictionary': philoConfig.dictionary}"
                v-if="philoConfig.logo"
            >
                <img style="max-height: 300px; width: auto;" :src="philoConfig.logo">
            </div>
            <div id="default-landing-page" v-if="landingPageBrowsing === 'default'">
                <b-row id="landingGroup">
                    <b-col
                        cols="12"
                        sm="6"
                        :class="{'col-sm-offset-3': defaultLandingPageBrowsing.length == 1}"
                        v-for="browseType in defaultLandingPageBrowsing"
                        :key="browseType.label"
                    >
                        <b-card no-body :header="browseType.label" class="shadow-sm">
                            <b-row no-gutters>
                                <b-col
                                    v-for="(range, rangeIndex) in browseType.queries"
                                    :key="rangeIndex"
                                    @click="getContent(browseType, range)"
                                >
                                    <b-button
                                        variant="light"
                                        :class="{'first': rangeIndex === 0, 'last': rangeIndex === browseType.queries.length-1}"
                                        style="border-radius: 0; width: 100%"
                                    >{{range}}</b-button>
                                </b-col>
                            </b-row>
                        </b-card>
                    </b-col>
                </b-row>
            </div>
            <div id="simple-landing-page" v-if="landingPageBrowsing === 'simple'">
                <b-row id="landingGroup">
                    <b-col cols="12" sm-offset="2" sm="8">
                        <b-card no-body>
                            <b-list-group>
                                <b-list-group-item
                                    v-for="(biblioObj, bibIndex) in bibliography.results"
                                    :key="bibIndex"
                                >
                                    <span
                                        class="citation"
                                        v-for="(citation, citeIndex) in biblioObj.citation"
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
                                                v-if="citeIndex != biblioObj.citation.length - 1"
                                            >&#9679;</span>
                                        </span>
                                        <span v-if="!citation.href">
                                            <span v-html="citation.prefix"></span>
                                            <span :style="citation.style">{{ citation.label }}</span>
                                            <span v-html="citation.suffix"></span>
                                            <span
                                                class="separator"
                                                v-if="citeIndex != biblioObj.citation.length - 1"
                                            >&#9679;</span>
                                        </span>
                                    </span>
                                </b-list-group-item>
                            </b-list-group>
                        </b-card>
                    </b-col>
                </b-row>
            </div>
            <div
                id="custom-landing-page"
                v-if="landingPageBrowsing != 'default' && landingPage != 'dictionary' && landingPageBrowsing != 'simple'"
                v-html="philoConfig.landing_page_browsing"
            ></div>
            <!-- <dictionary-landing-page ng-if="lp.landingPageBrowsing === 'dictionary'"></dictionary-landing-page> -->
            <div
                id="landing-page-content"
                infinite-scroll="displayMoreItems()"
                infinite-scroll-distance="2"
                class="mt-4"
            >
                <b-row>
                    <b-col
                        cols="12"
                        offset-sm="1"
                        sm="9"
                        offset-md="2"
                        md="8"
                        class="text-content-area"
                    >
                        <b-card
                            :header="group.prefix"
                            v-for="group in resultGroups"
                            :key="group.prefix"
                            class="mb-4 shadow-sm"
                        >
                            <li
                                class="contentClass"
                                v-for="(result, resultIndex) in group.results"
                                :key="resultIndex"
                            >
                                <span
                                    class="citation"
                                    v-for="(citation, citeIndex) in result.citation"
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
                                            v-if="citeIndex != result.citation.length - 1"
                                        >&#9679;</span>
                                    </span>
                                    <span v-if="!citation.href">
                                        <span v-html="citation.prefix"></span>
                                        <span :style="citation.style">{{ citation.label }}</span>
                                        <span v-html="citation.suffix"></span>
                                        <span
                                            class="separator"
                                            v-if="citeIndex != result.citation.length - 1"
                                        >&#9679;</span>
                                    </span>
                                </span>
                                <span v-if="displayCount == 'true'">&nbsp;({{ result.count }})</span>
                            </li>
                        </b-card>
                    </b-col>
                </b-row>
            </div>
        </b-container>
        <!-- <access-control ng-if="!lp.authorized"></access-control> -->
    </div>
</template>
<script>
export default {
    name: "landingPage",
    computed: {},
    data() {
        return {
            philoConfig: this.$philoConfig,
            authorized: true,
            landingPageBrowsing: this.$philoConfig.landing_page_browsing,
            defaultLandingPageBrowsing: this.$philoConfig
                .default_landing_page_browsing,
            displayCount: true,
            resultGroups: [],
            contentType: "",
            loadingContent: false
        };
    },
    methods: {
        getContent(browseType, range) {
            let query = {
                browseType: browseType,
                query: range
            };
            this.$http
                .get(
                    "http://anomander.uchicago.edu/philologic/frantext0917/scripts/get_landing_page_content.py",
                    {
                        params: {
                            group_by_field: browseType.group_by_field,
                            display_count: browseType.display_count,
                            is_range: browseType.is_range,
                            query: range,
                            citation: JSON.stringify(browseType.citation)
                        }
                    }
                )
                .then(response => {
                    this.resultGroups = response.data.content;
                    this.displayCount = response.data.display_count;
                    this.contentType = response.data.content_type;
                    this.loadingContent = false;
                })
                .catch(response => {
                    this.loadingContent = false;
                });
        }
    }
};
</script>
<style thisd>
.btn-light {
    background-color: #fff;
    border-width: 0px 1px 0px 0px;
    border-color: rgba(0, 0, 0, 0.125);
}
.first {
    border-bottom-left-radius: 0.25rem !important;
}
.last {
    border-bottom-right-radius: 0.25rem !important;
    border-right-width: 0px;
}
.btn-light:hover {
    background-color: #f8f8f8;
}
.card-header {
    text-align: center;
    font-variant: small-caps;
}
</style>


