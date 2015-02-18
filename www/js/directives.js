philoApp.directive('loading', function() {
    return {
        restrict: 'E',
        template: '<div class="spinner"><div class="bounce1"></div><div class="bounce2"></div><div class="bounce3"></div></div>'
    }
});

philoApp.directive('progressBar', function() {
    return {
        restrict: 'E',
        template: '<div class="progress"><div class="progress-bar" role="progressbar" aria-valuenow="20" aria-valuemin="0" aria-valuemax="100" style="width: 0%;"></div></div>',
        link: function(scope, element, attrs) {
            attrs.$observe('progress', function(percent){
                var progressElement = $(element).find('.progress-bar');
                progressElement.velocity({'width': percent.toString() + '%'}, {
                    queue: false,
                    complete: function() {
                        progressElement.text(percent.toString() + '%');
                        if (percent == 100) {
                            progressElement.delay(500).velocity('slideUp');
                        }
                    }
                }); 
            });     
        }
    }
});

philoApp.directive('pages', ['$rootScope', function($rootScope) {
    var buildPages = function() {
        var start = $rootScope.results.description.start;
        var resultsPerPage = parseInt($rootScope.formData.results_per_page);
        var resultsLength = $rootScope.results.results_length;
    
        // first find out what page we are on currently.    
        var currentPage = Math.floor(start / resultsPerPage) + 1 || 1;
        
        // then how many total pages the query has    
        var totalPages = Math.floor(resultsLength / resultsPerPage);
        var remainder = resultsLength % resultsPerPage;
        if (remainder !== 0) {
            totalPages += 1;
        }
        totalPages = totalPages || 1;
        
        // construct the list of page numbers we will output.
        var pages = []
        // up to four previous pages
        var prev = currentPage - 4;
        while (prev < currentPage) {
            if (prev > 0) {
                pages.push(prev);
            }
            prev += 1;
        }
        // the current page
        pages.push(currentPage);
        // up to five following pages
        var next = currentPage + 5;
        while (next > currentPage) {
            if (next < totalPages) {
                pages.push(next);
            }
            next -= 1;
        }
        // first and last if not already there
        if (pages[0] !== 1) {
            pages.unshift(1);
        }
        if (pages[-1] !== totalPages) {
            pages.push(totalPages);
        }
        var uniquePages = [];
        $.each(pages, function(i, el){
            if($.inArray(el, uniquePages) === -1) uniquePages.push(el);
        });
        var pages = uniquePages.sort(function (a, b) { 
            return a - b;
        });
        
        // now we construct the actual links from the page numbers
        var pageObject = [];
        for (var i=0; i < pages.length; i++) {
            var page = pages[i];
            var pageStart = page * resultsPerPage - resultsPerPage + 1;
            var pageEnd = page * resultsPerPage;
            if (page === currentPage) {
                var active = "active";
            } else {
                var active = "";
            }
            var pageStart = resultsPerPage * (page - 1) + 1;
            var pageEnd = pageStart + resultsPerPage - 1;
            if (pageEnd > resultsLength) {
                pageEnd = resultsLength;
            }
            if (page === 1 && !2 in pages) {
                page = "First";
            }
            if (page === totalPages) {
                page = "Last";
            }
            pageObject.push({display: page, start: pageStart, end: pageEnd, active: active});
        }
        return pageObject;
    }
    return {
        restrict: 'E',
        template: '<div id="page_links" class="btn-group">' +
                  '<a id="current_results_page" class="btn btn-default btn-lg {{ page.active }}" ng-repeat="page in pages" ng-click="goToPage(page.start, page.end)">{{ page.display }}</a>' +
                  '</div>',
        link: function(scope, element, attrs) {
                scope.$watch(function() {
                    return $rootScope.results;
                    }, function() {
                    scope.pages = buildPages();
                }, true);
        }
    }
}]);

