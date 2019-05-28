<template>
    <div>
        <b-row>
            <b-col sm="10" offset-sm="1" xl="8" offset-xl="2">
                <b-card no-body class="shadow">
                    <b-form @submit="onSubmit" @reset="onReset">
                        <div id="form_body">
                            <div id="initial-form">
                                <b-button-group id="report" style="width: 100%">
                                    <b-button
                                        :id="report"
                                        v-for="searchReport in reports"
                                        @click="reportChange(searchReport.value)"
                                        :key="searchReport.value"
                                        :class="{'active':  report == searchReport.value}"
                                    >{{ searchReport.label }}</b-button>
                                </b-button-group>
                                <div id="search_terms_container" class="p-2 pt-4">
                                    <b-row id="search_terms">
                                        <b-col cols="12" md="8">
                                            <b-input-group prepend="Search Terms">
                                                <b-input-group-prepend>
                                                    <b-button variant="outline-info">Tips</b-button>
                                                </b-input-group-prepend>

                                                <b-form-input type="text" v-model="q"></b-form-input>

                                                <b-input-group-append>
                                                    <b-button
                                                        variant="outline-secondary"
                                                        id="button-search"
                                                        type="submit"
                                                    >Search</b-button>
                                                </b-input-group-append>
                                            </b-input-group>
                                        </b-col>
                                        <b-col
                                            cols="12"
                                            md="4"
                                            v-if="!philoConfig.dictionary"
                                            id="search-buttons"
                                        >
                                            <b-button
                                                type="reset"
                                                id="reset_form"
                                                class="btn btn-danger"
                                                @click="onReset()"
                                            >Clear</b-button>
                                            <button
                                                type="button"
                                                id="show-search-form"
                                                class="btn btn-primary"
                                                data-display="none"
                                                @click="toggleForm()"
                                            >{{ searchOptionsButton }}</button>
                                        </b-col>
                                    </b-row>
                                </div>
                            </div>
                            <div
                                id="search-elements"
                                v-if="formOpen"
                                class="p-2 velocity-opposites-transition-slideDownBigIn"
                                data-velocity-opts="{ duration: 400 }"
                            >
                                <h5>Refine your search with the following options and fields:</h5>
                                <b-row>
                                    <b-col cols="12" sm="2">Search Terms</b-col>
                                    <b-col cols="12" sm="10">
                                        <b-row>
                                            <b-col cols="12" sm="2">
                                                <b-form-checkbox
                                                    id="checkbox-1"
                                                    v-model="approximate"
                                                    name="checkbox-1"
                                                    value="yes"
                                                    unchecked-value="no"
                                                >Approximate match</b-form-checkbox>
                                            </b-col>
                                            <b-col cols="12" sm="9" v-if="approximate === 'yes'">
                                                <b-dropdown
                                                    id="dropdown-1"
                                                    text="100%"
                                                    class="m-md-2"
                                                >
                                                    <b-dropdown-item
                                                        v-for="value in approximateValues"
                                                        @click="selectApproximate(value)"
                                                        :key="value"
                                                    >{{ value }}%</b-dropdown-item>
                                                </b-dropdown>or more
                                            </b-col>
                                        </b-row>
                                    </b-col>
                                </b-row>
                                <b-row id="method" class="p-2" v-if="report != 'collocation'">
                                    <b-col cols="12" sm="2">Search Terms</b-col>
                                    <b-col cols="12" sm="3" lg="2" id="method-buttons">
                                        <b-form-group>
                                            <b-form-radio-group
                                                id="btn-radios-3"
                                                v-model="method"
                                                :options="methodOptions"
                                                buttons
                                                stacked
                                                size="sm"
                                                name="radio-btn-stacked"
                                            ></b-form-radio-group>
                                        </b-form-group>
                                    </b-col>
                                    <b-col cols="12" sm="7" lg="8">
                                        <b-row>
                                            <b-col sm="8" md="5">
                                                <b-input-group
                                                    size="sm"
                                                    append="words in the same sentence"
                                                >
                                                    <b-form-input v-model="arg_proxy"></b-form-input>
                                                </b-input-group>
                                            </b-col>
                                            <b-col sm="4" md="7"></b-col>
                                            <b-col sm="8" md="5">
                                                <b-input-group
                                                    size="sm"
                                                    append="words in the same sentence"
                                                >
                                                    <b-form-input v-model="arg_phrase"></b-form-input>
                                                </b-input-group>
                                            </b-col>
                                        </b-row>
                                    </b-col>
                                </b-row>
                                <b-row
                                    v-for="localField in metadataDisplay"
                                    :key="localField.value"
                                >
                                    <b-col cols="12" class="pb-2">
                                        <div class="input-group">
                                            <div class="input-group-prepend">
                                                <span class="input-group-text">{{localField.label}}</span>
                                            </div>
                                            <input
                                                type="text"
                                                class="form-control"
                                                :name="localField.value"
                                                :placeholder="localField.example"
                                                v-model="metadataValues[localField.value]"
                                            >
                                        </div>
                                    </b-col>
                                </b-row>
                                <b-row id="collocation-options" v-if="report === 'collocation'">
                                    <b-col cols="12">
                                        <b-row>
                                            <b-col cols="3" sm="2">Word Filtering</b-col>
                                            <b-col cols="3" sm="1">
                                                <b-form-input
                                                    name="filter_frequency"
                                                    placeholder="100"
                                                    v-model="filter_frequency"
                                                ></b-form-input>
                                            </b-col>
                                            <b-col cols="6" sm="2">
                                                <b-form-group>
                                                    <b-form-radio-group
                                                        id="btn-radios-3"
                                                        v-model="colloc_filter_choice"
                                                        :options="collocationOptions"
                                                        buttons
                                                        stacked
                                                        size="sm"
                                                        name="radio-btn-stacked"
                                                    ></b-form-radio-group>
                                                </b-form-group>
                                            </b-col>
                                        </b-row>
                                    </b-col>
                                </b-row>
                                <b-row id="time-series-options" v-if="report === 'time_series'">
                                    <b-col cols="12" sm="2">Date range:</b-col>
                                    <b-col cols="12" sm="10">
                                        from
                                        <input
                                            type="text"
                                            name="start_date"
                                            id="start_date"
                                            style="width:35px;"
                                            v-model="start_date"
                                        >
                                        to
                                        <input
                                            type="text"
                                            name="end_date"
                                            id="end_date"
                                            style="width:35px;"
                                            v-model="end_date"
                                        >
                                    </b-col>
                                </b-row>
                                <b-row id="date_range" v-if="report == 'time_series'">
                                    <b-col cols="12" sm="2">Year interval:</b-col>
                                    <b-col cols="12" sm="10">
                                        every
                                        <input
                                            type="text"
                                            name="year_interval"
                                            id="year_interval"
                                            style="width:35px; text-align: center;"
                                            v-model="year_interval"
                                        >&nbsp;years
                                    </b-col>
                                </b-row>
                                <b-row
                                    id="sort-options"
                                    v-if="report === 'concordance' || report === 'bibliography'"
                                >
                                    <b-col cols="12" style="margin-top: 10px;">
                                        <b-row>
                                            <b-col cols="3" sm="2">Sort results by</b-col>
                                            <b-col cols="6" sm="4">
                                                <b-form-select
                                                    v-model="sort_by"
                                                    :options="sortValues"
                                                    class="mb-3"
                                                >
                                                    <option>Sort results by</option>
                                                </b-form-select>
                                            </b-col>
                                        </b-row>
                                    </b-col>
                                </b-row>
                                <b-row
                                    id="results_per_page"
                                    v-if="report != 'collocation' && report != 'time_series'"
                                >
                                    <b-col cols="12" sm="2">Results per page:</b-col>
                                    <b-col cols="12" sm="10">
                                        <b-form-group>
                                            <b-form-radio-group
                                                id="btn-radios-3"
                                                v-model="results_per_page"
                                                :options="resultsPerPageOptions"
                                                buttons
                                                size="sm"
                                                name="radio-btn"
                                            ></b-form-radio-group>
                                        </b-form-group>
                                    </b-col>
                                </b-row>
                            </div>
                        </div>
                    </b-form>
                </b-card>
            </b-col>
        </b-row>
    </div>
