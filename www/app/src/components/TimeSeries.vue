<template>
    <div class="container-fluid" role="main">
        <div id="time-series-container" class="mt-4 mx-2">
            <results-summary :description="results.description" :running-total="runningTotal"></results-summary>
            <div class="card mt-4" id="time-series">
                <div class="btn-group d-inline-block" role="group">
                    <button type="button" class="btn btn-secondary"
                        :class="{ active: frequencyType == 'absolute_time' }" @click="toggleFrequency('absolute_time')">
                        {{ $t("common.absoluteFrequency") }}
                    </button>
                    <button type="button" class="btn btn-secondary"
                        :class="{ active: frequencyType == 'relative_time' }" @click="toggleFrequency('relative_time')">
                        {{ $t("common.relativeFrequency") }}
                    </button>
                </div>
                <div class="p-3 mt-4" style="min-height: 500px; max-height: 800px">
                    <canvas id="bar" class="chart" aria-label="Bar Graph"></canvas>
                </div>
            </div>
        </div>
    </div>
</template>
<script>
import Chart from "chart.js/dist/Chart.min.js";
import { mapFields } from "vuex-map-fields";
import cssVariables from "../assets/styles/theme.module.scss";
import ResultsSummary from "./ResultsSummary";

export default {
    name: "timeSeries",
    components: {
        ResultsSummary,
    },
    inject: ["$http"],
    provide() {
        return {
            results: this.results.results,
        };
    },
    computed: {
        ...mapFields({
            report: "formData.report",
            interval: "formData.year_interval",
            start_date: "formData.start_date",
            end_date: "formData.end_date",
            currentReport: "currentReport",
            searching: "searching",
            resultsLength: "resultsLength",
            urlUpdate: "urlUpdate",
            accessAuthorized: "accessAuthorized",
        }),
    },
    data() {
        return {
            frequencyType: "absolute_time",
            totalResults: 100,
            globalQuery: "",
            localQuery: "",
            myBarChart: null,
            absoluteCounts: [],
            dateCounter: [],
            relativeCounts: [],
            moreResults: false,
            done: false,
            startDate: "",
            endDate: "",
            results: [],
            runningTotal: 0,
        };
    },
    mounted() {
        this.report = "time_series";
        this.currentReport = "time_series";
        this.fetchResults();
    },
    watch: {
        urlUpdate() {
            if (this.report == "time_series") {
                this.fetchResults();
            }
        },
    },
    beforeUnmount() {
        this.myBarChart.destroy();
    },
    methods: {
        fetchResults() {
            this.runningTotal = 0;
            if (this.interval == "") {
                this.interval = this.$philoConfig.time_series.interval;
            }
            this.interval = parseInt(this.interval);
            this.frequencyType = "absolute_time";
            this.searching = true;
            this.startDate = parseInt(this.start_date || this.$philoConfig.time_series_start_end_date.start_date);
            this.endDate = parseInt(this.end_date || this.$philoConfig.time_series_start_end_date.end_date);
            this.$store.dispatch("updateStartEndDate", {
                startDate: this.startDate,
                endDate: this.endDate,
            });
            // Store the current query as a local and global variable in order to make sure they are equal later on...
            this.globalQuery = this.copyObject(this.$store.state.formData);
            this.localQuery = this.copyObject(this.globalQuery);

            var dateList = [];
            var zeros = [];
            for (let i = this.startDate; i <= this.endDate; i += this.interval) {
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
            var vm = this;
            vm.myBarChart = new Chart(chart, {
                type: "bar",
                data: {
                    labels: dateList,
                    datasets: [
                        {
                            label: this.$t("common.absoluteFrequency"),
                            backgroundColor: cssVariables.color,
                            borderWidth: 1,
                            hoverBackgroundColor: this.hexToRGBA(cssVariables.color),
                            yAxisID: "absolute",
                            data: zeros,
                        },
                    ],
                },
                options: {
                    legend: {
                        display: false,
                    },
                    scales: {
                        yAxes: [
                            {
                                type: "linear",
                                display: true,
                                position: "left",
                                id: "absolute",
                                gridLines: {
                                    offsetGridLines: true,
                                },
                                ticks: {
                                    beginAtZero: true,
                                },
                            },
                        ],
                    },
                    tooltips: {
                        cornerRadius: 0,
                        callbacks: {
                            title: function (tooltipItem) {
                                var interval;
                                if (vm.interval == 1) {
                                    interval = tooltipItem[0].xLabel;
                                } else {
                                    interval = `${tooltipItem[0].xLabel}-${parseInt(tooltipItem[0].xLabel) + parseInt(vm.interval) - 1
                                        }`;
                                }
                                return interval;
                            },
                            label: function (tooltipItem) {
                                if (vm.frequencyType == "absolute_time") {
                                    return tooltipItem.yLabel + ` ${vm.$t("timeSeries.occurrences")}`;
                                } else {
                                    return tooltipItem.yLabel + ` ${vm.$t("timeSeries.per1000Words")}`;
                                }
                            },
                        },
                    },
                },
            });
            chart.onclick = function (evt) {
                var activePoints = vm.myBarChart.getElementsAtEvent(evt);
                if (activePoints.length > 0) {
                    var clickedElementindex = activePoints[0]["_index"];
                    var startDate = parseInt(vm.myBarChart.data.labels[clickedElementindex]);
                    let endDate = startDate + parseInt(vm.interval) - 1;
                    var year;
                    if (startDate == endDate) {
                        year = startDate.toString();
                    } else {
                        year = `${startDate}-${endDate}`;
                    }
                    vm.$store.commit("updateFormDataField", {
                        key: "year",
                        value: year,
                    });
                    vm.$router.push(
                        vm.paramsToRoute({
                            ...vm.$store.state.formData,
                            report: "concordance",
                            start_date: "",
                            end_date: "",
                            year_interval: "",
                        })
                    );
                }
            };

            this.absoluteCounts = this.copyObject(zeros);
            this.relativeCounts = this.copyObject(zeros);
            this.dateCounts = {};
            var fullResults;
            this.updateTimeSeries(fullResults);
        },
        updateTimeSeries(fullResults) {
            this.$http
                .get(`${this.$dbUrl}/reports/time_series.py`, {
                    params: {
                        ...this.paramsFilter({ ...this.$store.state.formData }),
                        start_date: this.startDate,
                        max_time: 5,
                        year_interval: this.interval,
                    },
                })
                .then((results) => {
                    this.searching = false;
                    var timeSeriesResults = results.data;
                    this.results = results.data;
                    this.runningTotal += timeSeriesResults.results_length;
                    this.moreResults = timeSeriesResults.more_results;
                    this.startDate = timeSeriesResults.new_start_date;
                    for (let date in timeSeriesResults.results.date_count) {
                        this.dateCounts[date] = timeSeriesResults.results.date_count[date];
                    }
                    this.sortAndRenderTimeSeries(fullResults, timeSeriesResults);
                })
                .catch((response) => {
                    this.debug(this, response);
                    this.searching = false;
                });
        },
        sortAndRenderTimeSeries(fullResults, timeSeriesResults) {
            var allResults = this.mergeResults(fullResults, timeSeriesResults.results["absolute_count"], "label");
            fullResults = allResults.unsorted;
            for (let i = 0; i < allResults.sorted.length; i += 1) {
                var date = allResults.sorted[i].label;
                var value = allResults.sorted[i].count;
                this.absoluteCounts[i] = value;
                this.relativeCounts[i] = Math.round((value / this.dateCounts[date]) * 10000 * 100) / 100;
                if (isNaN(this.relativeCounts[i])) {
                    this.relativeCounts[i] = 0;
                }
            }
            this.myBarChart.data.datasets[0].data = this.absoluteCounts;
            this.myBarChart.update();
            if (this.report === "time_series" && this.deepEqual(this.globalQuery, this.localQuery)) {
                // are we running a different query?
                if (this.moreResults) {
                    this.updateTimeSeries(fullResults);
                } else {
                    this.runningTotal = this.resultsLength;
                    this.done = true;
                }
            }
        },
        toggleFrequency(frequencyType) {
            if (frequencyType == "absolute_time") {
                this.myBarChart.data.datasets[0].data = this.absoluteCounts;
                this.myBarChart.data.datasets[0].label = this.$t("common.absoluteFrequency");
                this.frequencyType = frequencyType;
            } else {
                this.myBarChart.data.datasets[0].data = this.relativeCounts;
                this.myBarChart.data.datasets[0].label = this.$t("common.relativeFrequency");
                this.frequencyType = frequencyType;
            }
            this.myBarChart.update();
        },
        hexToRGBA(h) {
            let r = 0,
                g = 0,
                b = 0;

            // 3 digits
            if (h.length == 4) {
                r = "0x" + h[1] + h[1];
                g = "0x" + h[2] + h[2];
                b = "0x" + h[3] + h[3];

                // 6 digits
            } else if (h.length == 7) {
                r = "0x" + h[1] + h[2];
                g = "0x" + h[3] + h[4];
                b = "0x" + h[5] + h[6];
            }
            return "rgba(" + +r + "," + +g + "," + +b + ", .7)";
        },
    },
};
</script>
<style scoped>
#description {
    position: relative;
}

#export-results {
    position: absolute;
    right: 0;
    padding: 0.125rem 0.25rem;
    font-size: 0.8rem !important;
}
</style>