philoApp.directive('searchArguments', ['$rootScope','$http', '$location', 'URL', function($rootScope, $http, $location, URL) {
    var getSearchArgs = function(queryParams) {
        var queryArgs = {};
        if ('q' in queryParams) {
            queryArgs.queryTerm = queryParams.q;
        } else {
            queryArgs.queryTerm = '';  
        }
        queryArgs.biblio = buildCriteria(queryParams);
        return queryArgs;
    }
    var buildCriteria = function(queryParams) {
        var queryArgs = angular.copy(queryParams);
        var biblio = []
        if (queryArgs.report === "time_series") {
            delete queryParams.date;
        }
        var config = $rootScope.philoConfig;
        for (var i=0; i < config.metadata.length; i++) {
            var k = config.metadata[i];
            var v = queryArgs[k];
            var alias = k;
            if (v) {
                if (k in config.metadata_aliases) {
                    alias = config.metadata_aliases[k];
                }
                biblio.push({key: k, alias: alias, value: v});
            }
        }
        return biblio
    }
    var removeMetadata = function(metadata, queryParams) {
        delete queryParams[metadata];
        var request = $rootScope.philoConfig.db_url + '/' + URL.query(queryParams);
        if (queryParams.report === "concordance" || queryParams.report === "kwic" || queryParams.report === "bibliography") {
            $http.get(request).success(function(data) {
                $rootScope.results = data;
                $location.url(URL.objectToString(queryParams, true));
            })
        } else if (queryParams.report === "collocation") {
            $('#collocate_counts').empty();
        }
    }
    return {
        restrict: 'E',
        templateUrl: 'templates/searchArguments.html',
        link: function(scope, element, attrs) {
                scope.$watch(function() {
                    return $location.search();
                    }, function() {
                    scope.queryArgs = getSearchArgs($location.search());
                    scope.queryArgs.report = $location.search().report;
                }, true);
                scope.formData = $rootScope.formData;
                scope.removeMetadata = removeMetadata;
        } 
    }
}]);

philoApp.directive('collocationCloud', ['defaultDiacriticsRemovalMap', function(defaultDiacriticsRemovalMap) {
    var buildCloud = function(sortedList) {
        var cloudList = angular.copy(sortedList);
        $.fn.tagcloud.defaults = {
            size: {start: 1.0, end: 3.5, unit: 'em'},
            color: {start: '#C4DFF3', end: '#286895'}
          };
        $('#collocate_counts').hide().empty();
        var removeDiacritics = function(str) {
            var changes = defaultDiacriticsRemovalMap.map;
            for(var i=0; i<changes.length; i++) {
                str = str.replace(changes[i].letters, changes[i].base);
            }
            return str;
        }
        cloudList.sort(function(a,b) {
            var x = removeDiacritics(a.label);
            var y = removeDiacritics(b.label);
            return x < y ? -1 : x > y ? 1 : 0;
        });
        var html = ''
        for (var i in cloudList) {
            var word = cloudList[i].label;
            var count = cloudList[i].count;
            var href = cloudList[i].url;
            var searchLink = '<span class="cloud_term" rel="' + count + '" data-href="' + href + '&collocate_num=' + count + '">';
            html += searchLink + word + ' </span>';
        }
        $("#collocate_counts").html(html);
        $("#collocate_counts span").tagcloud();
        $("#collocate_counts").velocity('fadeIn');
    }
    return {
        restrict: 'E',
        template: '<div id="word_cloud" class="word_cloud">' +
                  '<div id="collocate_counts" class="collocation_counts">{{ cloud }}</div></div>',
        link: function(scope, element, attrs) {
                scope.$watch('sortedLists', function() {
                    if (!$.isEmptyObject(scope.sortedLists)) {
                        scope.cloud = buildCloud(scope.sortedLists.all);
                    }
                });
        }
        
    }
}]);

