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
                    <search-arguments></search-arguments>
                </div>
                <!-- <progress-bar
                            progress="{{ percent }}"
                            style="margin-left: 15px; margin-right: 15px; margin-top: -10px;"
                ></progress-bar>-->
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
            startDate: "formData.start_date",
            endDate: "formData.end_date",
            interval: "formData.year_interval"
        })
    },
    data() {
        return {
            frequencyType: "absolute_time",
            resultsLength: 0,
            totalResults: 0,
            globalQuery: "",
            localQuery: "",
            myBarChart: null,
            absoluteCounts: [],
            dateCounter: [],
            relativeCounts: [],
            moreResults: false,
            percent: 0,
            done: false,
            authorized: true
        };
    },
    created() {
        this.report = "time_series";
        this.fetchResults();
    },
    methods: {
        fetchResults() {
            if (this.interval == "") {
                this.interval = 10;
            }
            this.resultsLength = 0;
            this.frequencyType = "absolute_time";
            var vm = this;
            this.$http
                .get(
                    "http://anomander.uchicago.edu/philologic/test/scripts/get_start_end_date.py",
                    {
                        params: vm.paramsFilter(vm.$store.state.formData)
                    }
                )
                .then(function(response) {
                    // if no dates supplied or if invalid dates
                    vm.startDate = parseInt(response.data.start_date);
                    vm.endDate = parseInt(response.data.end_date);
                    vm.interval = parseInt(vm.interval);
                    vm.totalResults = response.data.total_results;

                    // Store the current query as a local and global variable in order to make sure they are equal later on...
                    vm.globalQuery = {
                        ...vm.$store.state.formData,
                        start_date: vm.startDate,
                        end_date: vm.endDate
                    };
                    vm.localQuery = vm.copyObject(vm.globalQuery);

                    var dateList = [];
                    var zeros = [];
                    for (
                        let i = vm.startDate;
                        i <= vm.endDate;
                        i += vm.interval
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
                    if (vm.myBarChart != null) {
                        vm.myBarChart.destroy();
                    }
                    var chart = document.querySelector("#bar");
                    // var font = chart.css("font-family");
                    // Chart.defaults.global.fontFamily = font;
                    // var backgroundColor = angular
                    //     .element(".btn-primary")
                    //     .css("background-color");
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
                            vm.$store.commit("updateMetadata", { year: year });
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

                    vm.absoluteCounts = vm.copyObject(zeros);
                    vm.relativeCounts = vm.copyObject(zeros);
                    vm.dateCounts = {};
                    var fullResults;
                    vm.updateTimeSeries(vm, fullResults);
                })
                .catch(function(response) {
                    console.log(response);
                });
        },
        updateTimeSeries(vm, fullResults) {
            vm.$http
                .get(
                    "http://anomander.uchicago.edu/philologic/test/reports/time_series.py",
                    {
                        params: {
                            ...vm.paramsFilter(vm.$store.state.formData),
                            start_date: vm.startDate,
                            max_time: 5,
                            year_interval: vm.interval
                        }
                    }
                )
                .then(function(results) {
                    vm.loading = false;
                    var timeSeriesResults = results.data;
                    vm.resultsLength += timeSeriesResults.results_length;
                    vm.resultsLength = vm.resultsLength;
                    vm.moreResults = timeSeriesResults.more_results;
                    vm.startDate = timeSeriesResults.new_start_date;
                    for (let date in timeSeriesResults.results.date_count) {
                        // Update date counts
                        vm.dateCounts[date] =
                            timeSeriesResults.results.date_count[date];
                    }
                    vm.percent = Math.floor(
                        (vm.resultsLength / vm.totalResults) * 100
                    );
                    vm.sortAndRenderTimeSeries(
                        vm,
                        fullResults,
                        timeSeriesResults
                    );
                })
                .catch(function(response) {
                    console.log(response);
                    vm.loading = false;
                });
        },
        sortAndRenderTimeSeries(vm, fullResults, timeSeriesResults) {
            var allResults = this.mergeResults(
                fullResults,
                timeSeriesResults.results["absolute_count"],
                "label"
            );
            fullResults = allResults.unsorted;
            for (let i = 0; i < allResults.sorted.length; i += 1) {
                var date = allResults.sorted[i].label;
                var value = allResults.sorted[i].count;
                vm.absoluteCounts[i] = value;
                vm.relativeCounts[i] =
                    Math.round((value / vm.dateCounts[date]) * 10000 * 100) /
                    100;
                if (isNaN(vm.relativeCounts[i])) {
                    vm.relativeCounts[i] = 0;
                }
            }
            vm.myBarChart.data.datasets[0].data = vm.absoluteCounts;
            vm.myBarChart.update();
            // this.$nextTick(function() {
            //     vm.chartLinker(vm);
            // });
            if (
                vm.report === "time_series" &&
                vm.deepEqual(vm.globalQuery, vm.localQuery)
            ) {
                // are we running a different query?
                if (vm.moreResults) {
                    vm.updateTimeSeries(vm, fullResults);
                } else {
                    vm.percent = 100;
                    vm.done = true;
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
        }
    }
};
</script>
<style scoped>
</style>