</template>

<script>
import { mapFields } from "vuex-map-fields";
import { EventBus } from "../main.js";

export default {
    name: "SearchForm",
    computed: {
        // When using nested data structures, the string
        // after the last dot (e.g. `firstName`) is used
        // for defining the name of the computed property.
        ...mapFields([
            "formData.report",
            "formData.q",
            "formData.colloc_filter_choice",
            "formData.filter_frequency",
            "formData.approximate",
            "formData.approximate_ratio",
            "formData.method",
            "formData.arg_proxy",
            "formData.arg_phrase",
            "formData.metadataFields",
            "formData.start_date",
            "formData.end_date",
            "formData.year_interval",
            "formData.sort_by",
            "formData.results_per_page"
        ]),
        formData() {
            return this.$store.state.formData;
        },
        sortValues() {
            let sortValues = [
                {
                    value: "rowid",
                    text: "select"
                }
            ];
            for (let fields of this.philoConfig.concordance_biblio_sorting) {
                let label = [];
                for (let field of fields) {
                    if (field in this.philoConfig.metadata_aliases) {
                        label.push(this.philoConfig.metadata_aliases[field]);
                    } else {
                        label.push(field);
                    }
                }
                sortValues.push({ text: label.join(", "), value: fields });
            }
            return sortValues;
        }
    },
    data() {
        return {
            philoConfig: this.$philoConfig,
            formOpen: false,
            searchOptionsButton: "Show search options",
            approximateValues: [50, 60, 70, 80, 90],
            methodOptions: [
                { text: "Within", value: "proxy" },
                { text: "Exactly", value: "phrase" },
                { text: "In the same sentence", value: "cooc" }
            ],
            metadataDisplay: [],
            metadataValues: {},
            collocationOptions: [
                { text: "Most Frequent Terms", value: "frequency" },
                { text: "Stopwords", value: "stopwords" },
                { text: "No Filtering", value: "nofilter" }
            ],
            selectedSortValues: "rowid",
            resultsPerPageOptions: [25, 100, 500, 1000]
        };
    },
    created() {
        this.reports = this.buildReports();
        for (let metadataField of this.philoConfig.metadata) {
            let metadataObj = {
                label: metadataField[0].toUpperCase() + metadataField.slice(1),
                value: metadataField,
                example: this.philoConfig.search_examples[metadataField]
            };
            if (metadataField in this.philoConfig.metadata_aliases) {
                metadataObj.label = this.philoConfig.metadata_aliases[
                    metadataField
                ];
            }
            this.metadataDisplay.push(metadataObj);
            if (metadataField in this.metadataFields) {
                this.metadataValues[metadataField] = this.metadataFields[
                    metadataField
                ];
            }
        }
        var vm = this;
        EventBus.$on("metadataUpdate", function(metadata) {
            for (let field in metadata) {
                vm.metadataValues[field] = metadata[field];
            }
        });
    },
    methods: {
        buildReports() {
            let reports = [];
            for (let value of this.philoConfig.search_reports) {
                let label = value.replace("_s", "-s");
                label = label.charAt(0).toUpperCase() + label.slice(1);
                reports.push({
                    value: value,
                    label: label
                });
            }
            return reports;
        },
        buildMetadataFieldDisplay() {
            for (let metadataField of this.philoConfig.metadata) {
                let metadataObj = {
                    label:
                        metadataField[0].toUpperCase() + metadataField.slice(1),
                    value: metadataField,
                    example: this.philoConfig.search_examples[metadataField]
                };
                if (metadataField in this.philoConfig.metadata_aliases) {
                    metadataObj.label = this.philoConfig.metadata_aliases[
                        metadataField
                    ];
                }
                this.metadataValues[metadataField] = "";
                this.metadataDisplay.push(metadataObj);
            }
        },
        generateSortValues() {
            let sortValues = [
                {
                    value: ["rowid"],
                    label: "select"
                }
            ];
            for (let fields of this.philoConfig.concordance_biblio_sorting) {
                let label = [];
                for (let field of fields) {
                    if (field in this.philoConfig.metadata_aliases) {
                        label.push(this.philoConfig.metadata_aliases[field]);
                    } else {
                        label.push(field);
                    }
                }
                sortValues.push({ label: label.join(", "), value: fields });
            }
            return sortValues;
        },
        onSubmit(event) {
            event.preventDefault();
            this.$store.commit("updateMetadata", this.metadataValues);
            this.q = this.q.trim();
            if (this.q.length == 0) {
                this.report = "bibliography";
            }
            this.formOpen = false;
            this.$router.push(this.paramsToRoute(this.$store.state.formData));
        },
        onReset(evt) {
            evt.preventDefault();
            // Reset our form values
            this.form.email = "";
            this.form.name = "";
            this.form.food = null;
            this.form.checked = [];
            // Trick to reset/clear native browser form validation state
            this.show = false;
            this.$nextTick(() => {
                this.show = true;
            });
        },
        reportChange(report) {
            if (report === "landing_page") {
                this.report = this.philoConfig.search_reports[0];
            } else if (report === "collocation") {
                if (this.philoConfig.stopwords.length > 0) {
                    this.colloc_filter_choice = "stopwords";
                } else {
                    this.colloc_filter_choice = "frequency";
                }
            }
            this.report = report;
        },
        toggleForm() {
            if (!this.formOpen) {
                this.formOpen = true;
                this.searchOptionsButton = "Hide search options";
            } else {
                this.formOpen = false;
                this.searchOptionsButton = "Show search options";
            }
        },
        clearFormData() {},
        selectApproximate(approximateValue) {
            this.approximate_ratio = approximateValue;
        }
    }
};
</script>

