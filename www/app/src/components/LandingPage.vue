<template>
    <div id="landing-page-container" class="mt-5">
        <div class="container-fluid" v-if="accessAuthorized">
            <div class="landing-page-logo" :class="{ dictionary: dictionary }" v-if="logo">
                <img style="max-height: 300px; width: auto" :src="logo" />
            </div>
            <div class="d-flex justify-content-center position-relative">
                <div
                    class="spinner-border text-secondary"
                    role="status"
                    v-if="loading"
                    style="width: 4rem; height: 4rem; position: absolute; z-index: 50; top: 10px"
                ></div>
            </div>
            <div id="default-landing-page" v-if="landingPageBrowsing === 'default'">
                <div class="row" id="landingGroup">
                    <div
                        class="col-12 col-sm-6 mb-4"
                        :class="{ 'offset-sm-3': defaultLandingPageBrowsing.length == 1 }"
                        v-for="browseType in defaultLandingPageBrowsing"
                        :key="browseType.label"
                    >
                        <div class="card shadow-sm">
                            <div class="card-header">{{ browseType.label }}</div>
                            <div class="row g-0">
                                <div
                                    class="col"
                                    v-for="(range, rangeIndex) in browseType.queries"
                                    :key="rangeIndex"
                                    @click="getContent(browseType, range)"
                                >
                                    <button
                                        class="btn btn-light"
                                        :class="{
                                            first: rangeIndex === 0,
                                            last: rangeIndex === browseType.queries.length - 1,
                                        }"
                                        style="border-radius: 0; width: 100%"
                                    >
                                        {{ range }}
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div id="simple-landing-page" v-if="landingPageBrowsing === 'simple'">
                <div class="row" id="landingGroup">
                    <div class="cols-12 col-sm-8 offset-sm-2">
                        <div class="card">
                            <ul class="list-group">
                                <li class="list-group-item">
                                    v-for="(biblioObj, bibIndex) in bibliography.results" :key="bibIndex" >
                                    <citations :citation="biblioObj.citation"></citations>
                                </li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
            <div
                id="custom-landing-page"
                v-if="
                    landingPageBrowsing != 'default' &&
                    landingPageBrowsing != 'dictionary' &&
                    landingPageBrowsing != 'simple'
                "
                v-html="landingPageBrowsing"
            ></div>
            <div id="dictionary-landing-page" v-if="landingPageBrowsing === 'dictionary'">
                <div class="row">
                    <div class="col-6" :class="{ 'offset-3': !showDicoLetterRows }" id="dico-landing-volume">
                        <div class="card shadow-sm">
                            <div class="card-header">Browse by volume</div>
                            <div class="list-group" flush v-if="volumeData.length">
                                <div class="list-group-item" v-for="volume in volumeData" :key="volume.philo_id">
                                    <router-link :to="`/navigate/${volume.philo_id}/table-of-contents`">
                                        <i style="font-variant: small-caps">{{ volume.title }}</i>
                                        <span style="font-weight: 300" v-if="volume.start_head"
                                            >({{ volume.start_head }} - {{ volume.end_head }})</span
                                        >
                                    </router-link>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div
                        class="col"
                        id="dico-landing-alpha"
                        cols="6"
                        style="border-width: 0px; box-shadow: 0 0 0"
                        v-if="showDicoLetterRows"
                    >
                        <div class="card">
                            <div class="card-header">Browse by letter</div>
                            <table class="table table-borderless" style="margin-bottom: 0">
                                <tr v-for="(row, rowIndex) in dicoLetterRows" :key="rowIndex">
                                    <td
                                        class="letter"
                                        v-for="letter in row"
                                        :key="letter.letter"
                                        @click="goToLetter(letter.letter)"
                                    >
                                        {{ letter.letter }}
                                    </td>
                                </tr>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
            <div
                id="landing-page-content"
                infinite-scroll="displayMoreItems()"
                infinite-scroll-distance="2"
                class="mt-4"
            >
                <div class="row">
                    <div class="col-12 col-sm-9 offset-sm-1 col-md-8 offset-md-2 text-content-area">
                        <div class="card mb-4 shadow-sm" v-for="group in resultGroups" :key="group.prefix">
                            <div class="card-header">
                                {{ group.prefix.toString() }}
                            </div>
                            <li
                                class="contentClass p-2"
                                v-for="(result, resultIndex) in group.results"
                                :key="resultIndex"
                            >
                                <citations :citation="result.citation"></citations>
                                <span v-if="displayCount == 'true'">&nbsp;({{ result.count }})</span>
                            </li>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
