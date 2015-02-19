"use strict"

philoApp.filter('unsafe', function($sce) { return $sce.trustAsHtml; });

philoApp.factory('radio', ['$rootScope', function($rootScope) {
    return {
        click: function(key, value) {
            $rootScope.formData[key] = value;
        }
    }
}]);

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
                str.push(angular.isObject(v) ? this.objectToString(v, k) : (k) + "=" + encodeURIComponent(v));
            }
            return "dispatcher.py?" + str.join("&");
        },
        query: function(formData, url) {
            var obj = angular.copy(formData);
            var str = [];
            for (var p in obj) {
                var k = p, 
                    v = obj[k];
                str.push(angular.isObject(v) ? this.query(v, k) : (k) + "=" + encodeURIComponent(v));
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

philoApp.factory('progressiveLoad', ['$rootScope', function($rootScope) {
    return {
        mergeResults: function(fullResults, newData, sortKey) {
            if (typeof fullResults === 'undefined') {
                fullResults = newData;
            } else {
                for (var key in newData) {
                    if (key in fullResults) {
                        fullResults[key].count += newData[key].count;
                    }
                    else {
                        fullResults[key] = newData[key];
                    }
                }
            }
            var sortedList = this.sortResults(fullResults, sortKey);
            return {"sorted": sortedList, "unsorted": fullResults};
        },
        sortResults: function(fullResults, sortKey) {
            var sortedList = [];
            for (var key in fullResults) {
                sortedList.push({label:key, count: parseInt(fullResults[key].count), url: fullResults[key].url});
            }
            if (sortKey === "label") {
                sortedList.sort(function(a,b) {return a.label - b.label});
            } else {
                sortedList.sort(function(a,b) {return b.count - a.count});
            }
            return sortedList;
        },
        saveToLocalStorage: function(results) {
            if (typeof(localStorage) == 'undefined' ) {
                alert('Your browser does not support HTML5 localStorage. Try upgrading.');
            } else {
                try {
                    sessionStorage[$location.url()] = JSON.stringify(results);
                } catch(e) {
                    sessionStorage.clear();
                    console.log("Clearing sessionStorage for space...");
                    try {
                        sessionStorage[$location.url()] = JSON.stringify(results);
                    } catch(e) {
                        sessionStorage.clear();
                        console.log("Quota exceeded error: the JSON object is too big...")
                    }
                }
            }
        }
    }
}]);