<template>
    <div>
        <conckwic></conckwic>
        <b-row class="ml-2 mr-2 mb-2">
            <b-col cols="12" md="7" xl="8">
                <b-card no-body class="p-2 shadow-sm">
                    <div class="p-2 mb-1">
                        Resort results by
                        <div
                            class="btn-group"
                            style="margin-left: 3px;"
                            v-for="(fields, index) in sortingFields"
                            :key="index"
                        >
                            <b-dropdown size="sm">
                                <template slot="button-content">{{ sortingSelection[index] }}</template>
                                <b-dropdown-item
                                    v-for="(selection, fieldIndex) in fields"
                                    :key="fieldIndex"
                                    @click="updateSortingSelection(index, selection)"
                                >{{ selection.label }}</b-dropdown-item>
                            </b-dropdown>
                        </div>
                        <b-button
                            variant="primary"
                            type="button"
                            class="ml-1"
                            size="sm"
                            @click="sortResults()"
                        >Sort</b-button>
                    </div>
                    <div id="kwic-concordance" v-if="Object.keys(results).length">
                        <div
                            class="kwic_line"
                            v-for="(result, kwicIndex) in filteredKwic(results.results)"
                            :key="kwicIndex"
                        >
                            <span v-html="initializePos(kwicIndex)"></span>
                            <router-link
                                :to="'/' + result.citation_links.div1"
                                class="kwic_biblio"
                                @mouseover="showFullBiblio()"
                                @mouseleave="hideFullBiblio()"
                            >
                                <span
                                    class="full_biblio"
                                    style="display:none;"
                                >{{ result.fullBiblio }}</span>
                                <span class="short_biblio" v-html="result.shortBiblio"></span>
                            </router-link>
                            <span v-html="result.context"></span>
                        </div>
                    </div>
                </b-card>
            </b-col>
            <b-col md="5" xl="4">
                <facets></facets>
            </b-col>
        </b-row>
        <pages></pages>
    </div>
</template>

<script>
import { mapFields } from "vuex-map-fields";
import conckwic from "./ConcordanceKwic";
import facets from "./Facets";
import pages from "./Pages";
import { EventBus } from "../main.js";