<script>
import citations from "./Citations";
import { mapFields } from "vuex-map-fields";

export default {
    name: "landingPage",
    components: {
        citations,
    },
    computed: { ...mapFields(["accessAuthorized"]) },
    inject: ["$http"],
    data() {
        return {
            dictionary: this.$philoConfig.dictionary,
            logo: this.$philoConfig.logo,
            landingPageBrowsing: this.$philoConfig.landing_page_browsing,
            defaultLandingPageBrowsing: this.$philoConfig.default_landing_page_browsing,
            displayCount: true,
            resultGroups: [],
            contentType: "",
            selectedField: "",
            loading: false,
            showDicoLetterRows: true,
            volumeData: [],
            dicoLetterRows: [],
        };
    },
    created() {
        if (this.dictionary) {
            this.setupDictView();
        }
    },
    methods: {
        setupDictView() {
            this.$http.get(`${this.$dbUrl}/scripts/get_bibliography.py?object_level=doc`).then((response) => {
                for (let i = 0; i < response.data.length; i++) {
                    this.volumeData.push(response.data[i]);
                }
            });

            let dicoLetterRange = this.$philoConfig.dico_letter_range;
            let row = [];
            let position = 0;
            for (var i = 0; i < dicoLetterRange.length; i++) {
                position++;
                row.push({
                    letter: dicoLetterRange[i],
                    url: "bibliography&head=^" + dicoLetterRange[i] + ".*",
                });
                if (position === 4) {
                    this.dicoLetterRows.push(row);
                    row = [];
                    position = 0;
                }
            }
            if (row.length) {
                this.dicoLetterRows.push(row);
            }
            if (this.dicoLetterRows.length == 0) {
                this.showDicoLetterRows = false;
            }
        },
        getContent(browseType, range) {
            this.selectedField = browseType.group_by_field;
            this.loading = true;
            this.$http
                .get(`${this.$dbUrl}/scripts/get_landing_page_content.py`, {
                    params: {
                        group_by_field: browseType.group_by_field,
                        display_count: browseType.display_count,
                        is_range: browseType.is_range,
                        query: range,
                        citation: JSON.stringify(browseType.citation),
                    },
                })
                .then((response) => {
                    if (browseType.group_by_field == "author") {
                        this.resultGroups = this.groupByAuthor(response.data.content);
                    } else {
                        this.resultGroups = response.data.content;
                    }
                    this.displayCount = response.data.display_count;
                    this.contentType = response.data.content_type;
                    this.loading = false;
                })
                .catch((error) => {
                    this.debug(this, error);
                    this.loading = false;
                });
        },
        groupByAuthor(letterGroups) {
            var groupedResults = [];
            for (let group of letterGroups) {
                var localGroup = [];
                for (let i = 0; i < group.results.length; i += 1) {
                    const innerGroup = group.results[i];
                    const citations = innerGroup.citation;
                    let authorName = innerGroup.metadata.author;
                    let savedCitation = "";
                    for (let c = 0; c < citations.length; c += 1) {
                        let citation = citations[c];
                        if (citation.label == authorName) {
                            savedCitation = citation;
                            break;
                        }
                    }
                    localGroup.push({
                        metadata: innerGroup.metadata,
                        citation: [savedCitation],
                        count: innerGroup.count,
                        normalized: innerGroup.normalized,
                    });
                }
                groupedResults.push({
                    prefix: group.prefix,
                    results: localGroup,
                });
            }
            return groupedResults;
        },
        goToLetter(letter) {
            this.$router.push(`/bibliography?head=^${letter}.*`);
        },
    },
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
.letter {
    text-align: center;
    cursor: pointer;
    color: #007bff;
}
.letter:hover {
    background-color: #e8e8e8;
}
tr:nth-child(odd) {
    background-color: #f8f8f8;
}
tr:nth-child(odd) td.letter:nth-child(2n + 1) {
    background-color: #fff;
}
tr:nth-child(even) {
    background-color: #fff;
}
tr:nth-child(even) td.letter:nth-child(2n + 1) {
    background-color: #f8f8f8;
}
</style>
