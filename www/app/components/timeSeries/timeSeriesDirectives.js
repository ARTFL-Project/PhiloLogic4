(function() {
    "use strict";

    angular
        .module('philoApp')
        .directive('timeSeriesChart', timeSeriesChart);

    function timeSeriesChart($rootScope, $http, $location, progressiveLoad, URL, request, saveToLocalStorage) {
        var getTimeSeries = function(scope) {
                var formData = angular.copy(scope.formData);
                scope.resultsLength = 0;
                angular.element(".progress").show();
                var fullResults;
                var absoluteFrequency;
                scope.dateCounts = {};
                request.script(formData, {
                    script: 'get_start_end_date.py'
                }).then(function(dates) { // if no dates supplied or if invalid dates
                    scope.startDate = dates.data.start_date;
                    scope.endDate = dates.data.end_date;
                    scope.interval = formData.year_interval;

                    // Store the current query as a local and global variable in order to make sure they are equal later on...
                    $rootScope.globalQuery = URL.mergeParams(angular.copy(formData), {
                        start_date: scope.startDate,
                        end_date: scope.endDate
                    });
                    scope.localQuery = angular.copy($rootScope.globalQuery);

                    scope.barChart = [];
                    var barChartObject = initializeBarChart(scope.startDate, scope.endDate, formData.year_interval);
                    scope.barChart = barChartObject.dateList;
                    scope.chartIndex = barChartObject.chartIndex;
                    updateTimeSeries(scope, formData, fullResults);
                });
            }
            // Generate bars in chart by iterating over all date ranges
        var initializeBarChart = function(start, end, yearInterval) {
            yearInterval = parseInt(yearInterval);
            var startDate = parseInt(start);
            var endDate = parseInt(end);
            var dateList = [];
            var dataLength = Math.floor((endDate - startDate) / yearInterval);
            var remainder = (endDate - startDate) % yearInterval;
            if (remainder > 0) {
                dataLength += 1;
            }
            var barWidth = Math.floor(parseInt(angular.element('#time-series').width()) / dataLength - 1);
            var margin = 0;
            var chartIndex = {};
            var position = 0;
            for (var i = startDate; i <= endDate; i += yearInterval) {
                if (i !== startDate) {
                    margin += barWidth + 1;
                }
                dateList.push({
                    date: i,
                    barStyle: {
                        'margin-left': margin + 'px',
                        width: barWidth + 'px'
                    },
                    width: barWidth, // Keep this for the filter to decide whether to skip a year on display
                    title: '',
                    url: ''
                });
                chartIndex[i.toString()] = position;
                position++;
            }
            return {
                dateList: dateList,
                chartIndex: chartIndex
            };
        }
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
                sortAndRenderTimeSeries(scope, formData, fullResults, timeSeriesResults)
            }).catch(function(response) {
                scope.timeSeries.loading = false;
            });
        }
        var sortAndRenderTimeSeries = function(scope, formData, fullResults, timeSeriesResults) {
            //console.log(scope.barChart[scope.barChart.length])
            if (scope.startDate <= scope.barChart[scope.barChart.length - 1].date) {
                var index = scope.chartIndex[scope.startDate.toString()];
                scope.percent = Math.floor(index / scope.barChart.length * 100);
            }
            var allResults = progressiveLoad.mergeResults(fullResults, timeSeriesResults.results['absolute_count'], "label");
            fullResults = allResults.unsorted;
            scope.absoluteCounts = allResults.sorted;
            if (scope.report === 'time_series' && angular.equals($rootScope.globalQuery, scope.localQuery)) { // are we running a different query?
                drawFromData(scope, allResults.sorted, "absolute_time");
                if (scope.moreResults) {
                    updateTimeSeries(scope, formData, fullResults);
                } else {
                    scope.percent = 100;
                    scope.done = true;
                    scope.relativeCounts = relativeCount(allResults.sorted, scope.dateCounts);
                    angular.element('#relative_time').removeAttr('disabled');
                    angular.element(".progress").delay(500).velocity('slideUp');
                    var objectToSave = {
                        barChart: scope.barChart,
                        absoluteCounts: scope.absoluteCounts,
                        relativeCounts: scope.relativeCounts,
                        resultsLength: scope.resultsLength,
                        startDate: scope.startDate,
                        endDate: scope.endDate
                    }
                }
            }
        }
        var drawFromData = function(scope, data, frequencyType) {
            var maxCount = Math.max.apply(Math, data.map(function(object) {
                return Math.round(object.count);
            }));
            var chartHeight = angular.element('#time-series').height();
            var multiplier = (chartHeight - 10) / maxCount;
            for (var i = 0; i < data.length; i++) {
                var chartIndex = scope.chartIndex[data[i].label];
                var count = Math.round(data[i].count);
                var pixelHeight = count * multiplier;
                angular.element('.graph-bar').eq(chartIndex).data('height', pixelHeight);
                if (scope.barChart[chartIndex].url === '' && data[i].url !== '') {
                    scope.barChart[chartIndex].url = data[i].url;
                }
                var year = data[i].label;
                var yearDisplay = year + '-' + (parseInt(year) + parseInt(scope.interval) - 1); //yearToTimeSpan(year, scope.interval, scope.endDate);
                if (frequencyType === 'absolute_time') {
                    scope.barChart[chartIndex].title = Math.round(count, false) + ' occurrences between ' + yearDisplay;
                } else {
                    scope.barChart[chartIndex].title = Math.round(count, false) + ' occurrences per 1,000,000 words between ' + yearDisplay;
                }
            }

            angular.element('.graph-bar').velocity({
                'height': function() {
                    return angular.element(this).data('height')
                }
            }, {
                duration: 250,
                easing: "easeOutQuad",
                stagger: 15
            }); // stagger doesn't work

            // Draw three lines along the X axis to help visualize frequencies
            var top_line = (chartHeight - 10) / chartHeight * 100;
            angular.element("#top-division").css('bottom', top_line + '%');
            var topNumber = Math.round(maxCount);
            var middleNumber = Math.round(maxCount / 3 * 2);
            var bottomNumber = Math.round(maxCount / 3);
            if (frequencyType == "relative_time") {
                scope.sideText = 'Occurrences per 1,000,000 words';
                scope.topNumber = topNumber + ' occurrences per 1,000,000 words';
                scope.middleNumber = middleNumber + ' occurrences per 1,000,000 words';
                scope.bottomNumber = bottomNumber + ' occurrences per 1,000,000 words';
            } else {
                scope.sideText = 'Total occurrences';
                scope.topNumber = topNumber + ' occurrences';
                scope.middleNumber = middleNumber + ' occurrences';
                scope.bottomNumber = bottomNumber + ' occurrences';
            }
        }
        var relativeCount = function(absoluteCounts, dateCounts) {
            var relativeCounts = [];
            for (var i = 0; i < absoluteCounts.length; i++) {
                var absoluteObject = angular.copy(absoluteCounts[i]);
                absoluteObject.count = absoluteObject.count / dateCounts[absoluteObject.label] * 1000000;
                if (isNaN(absoluteObject.count)) {
                    absoluteObject.count = 0;
                }
                relativeCounts.push(absoluteObject);
            }
            return relativeCounts;
        }
        return {
            restrict: 'E',
            templateUrl: 'app/components/timeSeries/timeSeriesChart.html',
            replace: true,
            link: function(scope, element, attrs) {
                var height = angular.element(window).height() - angular.element('#footer').height() - angular.element('#initial_report').height() - angular.element('#header').height() - 190;
                var width = parseInt(angular.element('body').width()) - 60;
                scope.chartSize = {
                    height: height + 'px',
                    width: width + 'px'
                };
                scope.divisionWidth = {
                    width: width + 'px'
                };
                getTimeSeries(scope);
                attrs.$observe('frequencyType', function(frequencyType) {
                    if (typeof(scope.absoluteCounts) !== 'undefined') {
                        if (frequencyType === 'relative_time') {
                            drawFromData(scope, scope.relativeCounts, frequencyType);
                        } else {
                            drawFromData(scope, scope.absoluteCounts, frequencyType);
                        }
                    }
                });
                scope.restart = false;
                scope.$watch('restart', function() {
                    if (scope.restart) {
                        scope.timeSeries.loading = false;
                        getTimeSeries(scope);
                    }
                });
            }
        }
    }
})();