export default {
    name: "kwic",
    components: {
        conckwic,
        facets,
        pages
    },
    computed: {
        // When using nested data structures, the string
        // after the last dot (e.g. `firstName`) is used
        // for defining the name of the computed property.
        ...mapFields([
            "formData.report",
            "formData.q",
            "formData.start",
            "formData.end",
            "formData.results_per_page",
            "formData.first_kwic_sorting_option",
            "formData.second_kwic_sorting_option",
            "formData.third_kwic_sorting_option",
            "resultsLength",
            "searching",
            "currentReport",
            "description"
        ]),
        sortingSelection() {
            let sortingSelection = [];
            if (this.first_kwic_sorting_option !== "") {
                sortingSelection.push(
                    this.sortKeys[this.first_kwic_sorting_option]
                );
            }
            if (this.second_kwic_sorting_option !== "") {
                sortingSelection.push(
                    this.sortKeys[this.second_kwic_sorting_option]
                );
            }
            if (this.third_kwic_sorting_option !== "") {
                sortingSelection.push(
                    this.sortKeys[this.third_kwic_sorting_option]
                );
            }
            if (sortingSelection.length === 0) {
                sortingSelection = ["None", "None", "None"];
            } else if (sortingSelection.length === 1) {
                sortingSelection.push("None");
                sortingSelection.push("None");
            } else if (sortingSelection.length === 2) {
                sortingSelection.push("None");
            }
            return sortingSelection;
        }
    },
    data() {
        return {
            philoConfig: this.$philoConfig,
            results: {},
            searchParams: {},
            sortingFields: [],
            sortKeys: {
                q: "searched term(s)",
                left: "words to the left",
                right: "words to the right"
            },
            sortedResults: [],
            loading: false
        };
    },
    created() {
        this.report = "kwic";
        this.currentReport = "kwic";
        this.initializeKwic();
        this.fetchResults();
        EventBus.$on("urlUpdate", () => {
            console.log("update KWIC");
            if (this.report == "kwic") {
                this.fetchResults();
                console.log("updated");
            }
        });
    },
    beforeDestroy() {
        EventBus.$off("urlUpdate");
    },
    methods: {
        initializeKwic() {
            // Sorting fields
            let sortingFields = [
                {
                    label: "None",
                    field: ""
                },
                {
                    label: "searched term(s)",
                    field: "q"
                },
                {
                    label: "words to the left",
                    field: "left"
                },
                {
                    label: "words to the right",
                    field: "right"
                }
            ];
            for (let field of this.philoConfig.kwic_metadata_sorting_fields) {
                if (field in this.philoConfig.metadata_aliases) {
                    let label = this.philoConfig.metadata_aliases[field];
                    sortingFields.push({
                        label: label,
                        field: field
                    });
                    this.sortKeys[field] = label;
                } else {
                    sortingFields.push({
                        label: field[0].toUpperCase() + field.slice(1),
                        field: field
                    });
                    this.sortKeys[field] =
                        field[0].toUpperCase() + field.slice(1);
                }
            }
            this.sortingFields = [sortingFields, sortingFields, sortingFields];
        },
        buildFullCitation(metadataField) {
            let citationList = [];
            let biblioFields = this.philoConfig.kwic_bibliography_fields;
            if (
                typeof biblioFields === "undefined" ||
                biblioFields.length === 0
            ) {
                biblioFields = this.philoConfig.metadata.slice(0, 2);
                biblioFields.push("head");
            }
            for (var i = 0; i < biblioFields.length; i++) {
                if (biblioFields[i] in metadataField) {
                    var biblioField = metadataField[biblioFields[i]] || "";
                    if (biblioField.length > 0) {
                        citationList.push(biblioField);
                    }
                }
            }
            if (citationList.length > 0) {
                return citationList.join(", ");
            } else {
                return "NA";
            }
        },
        filteredKwic(results) {
            let filteredResults = [];
            for (let resultObject of results) {
                resultObject.fullBiblio = this.buildFullCitation(
                    resultObject.metadata_fields
                );
                resultObject.shortBiblio = resultObject.fullBiblio.slice(0, 30);
                filteredResults.push(resultObject);
            }
            return filteredResults;
        },
        showFullBiblio() {
            let target = event.srcElement.parentNode.querySelector(
                ".full_biblio"
            );
            target.classList.add("show");
        },
        hideFullBiblio() {
            let target = event.srcElement.parentNode.querySelector(
                ".full_biblio"
            );
            target.classList.remove("show");
        },
        updateSortingSelection(index, selection) {
            if (index === 0) {
                if (selection.label == "None") {
                    this.first_kwic_sorting_option = "";
                } else {
                    this.first_kwic_sorting_option = selection.field;
                }
            } else if (index == 1) {
                if (selection.label == "None") {
                    this.second_kwic_sorting_option = "";
                } else {
                    this.second_kwic_sorting_option = selection.field;
                }
            } else {
                if (selection.label == "None") {
                    this.third_kwic_sorting_option = "";
                } else {
                    this.third_kwic_sorting_option = selection.field;
                }
            }
        },
        fetchResults() {
            this.results = {};
            this.searching = true;
            this.searchParams = { ...this.$store.state.formData };
            if (this.first_kwic_sorting_option === "") {
                console.log("fetching KWIC");
                this.$http
                    .get(
                        "http://anomander.uchicago.edu/philologic/frantext0917/reports/kwic.py",
                        { params: this.paramsFilter(this.searchParams) }
                    )
                    .then(response => {
                        this.results = response.data;
                        this.resultsLength = this.results.results_length;
                        this.$store.commit("updateDescription", {
                            ...this.description,
                            start: this.results.description.start,
                            end: this.results.description.end,
                            results_per_page: this.results.description
                                .results_per_page
                        });
                        this.searching = false;
                        console.log("emitting done");
                        EventBus.$emit("resultsDone");
                    })
                    .catch(error => {
                        this.searching = false;
                        this.error = error.toString();
                        console.log(error);
                    });
            } else {
                this.start = "0";
                this.end = "0";
                this.recursiveLookup(0);
            }
        },
        mergeLists(list1, list2) {
            for (var i = 0; i < list2.length; i += 1) {
                list1.push(list2[i]);
            }
            return list1;
        },
        recursiveLookup(hitsDone) {
            var vm = this;
            this.$http
                .get(
                    "http://anomander.uchicago.edu/philologic/frantext0917/scripts/get_neighboring_words.py",
                    {
                        params: {
                            ...this.paramsFilter(this.$store.state.formData),
                            hits_done: hitsDone,
                            max_time: 10
                        }
                    }
                )
                .then(function(response) {
                    hitsDone = response.data.hits_done;
                    if (vm.sortedResults.length === 0) {
                        vm.sortedResults = response.data.results;
                    } else {
                        vm.sortedResults = vm.mergeLists(
                            vm.sortedResults,
                            response.data.results
                        );
                    }
                    if (hitsDone < vm.resultsLength) {
                        vm.recursiveLookup(hitsDone);
                    } else {
                        vm.start = "0";
                        vm.end = "0";
                        vm.getKwicResults(vm, hitsDone);
                        vm.loading = false;
                    }
                });
        },
        getKwicResults(vm, hitsDone) {
            let start = parseInt(vm.start);
            let end = 0;
            if (vm.results_per_page === "") {
                end = start + 25;
            } else {
                end = start + parseInt(vm.results_per_page);
            }
            vm.$http
                .post(
                    "http://anomander.uchicago.edu/philologic/frantext0917/scripts/get_sorted_kwic.py",
                    JSON.stringify({
                        results: vm.sortedResults,
                        hits_done: hitsDone,
                        query_string: this.paramsToUrlString(
                            this.$store.state.formData
                        ),
                        start: start,
                        end: end,
                        sort_keys: [
                            vm.first_kwic_sorting_option,
                            vm.second_kwic_sorting_option,
                            vm.third_kwic_sorting_option
                        ]
                    })
                )
                .then(function(response) {
                    vm.results = response.data;
                });
        },
        initializePos(index) {
            var start = this.results.description.start;
            var currentPos = start + index;
            var currentPosLength = currentPos.toString().length;
            var endPos = start + parseInt(this.results.results_per_page || 25);
            var endPosLength = endPos.toString().length;
            var spaces = endPosLength - currentPosLength + 1;
            return currentPos + "." + Array(spaces).join("&nbsp");
        },
        sortResults() {
            if (this.resultsLength < 50000) {
                this.results = {};
                this.$router.push(
                    this.paramsToRoute(this.$store.state.formData)
                );
            } else {
                alert(
                    "For performance reasons, you cannot sort KWIC reports of more than 50,000 results. Please narrow your query to filter results."
                );
            }
        },
        dicoLookup() {}
    }
};
</script>

