"use strict";

philoApp.directive('collocationCloud', ['defaultDiacriticsRemovalMap', function(defaultDiacriticsRemovalMap) {
    var buildCloud = function(scope, sortedList) {
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
            var searchLink = '<span class="cloud_term" rel="' + count + '"><a href="' + href + '&collocate_num=' + count + '">';
            html += searchLink + word + '</a> </span>';
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
                        scope.cloud = buildCloud(scope, scope.sortedLists.all);
                    }
                });
        }
        
    }
}]);

philoApp.directive('collocationTable', ['$rootScope', '$http', '$location', 'URL', 'progressiveLoad', 'saveToLocalStorage',
                                        function($rootScope, $http, $location, URL, progressiveLoad, save) {
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
        $http.get(request).then(function(response) {
            var data = response.data;
            if (!resultsLength) {
                // Fetch total results now since we know the hitlist will be fully on disk
                var queryParams = angular.copy($rootScope.formData)
                queryParams.script = "get_total_results.py";
                queryParams.report = "concordance"
                $http.get($rootScope.philoConfig.db_url + '/' + URL.query(queryParams))
                .then(function(results) {
                    scope.resultsLength = results.data;
                    sortAndRenderCollocation(scope, fullResults, data, results.data, start, end)
                })
            } else {
                sortAndRenderCollocation(scope, fullResults, data, resultsLength, start, end)
            }
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
            save({results: scope.sortedLists, resultsLength: scope.resultsLength, filterList: scope.filterList});
        }
    }
    var getCollocations = function(scope) {
        if (typeof(sessionStorage[$location.url()]) === 'undefined' || $rootScope.philoConfig.debug === true) {
            $('#philologic_collocation').velocity('fadeIn', {duration: 200});
            $(".progress").show();
            var collocObject;
            updateCollocation(scope, collocObject, false, 0, 1000);
        } else {
            retrieveFromStorage(scope);
        }
        
    }
    var retrieveFromStorage = function(scope) {
        var savedObject = JSON.parse(sessionStorage[$location.url()]);
        scope.sortedLists = savedObject.results;
        scope.resultsLength = savedObject.resultsLength;
        scope.filterList = savedObject.filterList;
        scope.percent = 100;
        scope.done = true;
        $('#philologic_collocation').velocity('fadeIn', {duration: 200});
    }
    return {
        restrict: 'E',
        templateUrl: 'app/components/collocation/collocationTable.html',
        link: function(scope, element, attrs) {
                getCollocations(scope);
                scope.restart = false; 
                scope.$watch('restart', function() {
                    if (scope.restart) {
                        getCollocations(scope);
                    }
                });
            }
    }
}]);