philoApp.directive('collocationTable', ['$rootScope', '$http', '$location', 'URL', 'progressiveLoad',  function($rootScope, $http, $location, URL, progressiveLoad) {
    var activateLinks= function() {
        // Activate links on collocations
        $('span[id^=all_word], span[id^=left_word], span[id^=right_word]').addClass('colloc_link');
        var href = window.location.href;
        $('.colloc_link, .cloud_term').click(function(e) {
            e.preventDefault();
            window.location = $(this).data('href');
        });
    }
    var updateCollocation = function(scope, fullResults, resultsLength, start, end) {
        $rootScope.formData.start = start;
        $rootScope.formData.end = end;
        var request = scope.philoConfig.db_url + '/' + URL.query($rootScope.formData);
        var collocation = this;
        $http.get(request)
        .success(function(data, status, headers, config) {
            if (!resultsLength) {
                // Fetch total results now since we know the hitlist will be fully on disk
                var queryParams = angular.copy($rootScope.formData)
                queryParams.script = "get_total_results.py";
                queryParams.report = "concordance"
                $http.get($rootScope.philoConfig.db_url + '/' + URL.query(queryParams))
                .success(function(length, status, headers, config) {
                    scope.resultsLength = length;
                    sortAndRenderCollocation(scope, fullResults, data, length, start, end)
                })
            } else {
                sortAndRenderCollocation(scope, fullResults, data, resultsLength, start, end)
            }
        })
        .error(function(data, status, headers, config) {
            console.log("Error", status, headers)
        });
    }
    var sortAndRenderCollocation = function(scope, fullResults, data, resultsLength, start, end) {
        if (end <= resultsLength) {
            scope.percent = Math.floor(end / resultsLength * 100);
        }
        if (typeof(fullResults) === "undefined") {
            fullResults = {"all_collocates": {}, 'left_collocates': {}, 'right_collocates': {}}
        }
        var all = progressiveLoad.mergeResults(fullResults["all_collocates"], data["all_collocates"]);
        var left = progressiveLoad.mergeResults(fullResults["left_collocates"], data['left_collocates']);
        var right = progressiveLoad.mergeResults(fullResults["right_collocates"], data['right_collocates']);
        scope.sortedLists = {
            'all': all.sorted.slice(0, 100),
            'left': left.sorted.slice(0, 100),
            'right': right.sorted.slice(0, 100)
            };
        if (typeof(start) === "undefined" || end < resultsLength) {
            var tempFullResults = {"all_collocates": all.unsorted, "left_collocates": left.unsorted, "right_collocates": right.unsorted};
            if (start === 0) {
                start = 1000;
            } else {
                start += 5000;
            }
            end += 5000;
            updateCollocation(scope, tempFullResults, resultsLength, start, end);
        } else {
            scope.percent = 100;
            scope.filterList = data.filter_list;
            scope.done = true;
            activateLinks();
            progressiveLoad.saveToLocalStorage({results: scope.sortedLists, resultsLength: scope.resultsLength, filterList: scope.filterList});
        }
    }
    var getCollocations = function(scope) {
        $('#philologic_collocation').velocity('fadeIn', {duration: 200});
        $(".progress").show();
        var collocObject;
        updateCollocation(scope, collocObject, false, 0, 1000);
    }
    var retrieveFromStorage = function(scope) {
        var savedObject = JSON.parse(sessionStorage[$location.url()]);
        scope.sortedLists = savedObject.results;
        scope.resultsLength = savedObject.resultsLength;
        scope.filterList = savedObject.filterList;
        collocation.activateLinks();
        scope.percent = 100;
        scope.done = true;
        $('#philologic_collocation').velocity('fadeIn', {duration: 200});
    }
    return {
        restrict: 'E',
        templateUrl: 'templates/collocationTable.html',
        link: function(scope, element, attrs) {
                if (sessionStorage[$location.url()] == null || $rootScope.philoConfig.debug === false) {
                    getCollocations(scope);
                } else {
                    retrieveFromStorage(scope);
                }
            }
    }
}]);

