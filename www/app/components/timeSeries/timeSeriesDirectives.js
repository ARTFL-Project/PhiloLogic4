(function() {
    "use strict";

    angular
        .module('philoApp')
        .directive('timeSeriesChart', timeSeriesChart);

    function timeSeriesChart($rootScope, $http, $location, $log, philoConfig, progressiveLoad, URL, request, saveToLocalStorage) {
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
                scope.startDate = parseInt(dates.data.start_date);
                scope.endDate = parseInt(dates.data.end_date);
                scope.interval = parseInt(formData.year_interval);

                // Store the current query as a local and global variable in order to make sure they are equal later on...
                $rootScope.globalQuery = URL.mergeParams(angular.copy(formData), {
                    start_date: scope.startDate,
                    end_date: scope.endDate
                });
                scope.localQuery = angular.copy($rootScope.globalQuery);

                scope.dateList = [];
                var zeros = [];
                for (var i = scope.startDate; i <= scope.endDate; i += scope.interval) {
                    scope.dateList.push(i);
                    zeros.push(0);
                }
                scope.absoluteCounts = angular.copy(zeros);
                scope.relativeCounts = angular.copy(zeros);
                updateTimeSeries(scope, formData, fullResults);
            });
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
            var allResults = progressiveLoad.mergeResults(fullResults, timeSeriesResults.results['absolute_count'], "label");
            fullResults = allResults.unsorted;
            for (var i=0; i < allResults.sorted.length; i+=1) {
                var date = allResults.sorted[i].label;
                var value = allResults.sorted[i].count;
                scope.absoluteCounts[i] = value;
                scope.relativeCounts[i] = Math.round(value / scope.dateCounts[date] * 10000);
                if (isNaN(scope.relativeCounts[i])) {
                    scope.relativeCounts[i] = 0;
                }
            };
            // var maxValueAbsolute = Math.max.apply(Math, scope.absoluteCounts);
            // var maxValueRelative = Math.max.apply(Math, scope.relativeCounts);
            // scope.divider = maxValueRelative / maxValueAbsolute;
            // scope.relativeCounts = scope.relativeCounts.map(function(count) {
            //     return count / scope.divider;
            // });
            scope.data[0] = scope.absoluteCounts;
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
                        return label.value + " occurrences in " + interval ;
                    }
                }
            } else {
                return {
                    tooltipTemplate: function(label) {
                        var intervalEnd = parseInt(label.label) + parseInt(scope.formData.year_interval) - 1
                        var interval = label.label + "-" + intervalEnd.toString();
                        return label.value + " occurrences per 10,000 words in " + interval ;
                    }
                }
            }
        }
        return {
            restrict: 'E',
            templateUrl: 'app/components/timeSeries/timeSeriesChart.html',
            replace: true,
            link: function(scope, element, attrs) {
                scope.height = angular.element(window).height() - angular.element('#footer').height() - angular.element('#initial_report').height() - angular.element('#header').height() - 70;
                Chart.defaults.global.tooltipCornerRadius = 0;
                Chart.defaults.global.maintainAspectRatio = false;
                Chart.defaults.Bar.scaleGridLineColor = "rgba(240, 240, 240,.5)";
                Chart.defaults.Bar.barShowStroke = false;
                Chart.defaults.Bar.barValueSpacing = 4;
                scope.chart_options = tooltipBuilder(scope, "absolute_time");
                scope.series = ["Absolute Count"];
                scope.absoluteCounts = [];
                scope.relativeCounts = [];
                scope.data = [[]];
                scope.frequencyType = "absolute_time";
                getTimeSeries(scope);
                attrs.$observe('frequencyType', function(frequencyType) {
                    scope.frequencyType = frequencyType;
                    if (typeof(scope.absoluteCounts) !== 'undefined') {
                        scope.chart_options = tooltipBuilder(scope, frequencyType);
                        if (frequencyType === 'relative_time') {
                            scope.data[0] = scope.relativeCounts;
                        } else {
                            scope.data[0] = scope.absoluteCounts;
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
                scope.goToConcordance = function(p, e) {
                    var formData = angular.copy(scope.formData);
                    var startDate  = parseInt(p[0].label);
                    var endDate = startDate + parseInt(formData.year_interval) - 1;
                    formData[philoConfig.time_series_year_field] = startDate + "-" + endDate;
                    formData.report = "concordance";
                    var urlString = "query?" + URL.objectToString(formData);
                    $location.url(urlString);
                }
            }
        }
    }
})();
