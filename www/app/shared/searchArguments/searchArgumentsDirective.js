"use strict";

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
    var removeMetadata = function(metadata, queryParams, restart) {
        delete queryParams[metadata];
        if (!queryParams.q) {
            queryParams.report = 'bibliography';
        }
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
        } 
    }
}]);