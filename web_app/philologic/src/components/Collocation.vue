<template>
    <div id="collocation-container" class="mt-4" v-if="authorized">
        <b-card no-body class="shadow-sm m-4 pb-3">
            <div id="description">
                <b-button
                    variant="outline-primary"
                    size="sm"
                    id="export-results"
                    data-target="#export-dialog"
                >Export results</b-button>
                <search-arguments :results-length="resultsLength"></search-arguments>
            </div>
            <!-- <progress-bar
                    progress="{{ collocation.percent }}"
                    class="velocity-opposites-transition-slideDownIn"
                    data-velocity-opts="{ duration: 400 }"
                    v-if="collocation.done === false"
            ></progress-bar>-->
            <div class="pl-3">
                <span>
                    <span tooltip tooltip-title="Click to display filtered words">
                        The
                        <a
                            href
                            @click="toggleFilterList()"
                            v-if="colloc_filter_choice === 'frequency'"
                        >{{ filter_frequency }} most common words</a>
                        <a
                            href
                            @click="toggleFilterList()"
                            v-if="colloc_filter_choice === 'stopwords'"
                        >{{ filter_frequency }} most common words</a>
                        are being filtered from this report.
                    </span>
                </span>
                <b-card
                    no-body
                    id="filter-list"
                    class="pl-3 pr-3 pb-3 shadow-lg"
                    data-velocity-opts="{duration: 200}"
                    v-if="showFilteredWords"
                >
                    <b-button class="close" @click="toggleFilterList()">
                        <span aria-hidden="true">&times;</span>
                    </b-button>
                    <b-row class="mt-4">
                        <b-col v-for="wordGroup in splittedFilterList" :key="wordGroup[0]">
                            <b-list-group flush>
                                <b-list-group-item v-for="word in wordGroup" :key="word">{{ word }}</b-list-group-item>
                            </b-list-group>
                        </b-col>
                    </b-row>
                </b-card>
            </div>
        </b-card>
        <b-row class="m-2">
            <b-col cols="12" sm="4">
                <b-card no-body class="shadow-sm">
                    <b-table
                        hover
                        striped
                        borderless
                        caption-top
                        :items="sortedList"
                        @row-clicked="collocTableClick"
                    ></b-table>
                </b-card>
            </b-col>
            <b-col cols="12" sm="8">
                <b-card no-body class="p-3 shadow-sm">
                    <div class="card-text">
                        <span
                            class="cloud-word"
                            v-for="word in collocCloudWords"
                            :key="word.word"
                            :style="getWordCloudStyle(word)"
                            @click="collocTableClick(word)"
                        >{{ word.collocate}}</span>
                    </div>
                </b-card>
            </b-col>
        </b-row>
        <!-- <access-control v-if="!authorized"></access-control> -->
    </div>
</template>
<script>
import { mapFields } from "vuex-map-fields";
import searchArguments from "./SearchArguments";
import { EventBus } from "../main.js";

