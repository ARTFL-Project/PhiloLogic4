philoApp.controller('philoMain', ['$rootScope', '$scope', '$location', function($rootScope, $scope, $location) {
    $rootScope.report = philoReport;
    $rootScope.philoConfig = philoConfig;
    $rootScope.queryParams = {}
    $location.path(philoReport)
}]);

philoApp.factory('URL', function() {
    return {
        objectToString: function(formData, url) {
            var obj = angular.copy(formData);
            if (url) {
                var report = obj.report;
                delete obj.report;
                delete obj.format;
            }
            var str = [];
            for (var p in obj) {
                var k = p, 
                    v = obj[k];
                str.push(angular.isObject(v) ? qs(v, k) : (k) + "=" + encodeURIComponent(v));
            }
            if (url) {
                return report + '/' + str.join('&');
            } else {
                return str.join("&");
            }
        }
    }
});


philoApp.factory('biblioCriteria', ['$rootScope','$http', '$location', 'URL', function($rootScope, $http, $location, URL) {
        return {
            build: function(queryParams) {
                var queryArgs = angular.copy(queryParams);
                var biblio = []
                if (queryArgs.report === "time_series") {
                    delete queryParams.date;
                }
                for (var i=0; i < philoConfig.metadata.length; i++) {
                    var k = philoConfig.metadata[i];
                    var v = queryArgs[k];
                    if (v) {
                        if (queryArgs.report !== "concordance_from_collocation") {
                            var close_icon = '<span class="glyphicon glyphicon-remove-circle remove_metadata" data-metadata="' + k + '"></span>';
                        } else {
                            var close_icon = ""
                        }
                        if (k in philoConfig.metadata_aliases) {
                            k = philoConfig.metadataAliases[k];
                        }
                        var htmlContent = '<span class="biblio-criteria">' + k.charAt(0).toUpperCase() + k.slice(1) + ': <b>' + v + '</b> ' + close_icon + '</span>';
                        biblio.push({key: k, value: v});
                    }
                }
                return biblio
            },
            remove: function(metadata, queryParams) {
                delete queryParams[metadata];
                var request = {
                    method: "GET",
                    url: $rootScope.philoConfig.db_url + '/dispatcher.py?' + URL.objectToString(queryParams)
                }
                $http(request)
                .success(function(data, status, headers, config) {
                    $rootScope.results = data;
                    $location.url(URL.objectToString(queryParams, true));
                })
                .error(function(data, status, headers, config) {
                    console.log("Error", status, headers)
                });
            }
        }
}]);