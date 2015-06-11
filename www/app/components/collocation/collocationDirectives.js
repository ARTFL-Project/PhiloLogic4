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
        template: '<div id="word_cloud" class="word_cloud text-content-area">' +
                  '<div id="collocate_counts" class="collocation_counts"></div></div>',
        replace: true,
        link: function(scope, element, attrs) {
                scope.$watch('sortedList', function() {
                    if (!$.isEmptyObject(scope.sortedList)) {
                        scope.cloud = buildCloud(scope, scope.sortedList);
                    }
                });
                scope.$on('$destroy', function() {
                    $('.cloud_term').off();
                });
        }
        
    }
}]);

philoApp.directive('collocationTable', ['$rootScope', '$http', '$location', 'URL', 'progressiveLoad', 'saveToLocalStorage', "request",
                                        function($rootScope, $http, $location, URL, progressiveLoad, save, request) {
    var getCollocations = function(scope) {
        if (typeof(sessionStorage[$location.url()]) === 'undefined' || $rootScope.philoConfig.production === false) {
            $('#philologic_collocation').velocity('fadeIn', {duration: 200});
            $(".progress").show();
            var collocObject;
            scope.localFormData = angular.copy(scope.formData);
            updateCollocation(scope, collocObject, 0);
        } else {
            retrieveFromStorage(scope);
        }  
    }
    var updateCollocation = function(scope, fullResults, start) {
        var collocation = this;
        request.report(scope.localFormData, {start: start}).then(function(response) {
            var data = response.data;
            scope.resultsLength = data.results_length;
            scope.moreResults = data.more_results;
			start = data.hits_done;
            sortAndRenderCollocation(scope, fullResults, data, start)
        });
    }
    var sortAndRenderCollocation = function(scope, fullResults, data, start) {
        if (start <= scope.resultsLength) {
            scope.collocation.percent = Math.floor(start / scope.resultsLength * 100);
        }
        if (typeof(fullResults) === "undefined") {
            fullResults = {}
            scope.filterList = data.filter_list;
        }
        var collocates = progressiveLoad.mergeResults(fullResults, data["collocates"]);
        scope.sortedList = collocates.sorted.slice(0, 100);
        scope.collocation.loading = false;
        if (scope.moreResults) {
            var tempFullResults = collocates.unsorted;
            if (scope.report === "collocation") { // make sure we haven't moved to a different report
                updateCollocation(scope, tempFullResults, start);
            }
        } else {
            scope.collocation.percent = 100;
            scope.done = true;
            activateLinks();
            // Collocation cloud not showing when loading cached searches one after the other
            //save({results: scope.sortedLists, resultsLength: scope.resultsLength, filterList: scope.filterList});
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
        scope.collocation.percent = 100;
        scope.done = true;
        scope.collocation.loading = false;
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
            scope.$on('$destroy', function() {
                $('.colloc_link').off();
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