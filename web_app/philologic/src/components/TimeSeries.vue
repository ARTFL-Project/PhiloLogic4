<template>
    <div id="time-series-container">
        <div id="philo-view" v-if="authorized">
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
                <b-progress
                    :max="totalResults"
                    show-progress
                    variant="secondary"
                    class="ml-3 mr-3 mb-3"
                    v-if="resultsLength != totalResults"
                >
                    <b-progress-bar
                        :value="resultsLength"
                        :label="`${((resultsLength / totalResults) * 100).toFixed(2)}%`"
                    ></b-progress-bar>
                </b-progress>
            </b-card>
            <b-card no-body id="time-series" class="m-4">
                <b-button-group class="d-inline-block">
                    <b-button
                        :class="{'active':  frequencyType == 'absolute_time'}"
                        @click="toggleFrequency('absolute_time')"
                    >Absolute Frequency</b-button>
                    <b-button
                        :class="{'active':  frequencyType == 'relative_time'}"
                        @click="toggleFrequency('relative_time')"
                    >Relative Frequency</b-button>
                </b-button-group>
                <div class="p-3 mt-4" style="min-height: 500px; max-height: 800px">
                    <canvas id="bar" class="chart"></canvas>
                </div>
            </b-card>
        </div>
        <!-- <access-control v-if="!authorized"></access-control> -->
    </div>
</template>
<script>
import Chart from "chart.js/dist/Chart.js";
import { mapFields } from "vuex-map-fields";
import searchArguments from "./SearchArguments";
import { EventBus } from "../main.js";

