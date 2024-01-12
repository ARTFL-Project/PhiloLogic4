<template>
    <div class="container-fluid mt-4">
        <results-summary :description="results.description" :running-total="runningTotal"
            :filter-list="filterList"></results-summary>
        <div class="row mt-4 pe-1" style="padding: 0 0.5rem" v-if="resultsLength">
            <div class="col-12 col-sm-4">
                <div class="card shadow-sm">
                    <table class="table table-hover table-striped table-light table-borderless caption-top">
                        <thead class="table-header">
                            <tr>
                                <th scope="col">{{ $t("collocation.collocate") }}</th>
                                <th scope="col">{{ $t("collocation.count") }}</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr style="line-height: 2rem" v-for="word in sortedList" :key="word.collocate"
                                @click="collocTableClick(word)">
                                <td class="text-view">{{ word.collocate }}</td>
                                <td>{{ word.count }}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
            <div class="col-12 col-sm-8">
                <div class="card p-3 shadow-sm">
                    <div class="card-text">
                        <span class="cloud-word text-view" v-for="word in collocCloudWords" :key="word.word"
                            :style="getWordCloudStyle(word)" @click="collocTableClick(word)">{{ word.collocate }}</span>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
<script>
import { mapFields } from "vuex-map-fields";
import ResultsSummary from "./ResultsSummary";
import variables from "../assets/styles/theme.module.scss";

