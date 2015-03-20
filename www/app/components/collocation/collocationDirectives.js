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
        replace: true,
        link: function(scope, element, attrs) {
                scope.$watch('sortedLists', function() {
                    if (!$.isEmptyObject(scope.sortedLists)) {
                        scope.cloud = buildCloud(scope, scope.sortedLists.all);
                    }
                });
        }
        
    }
}]);

philoApp.directive('collocationTable', ['$rootScope', '$http', '$location', 'URL', 'progressiveLoad', 'saveToLocalStorage', "request",
                                        function($rootScope, $http, $location, URL, progressiveLoad, save, request) {
    var getCollocations = function(scope) {
        if (typeof(sessionStorage[$location.url()]) === 'undefined' || $rootScope.philoConfig.debug === true) {
            $('#philologic_collocation').velocity('fadeIn', {duration: 200});
            $(".progress").show();
            var collocObject;
            updateCollocation(scope, collocObject, 0, 1000);
        } else {
            retrieveFromStorage(scope);
        }  
    }
    var updateCollocation = function(scope, fullResults, start, end) {
        var collocation = this;
        request.report($rootScope.formData, {start: start, end: end}).then(function(response) {
            var data = response.data;
            scope.resultsLength = data.results_length;
            scope.moreResults = data.more_results;
            sortAndRenderCollocation(scope, fullResults, data, start, end)
        });
    }
    var sortAndRenderCollocation = function(scope, fullResults, data, start, end) {
        if (end <= scope.resultsLength) {
            scope.collocation.percent = Math.floor(end / scope.resultsLength * 100);
        }
        if (typeof(fullResults) === "undefined") {
            fullResults = {"all_collocates": {}, 'left_collocates': {}, 'right_collocates': {}}
            scope.filterList = data.filter_list;
        }
        var all = progressiveLoad.mergeResults(fullResults["all_collocates"], data["all_collocates"]);
        var left = progressiveLoad.mergeResults(fullResults["left_collocates"], data['left_collocates']);
        var right = progressiveLoad.mergeResults(fullResults["right_collocates"], data['right_collocates']);
        scope.sortedLists = {
            'all': all.sorted.slice(0, 100),
            'left': left.sorted.slice(0, 100),
            'right': right.sorted.slice(0, 100)
            };
        scope.collocation.loading = false;
        if (scope.moreResults) {
            var tempFullResults = {"all_collocates": all.unsorted, "left_collocates": left.unsorted, "right_collocates": right.unsorted};
            if (start === 0) {
                start = 1000;
            } else {
                start += 5000;
            }
            end += 5000;
            updateCollocation(scope, tempFullResults, start, end);
        } else {
            scope.collocation.percent = 100;
            scope.done = true;
            activateLinks();
            save({results: scope.sortedLists, resultsLength: scope.resultsLength, filterList: scope.filterList});
        }
    }
    var activateLinks = function() {
        // Activate links on collocations
        $('span[id^=all_word], span[id^=left_word], span[id^=right_word]').addClass('colloc_link');
        var href = window.location.href;
        $('.colloc_link, .cloud_term').click(function(e) {
            e.preventDefault();
            window.location = $(this).data('href');
        });
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
        replace: true,
        link: function(scope, element, attrs) {
            getCollocations(scope);
            scope.restart = false; 
            scope.$watch('restart', function() {
                if (scope.restart) {
                    scope.collocation.loading = true;
                    getCollocations(scope);
                }
            });
        }
    }
}]);

philoApp.directive('collocationParameters', function() {
    return {
        templateUrl: 'app/components/collocation/collocationParameters.html',
        replace: true,
        link: function(scope) {
            scope.collocationParams = {
                q: scope.formData.q,
                wordNum: scope.formData.word_num,
                collocFilterChoice: scope.formData.colloc_filter_choice,
                collocFilterFrequency: scope.formData.filter_frequency,
                collocFilterList: scope.formData.filter_list
            }
        }
    }
});