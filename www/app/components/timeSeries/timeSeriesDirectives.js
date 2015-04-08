"use strict";

philoApp.directive('timeSeriesChart', ['$rootScope', '$http', '$location', 'progressiveLoad', 'URL', 'request', 'saveToLocalStorage',
                                       function($rootScope, $http, $location, progressiveLoad, URL, request, save) {
    var getTimeSeries = function(scope) {
        var formData = angular.copy(scope.formData);
        scope.resultsLength = false; // set to false for now
        $(".progress").show();
        var fullResults;
        var absoluteFrequency;
        scope.dateCounts = {};
        request.script({script: 'get_start_end_date.py'}).then(function(dates) { // always run even if useless since so fast
            scope.startDate = formData.start_date || dates.data.start_date;
            scope.endDate = formData.end_date || dates.data.end_date;
            scope.interval = formData.year_interval;
            
            // Store the current query as a local and global variable in order to make sure they are equal later on...
            $rootScope.globalQuery = URL.mergeParams(angular.copy(formData), {start_date: scope.startDate, end_date: scope.endDate});
            scope.localQuery = angular.copy($rootScope.globalQuery);
            
            scope.barChart = [];
            var barChartObject = initializeBarChart(scope.startDate, scope.endDate, formData.year_interval);
            scope.barChart = barChartObject.dateList;
            scope.chartIndex = barChartObject.chartIndex;
            updateTimeSeries(scope, formData, fullResults, 0, 1000);
        });
    }
    // Generate bars in chart by iterating over all date ranges
    var initializeBarChart = function(start, end, yearInterval) {
        yearInterval = parseInt(yearInterval);
        var startDate = normalizeDate(start, yearInterval);
        var endDate = parseInt(end);
        var dateList = [];
        var dataLength = Math.floor((endDate - startDate) / yearInterval) + 1;
        var remainder = (endDate - startDate) % yearInterval;
        if (remainder > 0) {
            dataLength += 1;
        }
        var barWidth = (parseInt($('#time-series').width()) - dataLength) / dataLength; // Something is off here...
        var margin = 0;
        var chartIndex = {};
        var position = 0;
        for (var i = startDate; i <= endDate; i += yearInterval) {
            if (i !== startDate) {
                margin += barWidth + 1;
            }
            var yearWidth = (barWidth - 25) / 2;
            dateList.push({
                date: i,
                barStyle: {
                    'margin-left': margin + 'px',
                    width: barWidth + 'px'
                },
                dateStyle: {
                    width: yearWidth + 'px'
                },
                width: barWidth, // Keep this for the filter to decide whether to skip a year on display
                title: '',
                url: ''
            });
            chartIndex[i.toString()] = position;
            position ++;
        }
        return {dateList: dateList, chartIndex: chartIndex};
    }
    var updateTimeSeries = function(scope, formData, fullResults, start, end) {
        request.report(formData, {start: start, end: end}).then(function(results) {
            scope.timeSeries.loading = false;
            var timeSeriesResults = results.data;
            scope.resultsLength = timeSeriesResults.results_length;
            scope.timeSeries.resultsLength = scope.resultsLength;
            scope.moreResults = timeSeriesResults.more_results;
            for (var date in timeSeriesResults.results.date_count) { // Update date counts
                scope.dateCounts[date] = timeSeriesResults.results.date_count[date];
            }
            sortAndRenderTimeSeries(scope, formData, fullResults, timeSeriesResults, start, end)
        });
    }
    var sortAndRenderTimeSeries = function(scope, formData, fullResults, timeSeriesResults, start, end) {
        if (end <= scope.resultsLength) {
            scope.percent = Math.floor(end / scope.resultsLength * 100);
        }
        var allResults = progressiveLoad.mergeResults(fullResults, timeSeriesResults.results['absolute_count'], "label");
        fullResults = allResults.unsorted;
        scope.absoluteCounts = allResults.sorted;
        if (scope.report === 'time_series' && angular.equals($rootScope.globalQuery, scope.localQuery)) { // are we running a different query?
            drawFromData(scope, allResults.sorted, "absolute_time");
            if (scope.moreResults) {
                if (start === 0) {
                    start = 1000;
                } else {
                    start += 10000;
                }
                end += 10000;
                updateTimeSeries(scope, formData, fullResults, start, end);
            } else {
                scope.percent = 100;
                scope.done = true;
                scope.relativeCounts = relativeCount(allResults.sorted, scope.dateCounts);
                $('#relative_time').removeAttr('disabled');
                $(".progress").delay(500).velocity('slideUp');
                var objectToSave = {
                    barChart: scope.barChart,
                    absoluteCounts: scope.absoluteCounts,
                    relativeCounts: scope.relativeCounts,
                    resultsLength: scope.resultsLength,
                    startDate: scope.startDate,
                    endDate: scope.endDate
                }
                //save(objectToSave); This isn't quite working correctly.
            }
        }
    }
    var drawFromData = function(scope, data, frequencyType) {
        var maxCount = Math.max.apply(Math,data.map(function(object){return Math.round(object.count);}));
        var chartHeight = $('#time-series').height();
        var multiplier = (chartHeight - 10) / maxCount;
        for (var i=0; i < data.length; i++) {
            var chartIndex = scope.chartIndex[data[i].label];
            var count = Math.round(data[i].count);
            var pixelHeight = count * multiplier;
            $('.graph-bar').eq(chartIndex).data('height', pixelHeight);
            if (scope.barChart[chartIndex].url === '' && data[i].url !== '') {
                scope.barChart[chartIndex].url = data[i].url;
            }
            var year = data[i].label;
            var yearDisplay = yearToTimeSpan(year, scope.interval, scope.endDate);
            if (frequencyType === 'absolute_time') {
                scope.barChart[chartIndex].title = Math.round(count, false) + ' occurrences between ' + yearDisplay;
            } else {
                scope.barChart[chartIndex].title = Math.round(count, false) + ' occurrences per 1,000,000 words between ' + yearDisplay;
            }
        }

        $('.graph-bar').velocity({'height': function() {return $(this).data('height')}}, {duration: 250, easing: "easeOutQuad", stagger: 15}); // stagger doesn't work
        
        // Draw three lines along the X axis to help visualize frequencies
        var top_line = (chartHeight - 10) / chartHeight * 100;
        $("#top-division").css('bottom', top_line + '%');
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
    var normalizeDate = function(year, interval) {
        year = year.toString();
        if (interval === 10) {
            year = year.slice(0,-1) + '0';
        } else if (interval === 100) {
            year = year.slice(0,-2) + '00';
        } else if (interval === 50) {
            var decade = parseInt(year.slice(-2));
            if (decade < 50) {
                year = year.slice(0,-2) + '00';
            } else {
                year = year.slice(0,-2) + '50';
            }
        }
        return parseInt(year)
    }    
    var yearToTimeSpan = function(year, interval, endDate) {
        year = String(year);
        if (interval == '10') {
            year = year.slice(0,-1) + '0';
            var next = parseInt(year) + 9;
            if (next > endDate) {
                next = String(endDate)
            } else {
                next = String(next);   
            }
            year = year + '-' + next;
        }
        else if (interval == '100') {
            year = year.slice(0,-2) + '00';
            var next = parseInt(year) + 99;
            if (next > endDate) {
                next = String(endDate)
            } else {
                next = String(next);   
            }
            year = year + '-' + next
        } else if (interval == '50') {
            var decade = parseInt(year.slice(-2));
            if (decade < 50) {
                var next = parseInt(year.slice(0,-2) + '49');
                if (next > endDate) {
                    next = String(endDate)
                } else {
                    next = String(next);   
                }
                year = year.slice(0,-2) + '00' + '-' + next;
            } else {
                var next = year.slice(0,-2) + '99';
                if (next > endDate) {
                    next = String(endDate)
                } else {
                    next = String(next);   
                }
                year = year.slice(0,-2) + '50' + '-' + next;
            }
        }
        return year
    }
    var relativeCount = function(absoluteCounts, dateCounts) {
        var relativeCounts = [];
        for (var i=0; i < absoluteCounts.length; i++) {
            var absoluteObject = angular.copy(absoluteCounts[i]);
            absoluteObject.count = absoluteObject.count / dateCounts[absoluteObject.label] * 1000000;
            relativeCounts.push(absoluteObject);
        }
        return relativeCounts
    }
    var retrieveFromStorage = function(scope) {
        var results = JSON.parse(sessionStorage[$location.url()]);
        for (var k in results) scope[k] = results[k];
        scope.percent = 100;
        setTimeout(function() {
            drawFromData(scope, scope.absoluteCounts, "absolute_time");
        }, 500)
    }
    return {
        restrict: 'E',
        templateUrl: 'app/components/timeSeries/timeSeriesChart.html',
        replace: true,
        link: function(scope, element, attrs) {
            var height = $(window).height() - $('#footer').height() - $('#initial_report').height() - $('#header').height() - 190;
            var width = parseInt($('body').width()) - 90;
            scope.chartSize = {
                height: height + 'px',
                width: width + 'px'
                };
            scope.divisionWidth = {width: width + 'px'};
            if (typeof(sessionStorage[$location.url()]) === 'undefined' || $rootScope.philoConfig.production === false) {
                getTimeSeries(scope);
            } else {
                retrieveFromStorage(scope);
            }
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
}]);