<style>
#report .btn {
    font-variant: small-caps;
}
.dico-margin {
    margin-top: 210px !important;
}

#search-elements.dico {
    margin-top: 168px;
}

#search-elements > h5 {
    margin-top: 15px;
    margin-bottom: 15px;
}

#report label {
    font-size: 1.1em;
    font-variant: small-caps;
    text-transform: capitalize;
}

.search_box {
    width: 250px;
    vertical-align: middle;
}

#search_field {
    font-weight: 400;
}

#more_options {
    width: 200px;
}

#more_options:hover {
    cursor: pointer;
}

#search_terms_container {
    padding-top: 15px;
    padding-bottom: 15px;
}

#search_terms,
#head-search-container {
    text-align: center;
}

#head-search-container {
    margin-top: -10px;
    padding-bottom: 15px;
}

.no-example {
    display: none;
}

#method,
.metadata_fields,
#collocation-options > div,
#time-series-options > div {
    margin-top: 10px;
}

#method,
.metadata_fields.row,
#time_series_num.row,
#date_range.row,
#results_per_page.row,
#collocation-options > div,
#time-series-options > div {
    padding-top: 10px;
    padding-bottom: 10px;
}

#initial-form .btn-primary.active {
    box-shadow: 0px 0px;
    border-top: 0px;
}

