"use strict"

philoApp.factory('URL', function() {
    return {
        objectToString: function(formData, url) {
            var obj = angular.copy(formData);
            var str = [];
            for (var p in obj) {
                var k = p, 
                    v = obj[k];
                str.push(angular.isObject(v) ? qs(v, k) : (k) + "=" + encodeURIComponent(v));
            }
            return "dispatcher.py?" + str.join("&");
        },
        query: function(formData, url) {
            var obj = angular.copy(formData);
            var str = [];
            for (var p in obj) {
                var k = p, 
                    v = obj[k];
                str.push(angular.isObject(v) ? qs(v, k) : (k) + "=" + encodeURIComponent(v));
            }
            return "reports/" + obj.report + '.py?' + str.join("&");
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
                    url: $rootScope.philoConfig.db_url + '/' + URL.query(queryParams)
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

philoApp.factory('progressiveLoad', ['$rootScope', function($rootScope) {
    return {
        updateProgressBar: function(element, percent) {
            var truncated_percent = parseInt(percent.toString().split('.')[0]);
            element.velocity({'width': truncated_percent + '%'}, { queue: false, complete:function() {
                element.text(percent.toString().split('.')[0] + '%');}});
        },
        mergeResults: function(fullResults, newData) {
            if (typeof fullResults === 'undefined') {
                fullResults = newData;
            } else {
                for (var key in newData) {
                    if (key in fullResults) {
                        fullResults[key]['count'] += newData[key]['count'];
                    }
                    else {
                        fullResults[key] = newData[key];
                    }
                }
            }
            var sortedList = this.sortResults(fullResults);
            return {"sorted": sortedList, "unsorted": fullResults};
        },
        sortResults: function(fullResults) {
            var sortedList = [];
            for (var key in fullResults) {
                sortedList.push({label:key, count: fullResults[key].count});
            }
            sortedList.sort(function(a,b) {return b.count - a.count});
            return sortedList;
        }
    }
}]);