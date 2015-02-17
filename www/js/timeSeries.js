"use strict";

philoApp.controller('timeSeriesCtrl', ['$scope', '$rootScope', '$http', '$location', 'radio', 'biblioCriteria', 'progressiveLoad', 'URL',
                                            function($scope, $rootScope, $http, $location, radio, biblioCriteria, progressiveLoad, URL) {
    $rootScope.formData = $location.search();
    if ($rootScope.formData.q === "" && $rootScope.report !== "bibliography") {
        $rootScope.formData.report = "bibliography";
        $location.url(URL.objectToString($rootScope.formData, true));
    }
    
    radio.setReport('time_series');
    
    $scope.$watch(function() {
        return $rootScope.formData;
        }, function() {
      $scope.biblio = biblioCriteria.build($rootScope.formData);
    }, true);
    $scope.removeMetadata = biblioCriteria.remove;
    
    $scope.percent = 0;
    $scope.interval = parseInt($rootScope.formData.year_interval);
    
    // Generate range of all dates
    var generateDateList = function(start, end) {
        var yearInterval = parseInt($rootScope.formData.year_interval);
        var startDate = normalizeDate(start, yearInterval);
        var endDate = parseInt(end);
        var dateList = []
        for (var i = startDate; i <= endDate; i += yearInterval) {
            dateList.push(i);
        }
        return dateList;
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
    
    var updateTimeSeries = function(fullResults, start, end) {
        $rootScope.formData.start = start;
        $rootScope.formData.end = end;
        var request = $scope.philoConfig.db_url + '/' + URL.query($rootScope.formData);
        $http.get(request)
        .success(function(timeSeriesResults, status, headers, config) {
            // Now that we have initial results, we can determine start and end date if not specified
            $scope.startDate = timeSeriesResults.query.date.split('-')[0];
            $scope.endDate = timeSeriesResults.query.date.split('-')[1];
            if (!$scope.resultsLength) {
                // Fetch total results now since we know the hitlist will be fully on disk
                var queryParams = angular.copy($rootScope.formData)
                queryParams.script = "get_total_results.py";
                queryParams.date = timeSeriesResults.query.date;
                $http.get($scope.philoConfig.db_url + '/' + URL.query(queryParams))
                .success(function(length, status, headers, config) {
                    $scope.resultsLength = length;
                    sortAndRenderTimeSeries(fullResults, timeSeriesResults, start, end)
                })
            } else {
                sortAndRenderTimeSeries(fullResults, timeSeriesResults, start, end)
            }
        })
        .error(function(data, status, headers, config) {
            console.log("Error", status, headers)
        });
    }
    
    var sortAndRenderTimeSeries = function(fullResults, timeSeriesResults, start, end) {
        if (end <= $scope.resultsLength) {
            $scope.percent = Math.floor(end / $scope.resultsLength * 100);
        }
        if (typeof(fullResults) === "undefined") {
            // Populate fullResults with all the dates possible in the range
            $scope.dateList = generateDateList(timeSeriesResults.query.start_date, timeSeriesResults.query.end_date);
            fullResults = {};
            for (var i = 0; i < $scope.dateList.length; i++) {
                fullResults[$scope.dateList[i]] = {count: 0, 'url': ''};
            }
        }
        var allResults = progressiveLoad.mergeResults(fullResults, timeSeriesResults.results['absolute_count'], "label");
        fullResults = allResults.unsorted;
        drawFromData(allResults.sorted, "absolute_time");
        if (end < $scope.resultsLength) {
            if (start === 0) {
                start = 1000;
            } else {
                start += 5000;
            }
            end += 5000;
            updateTimeSeries(fullResults, start, end);
        } else {
            $scope.percent = 100;
            $scope.done = true;
            $(".progress").delay(500).velocity('slideUp');
            //saveToLocalStorage($scope.sortedLists);
        }
    }
    
    var yearToTimeSpan = function(year, interval) {
        var end_date = parseInt($('#search_arguments').data('end'));
        year = String(year);
        if (interval == '10') {
            year = year.slice(0,-1) + '0';
            var next = parseInt(year) + 9;
            if (next > end_date) {
                next = String(end_date)
            } else {
                next = String(next);   
            }
            year = year + '-' + next;
        }
        else if (interval == '100') {
            year = year.slice(0,-2) + '00';
            var next = parseInt(year) + 99;
            if (next > end_date) {
                next = String(end_date)
            } else {
                next = String(next);   
            }
            year = year + '-' + next
        } else if (interval == '50') {
            var decade = parseInt(year.slice(-2));
            if (decade < 50) {
                var next = parseInt(year.slice(0,-2) + '49');
                if (next > end_date) {
                    next = String(end_date)
                } else {
                    next = String(next);   
                }
                year = year.slice(0,-2) + '00' + '-' + next;
            } else {
                var next = year.slice(0,-2) + '99';
                if (next > end_date) {
                    next = String(end_date)
                } else {
                    next = String(next);   
                }
                year = year.slice(0,-2) + '50' + '-' + next;
            }
        }
        return year
    }
    
    var drawFromData = function(data, frequency_type) {
        var barWidth = (parseInt($('#time-series').width()) - 1 * data.length) / data.length;
        var maxCount = 0;
        var margin = 0;
        for (var i in data) {
            var count = Math.round(data[i].count);
            var year = data[i].label;
            var yearDisplay = yearToTimeSpan(year, $scope.interval);
            // Test if the chart has already been drawn
            if ($('.graph-bar').length < (data.length)) {
                if (i > 0) {
                    margin += barWidth + 1;
                }
                var graphBar = "<span class='graph-bar' data-toggle='tooltip' title='" + count + " occurrences in years '" + yearDisplay + "' style='margin-left:" + margin + "px' data-count='" + Math.round(count, false) + "' data-year='" + year + "'></span>";
                $('#time-series').append(graphBar);
                $('.graph-bar').eq(i).width(barWidth + 'px');
                $('.graph-bar').eq(i).data('href', data[i].url);
                var year = '<span class="graph-years">' + year + '</span>';
                $('.graph-bar').eq(i).append(year);
                var yearWidth = (barWidth - 25) / 2;
                $('.graph-bar').eq(i).find('.graph-years').css('margin-left', yearWidth + 'px');
            } else {
                $('.graph-bar').eq(i).data('count', count);
                if (frequency_type == "absolute_time") {
                    $('.graph-bar').eq(i).attr('title', Math.round(count, false) + ' occurrences<br>between ' + yearDisplay);
                } else {
                    $('.graph-bar').eq(i).attr('title', Math.round(count, false) + ' occurrences per 1,000,000 words<br>between ' + yearDisplay);
                }  
            }
            if (count > maxCount) {
                maxCount = count;
            }
        }
        
        // Make sure the years don't overlap
        if (barWidth > 12) {
            $('.graph-years').show();
            if (barWidth < 18) {
                $('.graph-years').css('font-size', '70%');
            }
        } else {
            var count = 0;
            $('.graph-years').eq(0).show();
            var num = parseInt($('.graph-years').length / 10);
            $('.graph-years').each(function() {
                count += 1;
                if (count == num) {
                    $(this).show();
                    count = 0;
                }
            });
        }
        
        var chart_height = $('#time-series').height();
        var multiplier = (chart_height - 10) / maxCount; 
        var max_height = 0;
        
        var delay_anim = 0
        $('.graph-bar').each(function() {
            var count = $(this).data('count');
            var height = count * multiplier;
            delay_anim += 20;
            if (height > max_height) {
                max_height = height;
            }
            $(this).eq(0).velocity({'height': height + 'px'}, {delay: delay_anim, duration: 250, easing: "easeOutQuad"});
        });
        
        var top_line = (chart_height - 10) / chart_height * 100;
        $("#top-division").css('bottom', top_line + '%');
        
        // Draw three lines along the X axis to help visualize frequencies
        var topNumber = Math.round(maxCount);
        var middleNumber = Math.round(maxCount / 3 * 2);
        var bottomNumber = Math.round(maxCount / 3);
        if (frequency_type == "relative_time") {
            $('#side-text').html('Occurrences per 1,000,000 words'); // TODO: move to translation file
            $('#top-number').html(topNumber + ' occurrences per 1,000,000 words');
            $('#middle-number').html(middleNumber + ' occurrences per 1,000,000 words');
            $('#first-number').html(bottomNumber + ' occurrences per 1,000,000 words');
        } else {
            $('#side-text').html('Total occurrences'); // TODO: move to translation file
            $('#top-number').html(topNumber + ' occurrences');
            $('#middle-number').html(middleNumber + ' occurrences');
            $('#first-number').html(bottomNumber + ' occurrences');
        }
        //clickOnChart(interval);
    }
    
    
    if (sessionStorage[$location.url()] == null || webConfig.debug == true) {
        
        // Calculate width and height of chart
        var height = $(window).height() - $('#footer').height() - $('#initial_report').height() - $('#header').height() - 190;
        $('#time-series').css('height', height);
        var bodyWidth = parseInt($('body').width());
        $('#time-series, #first-division, #middle-division, #top-division').width(bodyWidth-90 + 'px');        
        
        $scope.resultsLength = false; // set to false for now
        $(".progress").show();
        
        var fullResults;
        var absoluteFrequency;
        var dateCounts;
        
        updateTimeSeries(fullResults, 0, 1000, absoluteFrequency, dateCounts)
    } else {
        var time_series = JSON.parse(sessionStorage[window.location.href]);
        var date_counts = time_series['date_counts'];
        var abs_results = sortResults(time_series['abs_results']);
        var total = $("#time-series-length").html(total);
        $('#relative_counts').data('value', relativeCount(abs_results, date_counts))
        drawFromData(abs_sorted_list, interval, "absolute_time");
    }
    
}]);