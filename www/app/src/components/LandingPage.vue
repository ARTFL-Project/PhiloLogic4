<template>
    <div id="landing-page-container" class="mt-5">
        <div class="container-fluid">
            <div class="landing-page-logo" :class="{ dictionary: dictionary }" v-if="logo">
                <img style="max-height: 300px; width: auto" :src="logo" alt="logo" />
            </div>
            <div class="d-flex justify-content-center position-relative">
                <div
                    class="spinner-border text-secondary"
                    role="status"
                    v-if="loading"
                    style="width: 4rem; height: 4rem; position: absolute; z-index: 50; top: 10px"
                ></div>
            </div>
            <div id="default-landing-page" class="row justify-content-center" v-if="landingPageBrowsing === 'default'">
                <div
                    class="col-12 col-sm-6 col-md-8 mb-4"
                    v-for="browseType in defaultLandingPageBrowsing"
                    :key="browseType.label"
                >
                    <div class="card shadow-sm">
                        <div class="card-header">{{ browseType.label }}</div>
                        <div class="row g-0">
                            <div
                                class="col"
                                :class="{ 'col-2': browseType.queries.length > 6 }"
                                v-for="(range, rangeIndex) in browseType.queries"
                                :key="rangeIndex"
                                @click="getContent(browseType, range)"
                            >
                                <button
                                    class="btn btn-light landing-page-btn"
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
            <div id="simple-landing-page" v-if="landingPageBrowsing === 'simple'">
                <div class="row" id="landingGroup">
                    <div class="cols-12 col-sm-8 offset-sm-2">
                        <div class="card" style="width: fit-content">
                            <ul class="list-group">
                                <li
                                    class="list-group-item"
                                    v-for="(biblioObj, bibIndex) in bibliography.results"
                                    :key="bibIndex"
                                >
                                    <citations :citation="biblioObj.citation"></citations>
                                </li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
            <div id="custom-landing-page" v-if="customLandingPage.length > 0" v-html="customLandingPage"></div>
            <div id="dictionary-landing-page" v-if="landingPageBrowsing === 'dictionary'">
                <div class="row">
                    <div class="col-6" :class="{ 'offset-3': !showDicoLetterRows }" id="dico-landing-volume">
                        <div class="card shadow-sm">
                            <div class="card-header">{{ $t("landingPage.browseByVolume") }}</div>
                            <div class="list-group" flush v-if="volumeData.length">
                                <div class="list-group-item" v-for="volume in volumeData" :key="volume.philo_id">
                                    <router-link :to="`/navigate/${volume.philo_id}/table-of-contents`">
                                        <i style="font-variant: small-caps">{{ volume.title }}</i>
                                        <span style="font-weight: 300; padding-left: 0.25rem" v-if="volume.start_head"
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
                            <div class="card-header">{{ $t("landingPage.browseByLetter") }}</div>
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
            <div id="landing-page-content" class="mt-4">
                <div class="row">
                    <div class="col-12 col-sm-9 offset-sm-1 col-md-8 offset-md-2 text-content-area">
                        <div
                            class="card mb-4 shadow-sm"
                            v-for="(group, groupIndex) in resultGroups"
                            :key="group.prefix"
                            :id="`landing-${group.prefix}`"
                        >
                            <div class="card-header">
                                {{ group.prefix.toString() }}
                            </div>
                            <ul class="list-group list-group-flush">
                                <li
                                    class="list-group-item contentClass p-2"
                                    v-for="(result, resultIndex) in group.results.slice(0, groupDisplay[groupIndex])"
                                    :key="resultIndex"
                                >
                                    <citations :citation="buildCitationObject(result.metadata, citations)"></citations>
                                    <span v-if="displayCount == 'true'">&nbsp;({{ result.count }})</span>
                                </li>
                            </ul>
                            <p class="pt-2 ps-3" v-if="group.results.length > 100">
                                <button type="button" class="btn btn-outline-secondary" @click="seeAll(groupIndex)">
                                    {{ $t("landingPage.seeResults", { n: group.results.length }) }}
                                </button>
                            </p>
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
            customLandingPage: "",
            displayCount: true,
            resultGroups: [],
            contentType: "",
            selectedField: "",
            loading: false,
            showDicoLetterRows: true,
            volumeData: [],
            dicoLetterRows: [],
            citations: [],
            groupDisplay: {},
            bibliography: [],
        };
    },
    created() {
        if (!["simple", "default", "dictionary"].includes(this.landingPageBrowsing)) {
            this.setupCustomPage();
        } else if (this.dictionary) {
            this.setupDictView();
        } else if (this.landingPageBrowsing == "simple") {
            this.getSimpleLandingPageData();
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
        setupCustomPage() {
            this.$http
                .get(`${this.$dbUrl}/${this.landingPageBrowsing}`, {
                    withCredentials: false,
                    headers: { "Access-Control-Allow-Origin": "*", "Content-Type": "text/html" },
                })
                .then((response) => (this.customLandingPage = response.data));
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
                    },
                })
                .then((response) => {
                    for (let i in response.data.content) {
                        this.groupDisplay[i] = 100;
                    }
                    this.resultGroups = Object.freeze(response.data.content);
                    this.citations = response.data.citations;
                    this.displayCount = response.data.display_count;
                    this.contentType = response.data.content_type;
                    this.loading = false;
                })
                .catch((error) => {
                    this.debug(this, error);
                    this.loading = false;
                });
        },
        getSimpleLandingPageData() {
            this.$http
                .get(`${this.$dbUrl}/reports/bibliography.py`, { params: { simple_bibliography: "all" } })
                .then((response) => {
                    this.bibliography = response.data;
                })
                .catch((error) => {
                    this.debug(this, error);
                    this.loading = false;
                });
        },
        buildCitationObject(metadataFields, citations) {
            // Used because too many results are returned from server
            let citationObject = [];
            for (let citation of citations) {
                let label = metadataFields[citation.field] || "";
                if (citation.link) {
                    let link = "";
                    if (citation.field == "title") {
                        if (this.$philoConfig.skip_table_of_contents) {
                            link = `/navigate/${metadataFields.philo_id.split(" ")[0]}`;
                        } else {
                            link = `/navigate/${metadataFields.philo_id.split(" ")[0]}/table-of-contents`;
                        }
                        citationObject.push({ ...citation, href: link, label: metadataFields.title });
                    } else {
                        let queryParams = {
                            ...this.$store.state.formData,
                            start: "0",
                            end: "25",
                        };
                        if (label == "") {
                            queryParams[citation.field] = ""; // Should be NULL, but that's broken in the philo lib
                            label = this.$t("common.na");
                        } else {
                            queryParams[citation.field] = `"${label}"`;
                        }

                        // workaround for broken NULL searches
                        if (queryParams[citation.field].length) {
                            link = this.paramsToRoute({
                                ...queryParams,
                                report: "concordance",
                            });
                            citationObject.push({ ...citation, href: link, label: label });
                        } else {
                            citationObject.push({ ...citation, href: "", label: label });
                        }
                    }
                } else {
                    citationObject.push({ ...citation, href: "", label: label });
                }
            }
            return citationObject;
        },
        goToLetter(letter) {
            this.$router.push(`/bibliography?head=^${letter}.*`);
        },
        seeAll(groupIndex) {
            this.groupDisplay[groupIndex] = this.resultGroups[groupIndex].length;
        },
    },
};
</script>
<style scoped>
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
.landing-page-btn:focus {
    border-width: 3px;
}
#dico-landing-volume .list-group-item {
    padding: 0 1rem;
}
#dico-landing-volume a {
    display: inline-block;
    padding: 0.5rem 0;
}
.letter {
    text-align: center;
}
</style>