philoApp.directive('timeSeriesChart', ['$rootScope', '$http', '$location', 'radio', 'progressiveLoad', 'URL',
                    function($rootScope, $http, $location, radio, progressiveLoad, URL) {
    var updateTimeSeries = function(scope, fullResults, start, end) {
        $rootScope.formData.start = start;
        $rootScope.formData.end = end;
        var request = scope.philoConfig.db_url + '/' + URL.query($rootScope.formData);
        $http.get(request)
        .success(function(timeSeriesResults, status, headers, config) {
            // Now that we have initial results, we can determine start and end date if not specified
            scope.startDate = timeSeriesResults.query.date.split('-')[0];
            scope.endDate = timeSeriesResults.query.date.split('-')[1];
            if (!scope.resultsLength) {
                // Fetch total results now since we know the hitlist will be fully on disk
                var queryParams = angular.copy($rootScope.formData)
                queryParams.script = "get_total_results.py";
                queryParams.date = timeSeriesResults.query.date;
                $http.get(scope.philoConfig.db_url + '/' + URL.query(queryParams))
                .success(function(length, status, headers, config) {
                    scope.resultsLength = length;
                    sortAndRenderTimeSeries(scope, fullResults, timeSeriesResults, start, end)
                })
            } else {
                sortAndRenderTimeSeries(scope, fullResults, timeSeriesResults, start, end)
            }
        })
        .error(function(data, status, headers, config) {
            console.log("Error", status, headers)
        });
    }
    
    var sortAndRenderTimeSeries = function(scope, fullResults, timeSeriesResults, start, end) {
        if (end <= scope.resultsLength) {
            scope.percent = Math.floor(end / scope.resultsLength * 100);
        }
        if (typeof(fullResults) === "undefined") {
            // Populate fullResults with all the dates possible in the range
            scope.dateList = generateDateList(timeSeriesResults.query.start_date, timeSeriesResults.query.end_date);
            fullResults = {};
            for (var i = 0; i < scope.dateList.length; i++) {
                fullResults[scope.dateList[i]] = {count: 0, 'url': ''};
            }
        }
        var allResults = progressiveLoad.mergeResults(fullResults, timeSeriesResults.results['absolute_count'], "label");
        fullResults = allResults.unsorted;
        drawFromData(scope, allResults.sorted, "absolute_time");
        if (end < scope.resultsLength) {
            if (start === 0) {
                start = 1000;
            } else {
                start += 5000;
            }
            end += 5000;
            updateTimeSeries(scope, fullResults, start, end);
        } else {
            scope.percent = 100;
            scope.done = true;
            $(".progress").delay(500).velocity('slideUp');
            //saveToLocalStorage(scope.sortedLists);
        }
    }
    var drawFromData = function(scope, data, frequency_type) {
        var barWidth = (parseInt($('#time-series').width()) - 1 * data.length) / data.length;
        var maxCount = 0;
        var margin = 0;
        for (var i in data) {
            var count = Math.round(data[i].count);
            var year = data[i].label;
            var yearDisplay = yearToTimeSpan(year, scope.interval);
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
        // Draw three lines along the X axis to help visualize frequencies
        var top_line = (chart_height - 10) / chart_height * 100;
        $("#top-division").css('bottom', top_line + '%');
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
    var getTimeSeries = function(scope) {
        // Calculate width and height of chart
        var height = $(window).height() - $('#footer').height() - $('#initial_report').height() - $('#header').height() - 190;
        $('#time-series').css('height', height);
        var bodyWidth = parseInt($('body').width());
        $('#time-series, #first-division, #middle-division, #top-division').width(bodyWidth-90 + 'px');        
        
        scope.resultsLength = false; // set to false for now
        $(".progress").show();
        
        var fullResults;
        var absoluteFrequency;
        var dateCounts;
        updateTimeSeries(scope, fullResults, 0, 1000, absoluteFrequency, dateCounts);
    }
    var retrieveFromStorage = function(scope) {
        var time_series = JSON.parse(sessionStorage[window.location.href]);
        var date_counts = time_series['date_counts'];
        var abs_results = sortResults(time_series['abs_results']);
        var total = $("#time-series-length").html(total);
        $('#relative_counts').data('value', relativeCount(abs_results, date_counts))
        drawFromData(scope, abs_sorted_list, interval, "absolute_time");
    }
    return {
        restrict: 'E',
        template: '<div id="time-series"><div id="top-division"><div id="top-number"></div></div><div id="middle-division">' + 
                  '<div id="middle-number"></div></div><div id="first-division"><div id="first-number"></div></div><div id="side-text"></div></div>',
        link: function(scope, element, attrs) {
                if (sessionStorage[$location.url()] == null || $rootScope.philoConfig.debug === false) {
                    getTimeSeries(scope);
                } else {
                    retrieveFromStorage(scope);
                }
            }
    }
}]);