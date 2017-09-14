(function() {
    "use strict";

    angular
        .module("philoApp")
        .directive('searchArguments', searchArguments);

    function searchArguments($rootScope, $http, $timeout, $location, URL, request, queryTermGroups, philoConfig) {
        var getSearchArgs = function(queryParams) {
            var queryArgs = {};
            if ('q' in queryParams) {
                queryArgs.queryTerm = queryParams.q;
            } else {
                queryArgs.queryTerm = '';
            }
            queryArgs.biblio = buildCriteria(queryParams);

            if ('q' in queryParams) {
                var method = queryParams.method;
                if (typeof(method) === 'undefined') {
                    method = 'proxy';
                }
                if (queryParams.q.split(' ').length > 1) {
                    if (method === "proxy") {
                        if (typeof(queryParams.arg_proxy) !== 'undefined' || queryParams.arg_proxy) {
                            queryArgs.proximity = 'within ' + queryParams.arg_proxy + ' words';
                        } else {
                            queryArgs.proximity = '';
                        }
                    } else if (method === 'phrase') {
                        if (typeof(queryParams.arg_proxy) !== 'undefined' || queryParams.arg_phrase) {
                            queryArgs.proximity = 'within exactly ' + queryParams.arg_phrase + ' words';
                        } else {
                            queryArgs.proximity = ''
                        }
                    } else if (method === 'cooc') {
                        queryArgs.proximity = 'in the same sentence';
                    }
                } else {
                    queryArgs.proximity = '';
                }
            }
            if (queryParams.approximate == "yes") {
                queryArgs.approximate = true;
            } else {
                queryArgs.approximate = false;
            }
            return queryArgs;
        }
        var buildCriteria = function(queryParams) {
            var queryArgs = angular.copy(queryParams);
            var biblio = []
            if (queryArgs.report === "time_series") {
                delete queryParams[philoConfig.time_series_year_field];
            }
            var config = $rootScope.philoConfig;
            var facets = [];
            for (var i = 0; i < config.facets.length; i++) {
                var alias = Object.keys(config.facets[i])[0];
                var facet = config.facets[i][alias];
                if (angular.isString(facet)) {
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
                if (config.available_metadata.indexOf(k) >= 0) {
                    var v = queryArgs[k];
                    var alias = k;
                    if (v) {
                        if (k in config.metadata_aliases) {
                            alias = config.metadata_aliases[k];
                        }
                        biblio.push({ key: k, alias: alias, value: v });
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
                $location.url(URL.objectToUrlString(queryParams));
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


                scope.termGroups = queryTermGroups.group;
                // Get parsed query group
                request.script(scope.formData, {
                    script: 'get_term_groups.py'
                }).then(function(response) {
                    scope.termGroups = response.data.term_groups;
                    scope.originalQuery = response.data.original_query;
                    queryTermGroups.group = angular.copy(scope.termGroups);
                    scope.termGroupsCopy = angular.copy(scope.termGroups);
                });

                // Query terms functionality
                scope.getQueryTerms = function(group, index) {
                    scope.groupIndexSelected = index;
                    request.script(scope.formData, {
                        script: 'get_query_terms.py',
                        q: group,
                        approximate: 0
                    }).then(function(response) {
                        scope.words = response.data;
                        $timeout(function() {
                            angular.element('#query-terms').velocity('fadeIn');
                        })
                    });
                }
                scope.wordListChanged = false;
                scope.closeTermsList = function() {
                    angular.element('#query-terms').velocity('fadeOut')
                }
                scope.removeFromTermsList = function(word, groupIndex) {
                    var index = scope.words.indexOf(word);
                    scope.words.splice(index, 1);
                    scope.wordListChanged = true;
                    if (scope.termGroupsCopy[groupIndex].indexOf(' NOT ') !== -1) { // if there's already a NOT in the clause add an OR
                        scope.termGroupsCopy[groupIndex] += ' | ' + word.trim();
                    } else {
                        scope.termGroupsCopy[groupIndex] += ' NOT ' + word.trim();
                    }
                    $rootScope.formData.q = scope.termGroupsCopy.join(' ');
                    delete $rootScope.formData.approximate;
                    delete $rootScope.formData.approximate_ratio;
                }
                scope.rerunQuery = function() {
                    var url = URL.objectToUrlString($rootScope.formData);
                    $location.url(url);
                }
                scope.removeTerm = function(index) {
                    scope.termGroups.splice(index, 1);
                    queryTermGroups.group = angular.copy(scope.termGroups);
                    $rootScope.formData.q = scope.termGroups.join(' ');
                    if (scope.termGroups.length === 0) {
                        $rootScope.formData.report = "bibliography";
                    }
                    var url = URL.objectToUrlString($rootScope.formData, {
                        start: 0,
                        end: 0
                    });
                    $location.url(url);
                }
            }
        };
    }
})();