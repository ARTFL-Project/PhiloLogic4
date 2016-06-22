(function() {

    "use strict";

    angular
        .module('philoApp')
        .directive('facets', facets);

    function facets($rootScope, $location, request, progressiveLoad, saveToLocalStorage, URL, philoConfig, facetedBrowsing) {
        var populateFacets = function() {
            var facetConfig = philoConfig.facets;
            var facets = [];
            for (var i = 0; i < facetConfig.length; i++) {
                var facet = facetConfig[i];
                console.log(facet)
                if (facet in philoConfig.metadata_aliases) {
                    var alias = philoConfig.metadata_aliases[facet];
                } else {
                    var alias = facet;
                }
                facets.push({
                    facet: facet,
                    alias: alias,
                    type: 'facet'
                });
            }
            return facets;
        }
        var populateCollocationFacets = function() {
            var collocationFacets = [{
                facet: "all_collocates",
                alias: "in the same sentence",
                type: "collocationFacet"
            }, ];
            return collocationFacets;
        }
        var populateWordFacets = function() {
            var wordsFacets = [];
            for (var i = 0; i < $rootScope.philoConfig.words_facets.length; i++) {
                var alias = Object.keys($rootScope.philoConfig.words_facets[i])[0];
                var facet = $rootScope.philoConfig.words_facets[i][alias];
                wordsFacets.push({
                    facet: facet,
                    alias: alias,
                    type: 'wordFacet'
                });
            }
            return wordsFacets;
        }
        var getFacet = function(scope, facetObj) {
            scope.facet = facetObj;
            scope.selectedFacet = facetObj;
            var urlString = $location.url() + '&frequency_field=' + facetObj.alias;
            if (typeof(sessionStorage[urlString]) !== "undefined" && $rootScope.philoConfig.production === true) {
                scope.loading = true;
                scope.fullResults = fromJson(sessionStorage[urlString]);
                scope.facetResults = scope.fullResults.sorted.slice(0, 500);
                scope.loading = false;
                scope.percent = 100;
            } else {
                // store the selected field to check whether to kill the ajax calls in populate_sidebar
                angular.element('#select-facets').data('selected', facetObj.alias);
                angular.element('#select-facets').data('interrupt', false);
                scope.done = false;
                var fullResults = {};
                scope.loading = true;
                scope.moreResults = true;
                scope.percent = 0;
                var queryParams = angular.copy($rootScope.formData);
                if (facetObj.type === "facet") {
                    queryParams.script = "get_frequency.py";
                    queryParams.frequency_field = facetObj.facet;
                } else if (facetObj.type === "collocationFacet") {
                    queryParams.report = "collocation";
                } else {
                    queryParams.field = facetObj.facet;
                    queryParams.script = "get_word_frequency.py";
                }
                populateSidebar(scope, facetObj, fullResults, 0, queryParams);
            }
        }
        var populateSidebar = function(scope, facet, fullResults, start, queryParams) {
            if (scope.moreResults) {
                if (facet.type !== "collocationFacet") {
                    var promise = request.script(queryParams, {
                        start: start
                    });
                } else {
                    var promise = request.report(queryParams, {
                        start: start
                    });
                }
                scope.showFacetSelection = false;
                promise.then(function(response) {
                    var results = response.data.results;
                    scope.moreResults = response.data.more_results;
                    scope.resultsLength = response.data.results_length;
                    scope.sidebarHeight = {
                        maxHeight: angular.element('#results_container').height() - 41 + 'px'
                    };
                    if (angular.element('#select-facets').data('interrupt') != true && angular.element('#select-facets').data('selected') == facet.alias) {
                        if (facet.type === "collocationFacet") {
                            var merge = progressiveLoad.mergeResults(fullResults.unsorted, response.data.collocates);
                        } else {
                            var merge = progressiveLoad.mergeResults(fullResults.unsorted, results);
                        }
                        scope.facetResults = merge.sorted.slice(0, 500);
                        scope.loading = false;
                        scope.showFacetResults = true;
                        fullResults = merge;
                        if (response.data.hits_done < scope.resultsLength) {
                            $rootScope.percentComplete = response.data.hits_done / scope.resultsLength * 100;
                            scope.percent = Math.floor($rootScope.percentComplete);
                        }
                        start = response.data.hits_done;
                        populateSidebar(scope, facet, fullResults, start, queryParams);
                    } else {
                        // This won't affect the full collocation report which can't be interrupted when on the page
                        angular.element('#select-facets').data('interrupt', false);
                    }
                }).catch(function(response) {
                    scope.loading = false;
                });
            } else {
                scope.percent = 100;
                scope.fullResults = fullResults;
                var urlString = $location.url() + '&frequency_field=' + scope.selectedFacet.alias;
                saveToLocalStorage(fullResults, urlString);
            }
        }
        var getRelativeFrequencies = function(scope, hitsDone) {
            $http.post('scripts/get_metadata_token_count.py',
                    angular.toJson({
                        results: scope.fullResults.unsorted,
                        hits_done: hitsDone
                    }))
                .then(function(response) {
                    angular.merge(scope.fullRelativeFrequencies, response.data.frequencies);
                    var sortedRelativeResults = progressiveLoad.sortResults(scope.fullRelativeFrequencies);
                    scope.facetResults = angular.copy(sortedRelativeResults.slice(0, 500));
                    scope.showingRelativeFrequencies = true;
                    scope.loading = false;
                    if (response.data.more_results) {
                        scope.percent = Math.round(sortedRelativeResults.length / scope.fullResults.sorted.length * 100);
                        getRelativeFrequencies(scope, response.data.hits_done)
                    } else {
                        scope.percent = 100
                    }
                }).catch(function(response) {
                    scope.loading = false;
                });
        }
        return {
            restrict: 'E',
            templateUrl: 'app/components/concordanceKwic/facets.html',
            replace: true,
            link: function(scope) {
                scope.showFacetSelection = true;
                scope.showFacetResults = false;
                scope.facets = populateFacets();
                scope.collocationFacets = populateCollocationFacets();
                scope.wordsFacets = populateWordFacets();
                scope.getFacet = function(facetObj) {
                    getFacet(scope, facetObj);
                }
                scope.displayRelativeFrequencies = function() {
                    scope.loading = true;
                    if (scope.relativeFrequencies === 'undefined') {
                        scope.absoluteFrequencies = angular.copy(scope.facetResults);
                        scope.percent = 0;
                        scope.fullRelativeFrequencies = {};
                        getRelativeFrequencies(scope, 0);
                    } else {
                        scope.absoluteFrequencies = angular.copy(scope.facetResults);
                        scope.facetResults = scope.relativeFrequencies;
                        scope.showingRelativeFrequencies = true;
                        scope.loading = false;
                    }
                }
                scope.displayAbsoluteFrequencies = function() {
                    scope.loading = true;
                    scope.relativeFrequencies = angular.copy(scope.facetResults);
                    scope.facetResults = scope.absoluteFrequencies;
                    scope.showingRelativeFrequencies = false;
                    scope.loading = false;
                }
                scope.collocationToConcordance = function(word) {
                    var q = $location.search().q + ' "' + word + '"';
                    var newUrl = URL.objectToUrlString($location.search(), {
                        method: "cooc",
                        start: "0",
                        end: '0',
                        q: q,
                        report: "concordance"
                    });
                    $location.url(newUrl);
                }
                scope.closeFacets = function() {
                    scope.showFacetResults = false;
                    scope.showFacetSelection = true;
                }
                scope.toggleDisplayFacetSelection = function() {
                    if (scope.showFacetSelection) {
                        scope.showFacetSelection = false;
                    } else {
                        scope.showFacetSelection = true;
                    }
                }
                scope.hideFacets = function() {
                    scope.concKwic.showFacetedBrowsing = false;
                    facetedBrowsing.show = false;
                }
            }
        }
    }
})();
