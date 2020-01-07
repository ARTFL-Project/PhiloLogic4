(function() {
    "use strict";

    angular
        .module('philoApp')
        .directive('timeSeriesChart', timeSeriesChart);

    function timeSeriesChart($rootScope, $http, $location, $timeout, philoConfig, progressiveLoad, URL, request, saveToLocalStorage) {
        var updateTimeSeries = function(scope, formData, fullResults) {
            request.report(formData, {
                start_date: scope.startDate,
                max_time: 5
            }).then(function(results) {
                scope.timeSeries.loading = false;
                var timeSeriesResults = results.data;
                scope.resultsLength += timeSeriesResults.results_length;
                scope.timeSeries.resultsLength = scope.resultsLength;
                scope.moreResults = timeSeriesResults.more_results;
                scope.startDate = timeSeriesResults.new_start_date;
                for (var date in timeSeriesResults.results.date_count) { // Update date counts
                    scope.dateCounts[date] = timeSeriesResults.results.date_count[date];
                }
                scope.percent = Math.floor(scope.resultsLength / scope.totalResults * 100);
                sortAndRenderTimeSeries(scope, formData, fullResults, timeSeriesResults)
            }).catch(function(response) {
                scope.timeSeries.loading = false;
            });
        }
        var sortAndRenderTimeSeries = function(scope, formData, fullResults, timeSeriesResults) {
            var allResults = progressiveLoad.mergeResults(fullResults, timeSeriesResults.results['absolute_count'], "label");
            fullResults = allResults.unsorted;
            for (var i = 0; i < allResults.sorted.length; i += 1) {
                var date = allResults.sorted[i].label;
                var value = allResults.sorted[i].count;
                scope.absoluteCounts[i] = value;
                scope.relativeCounts[i] = Math.round(value / scope.dateCounts[date] * 10000 * 100) / 100;
                if (isNaN(scope.relativeCounts[i])) {
                    scope.relativeCounts[i] = 0;
                }
            };
            scope.myBarChart.data.datasets[0].data = scope.absoluteCounts;
            scope.myBarChart.update();
            $timeout(function() {
                chartLinker(scope);
            });
            // scope.data[1] = scope.relativeCounts;
            if (scope.report === 'time_series' && angular.equals($rootScope.globalQuery, scope.localQuery)) { // are we running a different query?
                if (scope.moreResults) {
                    updateTimeSeries(scope, formData, fullResults);
                } else {
                    scope.percent = 100;
                    scope.done = true;
                    angular.element('#relative_time').removeAttr('disabled');
                    angular.element(".progress").delay(500).velocity('slideUp');
                }
            }
        }
        var tooltipBuilder = function(scope, tsType) {
            if (tsType == 'absolute_time') {
                return {
                    tooltipTemplate: function(label) {
                        var intervalEnd = parseInt(label.label) + parseInt(scope.formData.year_interval) - 1
                        var interval = label.label + "-" + intervalEnd.toString();
                        return label.value + " occurrences in " + interval;
                    }
                }
            } else {
                return {
                    tooltipTemplate: function(label) {
                        var intervalEnd = parseInt(label.label) + parseInt(scope.formData.year_interval) - 1
                        var interval = label.label + "-" + intervalEnd.toString();
                        return label.value + " occurrences per 10,000 words in " + interval;
                    }
                }
            }
        }
        var chartLinker = function(scope) {
            angular.element("#bar").off();
            angular.element("#bar").on("click touchstart", function(e) {
                var formData = angular.copy(scope.formData);
                var target = scope.myBarChart.getElementAtEvent(e);
                if (typeof(target[0]) !== 'undefined') {
                    var startDate = parseInt(target[0]._view.label);
                    var endDate = startDate + parseInt(formData.year_interval) - 1;
                    formData[philoConfig.time_series_year_field] = startDate + "-" + endDate;
                    formData.report = "concordance";
                    var urlString = "query?" + URL.objectToString(formData);
                    $location.url(urlString);
                    scope.$apply();
                }
            });
        }
        return {
            restrict: 'E',
            templateUrl: 'app/components/timeSeries/timeSeriesChart.html',
            replace: true,
            link: function(scope, element, attrs) {
                scope.height = angular.element(window).height() - angular.element('#footer').height() - angular.element('#initial_report').height() - angular.element('#header').height() - 150;
                var formData = angular.copy(scope.formData);
                var formData2 = angular.copy(scope.formData); // used only for getting total hits
                scope.q = formData.q
                scope.resultsLength = 0
                scope.frequencyType = "absolute_time";
                angular.element(".progress").show();
                request.script(formData, {
                    script: 'get_start_end_date.py'
                }).then(function(response) { // if no dates supplied or if invalid dates
                    scope.startDate = parseInt(response.data.start_date);
                    scope.endDate = parseInt(response.data.end_date);
                    scope.interval = parseInt(formData.year_interval);
                    scope.totalResults = response.data.total_results

                    // Store the current query as a local and global variable in order to make sure they are equal later on...
                    $rootScope.globalQuery = URL.mergeParams(angular.copy(formData), {
                        start_date: scope.startDate,
                        end_date: scope.endDate
                    });
                    scope.localQuery = angular.copy($rootScope.globalQuery);

                    var dateList = [];
                    var zeros = [];
                    for (var i = scope.startDate; i <= scope.endDate; i += scope.interval) {
                        dateList.push(i);
                        zeros.push(0);
                    }
                    // Initialize Chart
                    Chart.defaults.global.responsive = true;
                    Chart.defaults.global.animation.duration = 400;
                    Chart.defaults.global.tooltipCornerRadius = 0;
                    Chart.defaults.global.maintainAspectRatio = false;
                    Chart.defaults.bar.scales.xAxes[0].gridLines.display = false;
                    var chart = angular.element("#bar");
                    var font = chart.css('font-family');
                    Chart.defaults.global.fontFamily = font;
                    var backgroundColor = angular.element('.btn-primary').css('background-color');
                    scope.myBarChart = new Chart(chart, {
                        type: 'bar',
                        data: {
                            labels: dateList,
                            datasets: [{
                                label: "Absolute Frequency",
                                backgroundColor: "rgba(0, 160, 205, .6)",
                                borderColor: backgroundColor,
                                borderWidth: 1,
                                hoverBackgroundColor: "rgba(0, 160, 205, .8)",
                                hoverBorderColor: backgroundColor,
                                yAxisID: "absolute",
                                data: zeros
                            }],
                        },
                        options: {
                            legend: {
                                display: false,
                            },
                            scales: {
                                yAxes: [{
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
                                }]
                            },
                            tooltips: {
                                cornerRadius: 0,
                                callbacks: {
                                    title: function(tooltipItem) {
                                        return tooltipItem[0].xLabel + "-" + (parseInt(tooltipItem[0].xLabel) + parseInt(formData.year_interval) - 1);
                                    },
                                    label: function(tooltipItem) {
                                        if (scope.q) {
                                            if (scope.frequencyType == "absolute_time") {
                                                return tooltipItem.yLabel + " occurrences";
                                            } else {
                                                return tooltipItem.yLabel + " occurrences per 10,000 words";
                                            }
                                        } else {
                                            if (scope.frequencyType == "absolute_time") {
                                                return tooltipItem.yLabel + " documents match search parameters"
                                            } else {
                                                return tooltipItem.yLabel + " matching documents per 10,000 documents"
                                            }

                                        }
                                    }
                                }
                            }
                        }
                    });
                    scope.absoluteCounts = angular.copy(zeros);
                    scope.relativeCounts = angular.copy(zeros);
                    scope.dateCounts = {};
                    var fullResults;
                    updateTimeSeries(scope, formData, fullResults);
                });
                scope.toggleFrequency = function(type) {
                    if (type == "absolute_time") {
                        scope.myBarChart.data.datasets[0].data = scope.absoluteCounts;
                        scope.myBarChart.data.datasets[0].label = "Absolute Frequency";
                        scope.frequencyType = type;
                    } else {
                        scope.myBarChart.data.datasets[0].data = scope.relativeCounts;
                        scope.myBarChart.data.datasets[0].label = "Relative Frequency";
                        scope.frequencyType = type;
                    }
                    scope.myBarChart.update();
                }
                scope.restart = false;
                scope.$watch('restart', function() {
                    if (scope.restart) {
                        scope.timeSeries.loading = false;
                        getTimeSeries(scope);
                    }
                });
                scope.$on("$destroy", function() {
                    scope.myBarChart.destroy();
                })
            }
        }
    }
})();