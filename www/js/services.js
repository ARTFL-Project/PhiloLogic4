"use strict"

philoApp.factory('searchConfigBuild', ['$rootScope', function($rootScope) {
    return {
        timeSeriesIntervals: function() {
            var options = {1: "Year", 10: "Decade", 50: "Half Century", 100: "Century"};
            var intervals = [];
            for (var i=0; i < $rootScope.philoConfig.time_series_intervals.length; i++) {
                var interval = {
                    date: $rootScope.philoConfig.time_series_intervals[i],
                    alias: options[$rootScope.philoConfig.time_series_intervals[i]]
                };
                intervals.push(interval);
            }
            return intervals
        },
        metadata: function() {
            var metadataFields = {};
            for (var i=0; i < $rootScope.philoConfig.metadata.length; i++) {
                var metadata = $rootScope.philoConfig.metadata[i];
                metadataFields[metadata] = {}
                if (metadata in $rootScope.philoConfig.metadata_aliases) {
                    metadataFields[metadata].value = $rootScope.philoConfig.metadata_aliases[metadata];
                } else {
                    metadataFields[metadata].value = metadata;
                }
                metadataFields[metadata].example = $rootScope.philoConfig.search_examples[metadata];
            }
            return metadataFields
        }
    }
}]);

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
            if ("script" in obj) {
                return "scripts/" + obj.script + '?' + str.join("&");
            } else {
                return "reports/" + obj.report + '.py?' + str.join("&");
            }
        },
        path: function(pathInfo) {
            pathInfo = pathInfo.split(' ').join('/');
            return "dispatcher.py/" + pathInfo;
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
        mergeCollocationResults: function(fullResults, newData) {
            for (var key in newData) {
                var value = newData[key];
                if (key in fullResults) {
                    fullResults[key].count += value.count;
                } else {
                    fullResults[key] = {'count': value.count, 'url': value.url};
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
        },
        sortCollocationResults: function(fullResults) {
            var sortedList = [];
            for (var key in fullResults) {
                sortedList.push([key, fullResults[key]]);
            }
            sortedList.sort(function(a,b) {return b[1].count - a[1].count});
            return sortedList;
        }
    }
}]);

philoApp.filter('unsafe', function($sce) { return $sce.trustAsHtml; });