export default {
    name: "collocation-report",
    components: {
        ResultsSummary,
    },
    computed: {
        ...mapFields([
            "formData.report",
            "formData.colloc_filter_choice",
            "formData.q",
            "formData.filter_frequency",
            "currentReport",
            "resultsLength",
            "searching",
            "urlUpdate",
            "accessAuthorized",
        ]),
        colorCodes: function () {
            let r = 0,
                g = 0,
                b = 0;
            // 3 digits
            if (this.cloudColor.length == 4) {
                r = "0x" + this.cloudColor[1] + this.cloudColor[1];
                g = "0x" + this.cloudColor[2] + this.cloudColor[2];
                b = "0x" + this.cloudColor[3] + this.cloudColor[3];

                // 6 digits
            } else if (this.cloudColor.length == 7) {
                r = "0x" + this.cloudColor[1] + this.cloudColor[2];
                g = "0x" + this.cloudColor[3] + this.cloudColor[4];
                b = "0x" + this.cloudColor[5] + this.cloudColor[6];
            }
            let colorCodes = {};
            var step = 0.03;
            for (let i = 0; i < 21; i += 1) {
                let rLocal = r - r * step * i;
                let gLocal = g - g * step * i;
                let bLocal = b - b * step * i;
                let opacityStep = i * 0.03;
                colorCodes[i] = `rgba(${rLocal}, ${gLocal}, ${bLocal}, ${0.4 + opacityStep})`;
            }
            return colorCodes;
        },
        splittedFilterList: function () {
            let arrayLength = this.filterList.length;
            let chunkSize = arrayLength / 5;
            let splittedList = [];
            for (let index = 0; index < arrayLength; index += chunkSize) {
                let myChunk = this.filterList.slice(index, index + chunkSize);
                splittedList.push(myChunk);
            }
            return splittedList;
        },
    },
    inject: ["$http"],
    provide() {
        return {
            results: this.results.results,
        };
    },
    data() {
        return {
            philoConfig: this.$philoConfig,
            results: {},
            filterList: [],
            searchParams: {},
            moreResults: false,
            sortedList: [],
            showFilteredWords: false,
            runningTotal: 0,
            collocCloudWords: [],
            unboundListener: null,
            cloudColor: variables.color,
        };
    },
    created() {
        this.report = "collocation";
        this.currentReport = "collocation";
        this.fetchResults();
    },
    watch: {
        urlUpdate() {
            if (this.$route.name == "collocation") {
                this.fetchResults();
            }
        },
    },
    methods: {
        fetchResults() {
            this.localFormData = this.copyObject(this.$store.state.formData);
            var collocObject = {};
            this.searching = true;
            this.updateCollocation(collocObject, 0);
            // } else {
            //     this.retrieveFromStorage();
            // }
        },
        updateCollocation(fullResults, start) {
            let params = {
                ...this.$store.state.formData,
                start: start.toString(),
            };
            this.$http
                .get(`${this.$dbUrl}/reports/collocation.py`, {
                    params: this.paramsFilter(params),
                })
                .then((response) => {
                    let data = response.data;
                    this.resultsLength = data.results_length;
                    this.moreResults = data.more_results;
                    this.runningTotal = data.hits_done;
                    start = data.hits_done;
                    this.searching = false;
                    if (this.resultsLength) {
                        this.sortAndRenderCollocation(fullResults, data, start);
                    }
                })
                .catch((error) => {
                    this.searching = false;
                    this.debug(this, error);
                });
        },
        sortAndRenderCollocation(fullResults, data, start) {
            if (typeof fullResults === "undefined" || Object.keys(fullResults).length === 0) {
                fullResults = {};
                this.filterList = data.filter_list;
            }
            var collocates = this.mergeResults(fullResults, data.collocates);
            let sortedList = [];
            for (let word of collocates.sorted.slice(0, 100)) {
                let collocate = `${word.label}`.replace(/lemma:/, "");
                let surfaceForm = word.label;
                sortedList.push({ collocate: collocate, surfaceForm: surfaceForm, count: word.count });
            }
            this.sortedList = sortedList;
            this.buildWordCloud();
            if (this.moreResults) {
                var tempFullResults = collocates.unsorted;
                var runningQuery = this.$store.state.formData;
                if (this.report === "collocation" && this.deepEqual(runningQuery, this.localFormData)) {
                    // make sure we're still running the same query
                    this.updateCollocation(tempFullResults, start);
                }
            } else {
                this.done = true;
                // Collocation cloud not showing when loading cached searches one after the other
                //saveToLocalStorage({results: this.sortedList, resultsLength: this.resultsLength, filterList: this.filterList});
            }
        },
        retrieveFromStorage() {
            let urlString = this.paramsToUrlString(this.$store.state.formData);
            var savedObject = JSON.parse(sessionStorage[urlString]);
            this.sortedList = savedObject.results;
            this.resultsLength = savedObject.resultsLength;
            this.filterList = savedObject.filterList;
            this.done = true;
            this.searching = false;
        },
        collocTableClick(item) {
            let q
            console.log(item)
            if (item.surfaceForm.startsWith("lemma:")) {
                q = `${this.q} ${item.surfaceForm}`;
            } else {
                q = `${this.q} "${item.surfaceForm}"`;
            }
            this.$router.push(
                this.paramsToRoute({
                    ...this.$store.state.formData,
                    report: "concordance",
                    q: q,
                    method: "cooc",
                })
            );
        },
        buildWordCloud() {
            let lowestValue = this.sortedList[this.sortedList.length - 1].count;
            let higestValue = this.sortedList[0].count;
            let diff = higestValue - lowestValue;
            let coeff = diff / 20;

            var adjustWeight = function (count) {
                let adjustedCount = count - lowestValue;
                let adjustedWeight = Math.round(adjustedCount / coeff);
                adjustedWeight = parseInt(adjustedWeight);
                return adjustedWeight;
            };

            let weightedWordList = [];
            for (let wordObject of this.sortedList) {
                let adjustedWeight = adjustWeight(wordObject.count);
                weightedWordList.push({
                    collocate: wordObject.collocate,
                    surfaceForm: wordObject.surfaceForm,
                    weight: 1 + adjustedWeight / 10,
                    color: this.colorCodes[adjustedWeight],
                });
            }
            weightedWordList.sort(function (a, b) {
                return a.collocate.localeCompare(b.collocate);
            });
            this.collocCloudWords = weightedWordList;
        },
        getWordCloudStyle(word) {
            return `font-size: ${word.weight}rem; color: ${word.color}`;
        },
    },
};
</script>
<style lang="scss" scoped>
@import "../assets/styles/theme.module.scss";

th {
    background-color: $link-color;
    color: #fff;
    font-weight: 400;
    font-variant: small-caps;
}

tbody tr {
    cursor: pointer;
}

#description {
    position: relative;
}

#export-results {
    position: absolute;
    right: 0;
    padding: 0.125rem 0.25rem;
    font-size: 0.8rem !important;
}

.cloud-word {
    display: inline-block;
    padding: 5px;
    cursor: pointer;
    line-height: initial;
}

.table th,
.table td {
    padding: 0.45rem 0.75rem;
}

#filter-list {
    position: absolute;
    z-index: 100;
}

#filter-list .list-group-item {
    border-width: 0px;
    padding: 0.1rem;
}

#close-filter-list {
    width: fit-content;
    float: right;
    padding: 0 0.2rem;
    position: absolute;
    right: 0;
}
</style>