#tip-text {
    display: none;
}

#tip-btn:hover #tip-text {
    display: inline;
}

#tip-btn:hover #tip {
    display: none;
}

#search_terms .row {
    text-align: left;
    padding-left: 20px;
    padding-right: 20px;
}

@media (max-width: 768px) {
    #collocation-options .row {
        margin-left: -15px;
    }
}

/*Dico layout changes*/

#search_elements {
    border-top-width: 0px;
}

/*Responsiveness*/

@media (min-width: 1201px) {
    #initial-form,
    #search-elements {
        left: 100px;
        right: 100px;
    }
}

@media (max-width: 1200px) {
    #initial-form,
    #search-elements {
        left: 70px;
        right: 70px;
    }
}

@media (max-width: 992px) {
    #search-buttons {
        padding-top: 15px;
    }
    #search_terms > div:nth-of-type(2),
    #head-search-container .metadata_fields div:nth-of-type(2) {
        padding-right: 20px;
        padding-left: 20px;
    }
    #head-search-container #metadata-fields #initial-form,
    #search-elements {
        left: 40px;
        right: 40px;
    }
    #philologic_response {
        margin-top: 170px;
    }
    #search-elements {
        margin-top: 148px;
    }
    #search-elements.dico {
        margin-top: 217px;
    }
    .dico-margin {
        margin-top: 245px !important;
    }
}

@media (max-width: 768px) {
    #right-act-on-report .btn-group {
        float: left !important;
    }
    #search-elements {
        padding-right: 20px;
        margin-top: 160px;
    }
    #search-elements.dico {
        margin-top: 248px;
    }
    #philologic_response {
        margin-top: 180px;
    }
    #initial-form,
    #search-elements {
        left: 0px;
        right: 0px;
    }
    #kwic,
    #time_series {
        display: none;
    }
    .dico-margin {
        margin-top: 270px !important;
    }
}

.select {
    font-size: inherit;
    position: relative;
    display: inline-block;
    width: 100%;
    text-align: center;
}

.select select {
    outline: none;
    -webkit-appearance: none;
    display: block;
    padding: 6px 12px;
    margin: 0;
    transition: border-color 0.2s;
    border: 1px solid #ccc;
    border-radius: 0px;
    background: #fff;
    color: #555;
    line-height: normal;
    font-family: inherit;
    font-size: inherit;
    line-height: inherit;
    width: 100%;
}
</style>