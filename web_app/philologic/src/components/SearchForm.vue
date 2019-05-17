<template>
    <div>
        <b-row>
            <b-col md="8" offset-md="2">
                <b-card no-body>
                    <form id="search" role="form">
                        <div id="form_body">
                            <div id="initial-form">
                                <b-button-group size="lg" id="report" style="width: 100%">
                                    <b-button
                                        :id="report"
                                        v-for="report in reports"
                                        @click="reportChange(report.value)"
                                        :key="report.value"
                                    >{{ report.label }}</b-button>
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
                                            <button
                                                type="reset"
                                                id="reset_form"
                                                class="btn btn-danger"
                                                @click="clearFormData()"
                                            >Clear</button>
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
                                <b-row v-for="metadata in metadataDisplay" :key="metadata.value">
                                    <b-col cols="12" class="pb-2">
                                        <div class="input-group">
                                            <div class="input-group-prepend">
                                                <span class="input-group-text">{{metadata.label}}</span>
                                            </div>
                                            <input
                                                type="text"
                                                class="form-control"
                                                :placeholder="metadata.example"
                                                v-model="metadata.value"
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
                            </div>
                        </div>
                    </form>
                </b-card>
            </b-col>
        </b-row>
        <!--
                        <time-series-options v-if="formData.report == 'time_series'"></time-series-options>
                        <sort-results
                            v-if="formData.report === 'concordance' || formData.report === 'bibliography'"
                        ></sort-results>
                        <results-per-page
                            v-if="formData.report != 'collocation' && formData.report != 'time_series'"
        ></results-per-page>-->
    </div>
</template>

<script>
import { mapFields } from "vuex-map-fields";

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
            "formData.year_interval"
        ])
    },
    data() {
        return {
            philoConfig: this.$philoConfig,
            formOpen: true,
            searchOptionsButton: "Show search options",
            approximateValues: [50, 60, 70, 80, 90],
            methodOptions: [
                { text: "Within", value: "proxy" },
                { text: "Exactly", value: "phrase" },
                { text: "In the same sentence", value: "cooc" }
            ],
            metadataDisplay: [],
            collocationOptions: [
                { text: "Most Frequent Terms", value: "frequency" },
                { text: "Stopwords", value: "stopwords" },
                { text: "No Filtering", value: "nofilter" }
            ]
        };
    },
    created() {
        let reports = [];
        for (let value of this.philoConfig.search_reports) {
            let label = value.replace("_", " ");
            reports.push({
                value: value,
                label: label
            });
        }
        console.log(reports);
        this.reports = reports;
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
            this.metadataFields[metadataField] = "";
            this.metadataDisplay.push(metadataObj);
            console.log(metadataObj);
        }
        console.log(this.metadataFields);
    },
    methods: {
        submit() {},
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
        selectApproximat(value) {
            this.approximate_ratio = value;
        }
    }
};
</script>

<style>
</style>