export default {
    name: "collocation",
    components: {
        searchArguments
    },
    computed: {
        ...mapFields([
            "formData.report",
            "formData.colloc_filter_choice",
            "formData.q",
            "formData.filter_frequency"
        ]),
        colorCodes: function() {
            let colorCodes = {};
            let r = 45;
            let g = 184;
            let b = 255;
            var step = 0.03;
            for (let i = 0; i < 21; i += 1) {
                let rLocal = r - r * step * i;
                let gLocal = g - g * step * i;
                let bLocal = b - b * step * i;
                let opacityStep = i * 0.03;
                colorCodes[i] = `rgba(${rLocal}, ${gLocal}, ${bLocal}, ${0.4 +
                    opacityStep})`;
            }
            return colorCodes;
        },
        splittedFilterList: function() {
            let arrayLength = this.filterList.length;
            let chunkSize = arrayLength / 5;
            let splittedList = [];
            for (let index = 0; index < arrayLength; index += chunkSize) {
                let myChunk = this.filterList.slice(index, index + chunkSize);
                splittedList.push(myChunk);
            }
            return splittedList;
        }
    },
    data() {
        return {
            philoConfig: this.$philoConfig,
            results: {},
            filterList: [],
            searchParams: {},
            authorized: true,
            resultsLength: 0,
            moreResults: false,
            loading: false,
            sortedList: [],
            showFilteredWords: false,
            percent: 0,
            loading: false,
            collocCloudWords: []
        };
    },
    created() {
        this.report = "collocation";
        this.filter_frequency = 100;
        this.fetchResults();
        EventBus.$on("urlUpdate", () => {
            if (this.report == "collocation") {
                this.fetchResults();
            }
        });
    },
    methods: {
        fetchResults() {
            let urlString = this.paramsToUrlString(this.$store.state.formData);
            // angular.element("#philologic_collocation").velocity("fadeIn", {
            //     duration: 200
            // });
            // angular.element(".progress").show();
            this.localFormData = this.copyObject(this.$store.state.formData);
            this.loading = false;
            var collocObject = {};
            this.updateCollocation(collocObject, 0);
            // } else {
            //     this.retrieveFromStorage();
            // }
        },
        updateCollocation(fullResults, start) {
            let params = {
                ...this.$store.state.formData,
                start: start.toString()
            };
            this.$http
                .get(
                    "http://anomander.uchicago.edu/philologic/test/reports/collocation.py",
                    { params: this.paramsFilter(params) }
                )
                .then(response => {
                    var data = response.data;
                    this.resultsLength = data.results_length;
                    this.moreResults = data.more_results;
                    start = data.hits_done;
                    this.sortAndRenderCollocation(fullResults, data, start);
                })
                .catch(response => {
                    this.loading = false;
                    console.log(response);
                });
        },
        sortAndRenderCollocation(fullResults, data, start) {
            if (start <= this.resultsLength) {
                this.percent = Math.floor((start / this.resultsLength) * 100);
            }
            if (
                typeof fullResults === "undefined" ||
                Object.keys(fullResults).length === 0
            ) {
                fullResults = {};
                this.filterList = data.filter_list;
            }
            var collocates = this.mergeResults(fullResults, data["collocates"]);
            let sortedList = [];
            for (let word of collocates.sorted.slice(0, 100)) {
                sortedList.push({ collocate: word.label, count: word.count });
            }
            this.sortedList = sortedList;
            this.buildWordCloud();
            this.loading = false;
            if (this.moreResults) {
                var tempFullResults = collocates.unsorted;
                var runningQuery = this.$store.state.formData;
                if (
                    this.report === "collocation" &&
                    this.deepEqual(runningQuery, this.localFormData)
                ) {
                    // make sure we're still running the same query
                    this.updateCollocation(tempFullResults, start);
                }
            } else {
                this.percent = 100;
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
            this.percent = 100;
            this.done = true;
            this.loading = false;
            angular.element("#philologic_collocation").velocity("fadeIn", {
                duration: 200
            });
        },
        collocTableClick(item) {
            this.$router.push(
                this.paramsToRoute({
                    ...this.$store.state.formData,
                    report: "concordance",
                    q: `${this.q} ${item.collocate}`,
                    method: "cooc"
                })
            );
        },
        buildWordCloud() {
            let lowestValue = this.sortedList[this.sortedList.length - 1].count;
            let higestValue = this.sortedList[0].count;
            let diff = higestValue - lowestValue;
            let coeff = diff / 20;

            var adjustWeight = function(count) {
                let adjustedCount = count - lowestValue;
                let adjustedWeight = Math.round(adjustedCount / coeff);
                adjustedWeight = parseInt(adjustedWeight);
                return adjustedWeight;
            };

            let weightedWordList = [];
            for (let wordObject of this.sortedList) {
                let adjustedWeight = adjustWeight(wordObject.count);
                // console.log(adjustedWeight);
                weightedWordList.push({
                    collocate: wordObject.collocate,
                    weight: 1 + adjustedWeight / 10,
                    color: this.colorCodes[adjustedWeight]
                });
            }
            weightedWordList.sort(function(a, b) {
                return a.collocate.localeCompare(b.collocate);
            });
            this.collocCloudWords = weightedWordList;
        },
        getWordCloudStyle(word) {
            // console.log(word.color, word.word);
            return `font-size: ${word.weight}rem; color: ${word.color}`;
        },
        toggleFilterList() {
            event.preventDefault();
            if (this.showFilteredWords == true) {
                this.showFilteredWords = false;
            } else {
                this.showFilteredWords = true;
            }
        }
    }
};
</script>
<style scoped>
#description {
    position: relative;
}
#export-results {
    position: absolute;
    right: 0;
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
</style>