export default {
    name: "timeSeries",
    components: {
        searchArguments
    },
    computed: {
        ...mapFields({
            report: "formData.report",
            interval: "formData.year_interval",
            currentReport: "currentReport"
        })
    },
    data() {
        return {
            frequencyType: "absolute_time",
            resultsLength: 0,
            totalResults: 100,
            globalQuery: "",
            localQuery: "",
            myBarChart: null,
            absoluteCounts: [],
            dateCounter: [],
            relativeCounts: [],
            moreResults: false,
            done: false,
            authorized: true,
            startDate: "",
            endDate: ""
        };
    },
    created() {
        this.report = "time_series";
        this.currentReport = "time_series";
        this.fetchResults();
        EventBus.$on("urlUpdate", () => {
            this.fetchResults();
        });
    },
    methods: {
        fetchResults() {
            if (this.interval == "") {
                this.interval = 10;
            }
            this.resultsLength = 0;
            this.frequencyType = "absolute_time";
            this.$http
                .get(
                    "http://anomander.uchicago.edu/philologic/frantext0917/scripts/get_start_end_date.py",
                    {
                        params: this.paramsFilter(this.$store.state.formData)
                    }
                )
                .then(response => {
                    // if no dates supplied or if invalid dates
                    if (
                        this.$store.state.formData.metadataFields.year.length >
                        0
                    ) {
                        let yearSplit = this.$store.state.formData.metadataFields.year.split(
                            "-"
                        );
                        if (
                            yearSplit[0].length > 0 &&
                            yearSplit[1].length > 0
                        ) {
                            // year is a range
                            this.startDate = parseInt(yearSplit[0]);
                            this.endDate = parseInt(yearSplit[1]);
                        } else if (
                            yearSplit[0].length > 0 &&
                            yearSplit[1].length < 1
                        ) {
                            // year is a range with just the start year provided
                            this.startDate = parseInt(yearSplit[0]);
                            this.endDate = parseInt(response.data.end_date);
                        } else if (
                            yearSplit[0].length < 1 &&
                            yearSplit[1].length > 0
                        ) {
                            // year is a range with just the end year provided
                            this.startDate = parseInt(response.data.start_date);
                            this.endDate = parseInt(yearSplit[1]);
                        } else {
                            // no year provided
                            this.startDate = parseInt(response.data.start_date);
                            this.endDate = parseInt(response.data.end_date);
                        }
                    }
                    console.log(this.startDate, this.endDate);
                    this.$store.dispatch("updateStartEndDate", {
                        startDate: this.startDate,
                        endDate: this.endDate
                    });
                    this.interval = parseInt(this.interval);
                    this.totalResults = response.data.total_results;
                    // Store the current query as a local and global variable in order to make sure they are equal later on...
                    this.globalQuery = this.copyObject(
                        this.$store.state.formData
                    );
                    this.localQuery = this.copyObject(this.globalQuery);

                    var dateList = [];
                    var zeros = [];
                    for (
                        let i = this.startDate;
                        i <= this.endDate;
                        i += this.interval
                    ) {
                        dateList.push(i);
                        zeros.push(0);
                    }
                    // Initialize Chart
                    Chart.defaults.global.responsive = true;
                    Chart.defaults.global.animation.duration = 400;
                    Chart.defaults.global.tooltipCornerRadius = 0;
                    Chart.defaults.global.maintainAspectRatio = false;
                    Chart.defaults.bar.scales.xAxes[0].gridLines.display = false;
                    if (this.myBarChart != null) {
                        this.myBarChart.destroy();
                    }
                    var chart = document.querySelector("#bar");
                    // var font = chart.css("font-family");
                    // Chart.defaults.global.fontFamily = font;
                    // var backgroundColor = angular
                    //     .element(".btn-primary")
                    //     .css("background-color");
                    var vm = this;
                    vm.myBarChart = new Chart(chart, {
                        type: "bar",
                        data: {
                            labels: dateList,
                            datasets: [
                                {
                                    label: "Absolute Frequency",
                                    backgroundColor: "rgba(0, 160, 205, .6)",
                                    // borderColor: backgroundColor,
                                    borderWidth: 1,
                                    hoverBackgroundColor:
                                        "rgba(0, 160, 205, .8)",
                                    // hoverBorderColor: backgroundColor,
                                    yAxisID: "absolute",
                                    data: zeros
                                }
                            ]
                        },
                        options: {
                            legend: {
                                display: false
                            },
                            scales: {
                                yAxes: [
                                    {
                                        type: "linear",
                                        display: true,
                                        position: "left",
                                        id: "absolute",
                                        gridLines: {
                                            // drawOnChartArea: false,
                                            offsetGridLines: true
                                        },
                                        ticks: {
                                            beginAtZero: true
                                        }
                                    }
                                ]
                            },
                            tooltips: {
                                cornerRadius: 0,
                                callbacks: {
                                    title: function(tooltipItem) {
                                        var interval;
                                        if (vm.interval == 1) {
                                            interval = tooltipItem[0].xLabel;
                                        } else {
                                            interval = `${
                                                tooltipItem[0].xLabel
                                            }-${parseInt(
                                                tooltipItem[0].xLabel
                                            ) +
                                                parseInt(vm.interval) -
                                                1}`;
                                        }
                                        return interval;
                                    },
                                    label: function(tooltipItem) {
                                        if (
                                            vm.frequencyType == "absolute_time"
                                        ) {
                                            return (
                                                tooltipItem.yLabel +
                                                " occurrences"
                                            );
                                        } else {
                                            return (
                                                tooltipItem.yLabel +
                                                " occurrences per 10,000 words"
                                            );
                                        }
                                    }
                                }
                            }
                        }
                    });
                    chart.onclick = function(evt) {
                        var activePoints = vm.myBarChart.getElementsAtEvent(
                            evt
                        );
                        if (activePoints.length > 0) {
                            var clickedElementindex = activePoints[0]["_index"];
                            var startDate = parseInt(
                                vm.myBarChart.data.labels[clickedElementindex]
                            );
                            let endDate = startDate + parseInt(vm.interval) - 1;
                            var year;
                            if (startDate == endDate) {
                                year = startDate;
                            } else {
                                year = `${startDate}-${endDate}`;
                            }
                            vm.$store.commit("updateMetadata", {
                                year: year
                            });
                            vm.$router.push(
                                vm.paramsToRoute({
                                    ...vm.$store.state.formData,
                                    report: "concordance",
                                    start_date: "",
                                    end_date: "",
                                    year_interval: ""
                                })
                            );
                        }
                    };

                    this.absoluteCounts = this.copyObject(zeros);
                    this.relativeCounts = this.copyObject(zeros);
                    this.dateCounts = {};
                    var fullResults;
                    this.updateTimeSeries(fullResults);
                })
                .catch(function(response) {
                    console.log(response);
                });
        },
        updateTimeSeries(fullResults) {
            this.$http
                .get(
                    "http://anomander.uchicago.edu/philologic/frantext0917/reports/time_series.py",
                    {
                        params: {
                            ...this.paramsFilter(this.$store.state.formData),
                            start_date: this.startDate,
                            max_time: 5,
                            year_interval: this.interval
                        }
                    }
                )
                .then(results => {
                    this.loading = false;
                    var timeSeriesResults = results.data;
                    this.resultsLength += timeSeriesResults.results_length;
                    this.resultsLength = this.resultsLength;
                    this.moreResults = timeSeriesResults.more_results;
                    this.startDate = timeSeriesResults.new_start_date;
                    for (let date in timeSeriesResults.results.date_count) {
                        // Update date counts
                        this.dateCounts[date] =
                            timeSeriesResults.results.date_count[date];
                    }
                    this.percent = Math.floor(
                        (this.resultsLength / this.totalResults) * 100
                    );
                    this.sortAndRenderTimeSeries(
                        fullResults,
                        timeSeriesResults
                    );
                })
                .catch(response => {
                    console.log(response);
                    this.loading = false;
                });
        },
        sortAndRenderTimeSeries(fullResults, timeSeriesResults) {
            var allResults = this.mergeResults(
                fullResults,
                timeSeriesResults.results["absolute_count"],
                "label"
            );
            fullResults = allResults.unsorted;
            for (let i = 0; i < allResults.sorted.length; i += 1) {
                var date = allResults.sorted[i].label;
                var value = allResults.sorted[i].count;
                this.absoluteCounts[i] = value;
                this.relativeCounts[i] =
                    Math.round((value / this.dateCounts[date]) * 10000 * 100) /
                    100;
                if (isNaN(this.relativeCounts[i])) {
                    this.relativeCounts[i] = 0;
                }
            }
            this.myBarChart.data.datasets[0].data = this.absoluteCounts;
            this.myBarChart.update();
            if (
                this.report === "time_series" &&
                this.deepEqual(this.globalQuery, this.localQuery)
            ) {
                // are we running a different query?
                if (this.moreResults) {
                    this.updateTimeSeries(fullResults);
                } else {
                    this.percent = 100;
                    this.done = true;
                    // angular.element("#relative_time").removeAttr("disabled");
                    // angular
                    //     .element(".progress")
                    //     .delay(500)
                    //     .velocity("slideUp");
                }
            }
        },
        toggleFrequency(frequencyType) {
            if (frequencyType == "absolute_time") {
                this.myBarChart.data.datasets[0].data = this.absoluteCounts;
                this.myBarChart.data.datasets[0].label = "Absolute Frequency";
                this.frequencyType = frequencyType;
            } else {
                this.myBarChart.data.datasets[0].data = this.relativeCounts;
                this.myBarChart.data.datasets[0].label = "Relative Frequency";
                this.frequencyType = frequencyType;
            }
            this.myBarChart.update();
        },
        afterDestroy: () => {
            console.log("destroying chart");
            this.myBarChart.destroy();
        }
    }
};
</script>
<style scoped>
</style>