<style scoped>
#kwic-concordance {
    font-family: monospace;
}
.kwic_line {
    line-height: 180%;
    white-space: nowrap;
    overflow: hidden;
}
.kwic_biblio {
    font-weight: 400 !important;
    z-index: 10;
}
.short_biblio {
    width: 200px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    display: inline-block;
    vertical-align: bottom;
    margin-left: -5px;
    padding-left: 5px;
}
.full_biblio {
    z-index: 10;
    display: none;
    opacity: 0;
}
.full_biblio.show {
    position: absolute;
    background-color: #fff;
    box-shadow: 5px 5px 15px #c0c0c0;
    display: inline !important;
    padding: 0px 5px;
    margin-left: -5px;
    opacity: 1;
}
/deep/ .kwic-before {
    text-align: right;
    overflow: hidden;
    display: inline-block;
    position: absolute;
}
/deep/ .inner-before {
    float: right;
}
/deep/ .kwic-after {
    text-align: left;
    display: inline-block;
}
/deep/ .kwic-text {
    display: inline-block;
    overflow: hidden;
    vertical-align: bottom;
}
#kwic-switch {
    margin-left: -3px;
}
@media (min-width: 1300px) {
    /deep/ .kwic-highlight {
        margin-left: 330px;
    }
    /deep/ .kwic-before {
        width: 330px;
    }
}
@media (min-width: 992px) and (max-width: 1299px) {
    /deep/ .kwic-highlight {
        margin-left: 230px;
    }
    /deep/ .kwic-before {
        width: 230px;
    }
}
@media (min-width: 768px) and (max-width: 991px) {
    /deep/ .kwic-highlight {
        margin-left: 120px;
    }
    /deep/ .kwic-before {
        width: 120px;
    }
    /deep/ .kwic_line {
        font-size: 12px;
    }
}
@media (max-width: 767px) {
    /deep/ .kwic-highlight {
        margin-left: 200px;
    }
    /deep/ .kwic-before {
        width: 200px;
    }
    /deep/ .kwic_line {
        font-size: 12px;
    }
}
</style>
