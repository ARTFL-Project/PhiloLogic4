"use strict";

philoApp.directive('searchArguments', ['$rootScope','$http', '$timeout', '$location', 'URL', 'request', function($rootScope, $http, $timeout, $location, URL, request) {
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
        var facets = [];
        for (var i=0; i < config.facets.length; i++) {
            var alias = Object.keys(config.facets[i])[0];
            var facet = config.facets[i][alias];
            if (typeof(facet) === 'string') {
                facets.push(facet);
            } else {
                //facets.push(facet)
                angular.forEach(facet, function(value, i) {
                    if (facets.indexOf(value) < 0) {
                        facets.push(value);
                    }
                });
            }
        }
        for (var k in queryArgs) {
            if (config.metadata.indexOf(k) >= 0 || facets.indexOf(k) >= 0) {
                var v = queryArgs[k];
                var alias = k;
                if (v) {
                    if (k in config.metadata_aliases) {
                        alias = config.metadata_aliases[k];
                    }
                    biblio.push({key: k, alias: alias, value: v});
                }
            }
        }
        return biblio
    }
    var removeMetadata = function(metadata, queryParams, restart) {
        delete queryParams[metadata];
        if (!queryParams.q) {
            queryParams.report = 'bibliography';
        }
		queryParams.start = 0;
		queryParams.end = 0;
        var request = URL.report(queryParams);
        if (queryParams.report === "concordance" || queryParams.report === "kwic" || queryParams.report === "bibliography") {
            $http.get(request).success(function(data) {
                $location.url(URL.objectToUrlString(queryParams));
            })
        } else if (queryParams.report === "collocation" || queryParams.report === "time_series") {
            $location.url(URL.objectToUrlString(queryParams));
            $rootScope.formData = queryParams;
            restart = true;
        }
    }
    return {
        restrict: 'E',
        templateUrl: 'app/shared/searchArguments/searchArguments.html',
        link: function(scope, element, attrs) {
                scope.$watch(function() {
                    return $location.search();
                    }, function() {
                        scope.queryArgs = getSearchArgs($location.search());
                        scope.queryArgs.report = $location.search().report;
                    }, true);
                scope.formData = $rootScope.formData;
                scope.removeMetadata = removeMetadata;
				
				// Query terms functionality
                scope.getQueryTerms = function() {
                    request.script(scope.formData, {
                        script: 'get_query_terms.py'
                    }).then(function(response) {
                        scope.words = response.data;
                        $timeout(function() {
                            $('#query-terms').velocity('fadeIn');
                        })
                    });
                }
                scope.wordListChanged = false;
                scope.closeTermsList = function() {
                    $('#query-terms').velocity('fadeOut')
                }
                scope.removeFromTermsList = function(word) {
                    var index = scope.words.indexOf(word);
                    scope.words.splice(index, 1);
                    scope.wordListChanged = true;
                    $rootScope.formData.q += ' NOT ' + word.trim();
                }
                scope.rerunQuery = function() {
                    var url = URL.objectToUrlString($rootScope.formData);
                    $location.url(url);
                }
        } 
    }
}]);