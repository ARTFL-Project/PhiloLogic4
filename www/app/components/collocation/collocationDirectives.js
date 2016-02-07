(function() {
    "use strict";

    angular
        .module('philoApp')
        .directive('collocationCloud', collocationCloud)
        .directive('collocationTable', collocationTable)
        .directive('collocationParameters', collocationParameters);

    function collocationCloud($compile, defaultDiacriticsRemovalMap) {
        var buildCloud = function(scope, sortedList) {
            var cloudList = angular.copy(sortedList);
            $.fn.tagcloud.defaults = {
                size: {
                    start: 1.0,
                    end: 3.5,
                    unit: 'em'
                },
                color: {
                    start: '#C4DFF3',
                    end: '#286895'
                }
            };
            angular.element('#collocate_counts').hide().empty();
            var removeDiacritics = function(str) {
                var changes = defaultDiacriticsRemovalMap.map;
                for (var i = 0; i < changes.length; i++) {
                    str = str.replace(changes[i].letters, changes[i].base);
                }
                return str;
            }
            cloudList.sort(function(a, b) {
                var x = removeDiacritics(a.label);
                var y = removeDiacritics(b.label);
                return x < y ? -1 : x > y ? 1 : 0;
            });
            var html = ''
            for (var i in cloudList) {
                var word = cloudList[i].label;
                var count = cloudList[i].count;
                var href = cloudList[i].url;
                var searchLink = '<span class="cloud_term" rel="' + count + '"><a ng-click="resolveCollocateLink($event)" collocate="' + word + '">';
                html += searchLink + word + '</a> </span>';
            }
            var el = angular.element(html);
            var compiledHTML = $compile(el)(scope); // Making ng-click work
            angular.element("#collocate_counts").html(el);
            angular.element("#collocate_counts span").tagcloud();
            angular.element("#collocate_counts").velocity('fadeIn');
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
                scope.resolveCollocateLink = function(e) {
                    var word = e.target.attributes.collocate.value;
                    scope.collocation.resolveCollocateLink(word);
                }
            }

        }
    }

    function collocationTable($rootScope, $http, $location, URL, progressiveLoad, saveToLocalStorage, request) {
        var getCollocations = function(scope) {
            if (typeof(sessionStorage[$location.url()]) === 'undefined' || $rootScope.philoConfig.production === false) {
                angular.element('#philologic_collocation').velocity('fadeIn', {
                    duration: 200
                });
                angular.element(".progress").show();
                var collocObject;
                scope.localFormData = angular.copy(scope.formData);
                updateCollocation(scope, collocObject, 0);
            } else {
                retrieveFromStorage(scope);
            }
        }
        var updateCollocation = function(scope, fullResults, start) {
            var collocation = this;
            request.report(scope.localFormData, {
                start: start
            }).then(function(response) {
                var data = response.data;
                scope.resultsLength = data.results_length;
                scope.moreResults = data.more_results;
                start = data.hits_done;
                sortAndRenderCollocation(scope, fullResults, data, start)
            }).catch(function(response) {
                scope.collocation.loading = false;
            });;
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
                var runningQuery = $location.search();
                if (scope.report === "collocation" && angular.equals(runningQuery, scope.localFormData)) { // make sure we're still running the same query
                    updateCollocation(scope, tempFullResults, start);
                }
            } else {
                scope.collocation.percent = 100;
                scope.done = true;
                // Collocation cloud not showing when loading cached searches one after the other
                //saveToLocalStorage({results: scope.sortedList, resultsLength: scope.resultsLength, filterList: scope.filterList});
            }
        }
        var retrieveFromStorage = function(scope) {
            var savedObject = angular.fromJson(sessionStorage[$location.url()]);
            scope.sortedList = savedObject.results;
            scope.resultsLength = savedObject.resultsLength;
            scope.filterList = savedObject.filterList;
            scope.collocation.percent = 100;
            scope.done = true;
            scope.collocation.loading = false;
            angular.element('#philologic_collocation').velocity('fadeIn', {
                duration: 200
            });
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
                    angular.element('.colloc_link').off();
                });
            }
        }
    }

    function collocationParameters() {
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
    }
})();
