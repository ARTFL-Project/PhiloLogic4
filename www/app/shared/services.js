"use strict";

philoApp.filter('unsafe', function($sce) { return $sce.trustAsHtml; });

philoApp.factory('accessControl', ['$rootScope', '$cookies', '$location', function($rootScope, $cookies, $location) {
    return {
        cookieCheck: function() {
            if (typeof($cookies.hash) !== 'undefined') {
                return true
            } else {
                return false
            }
        }
    }
}])

philoApp.factory('radio', ['$rootScope', function($rootScope) {
    return {
        click: function(key, value) {
            $rootScope.formData[key] = value;
        }
    }
}]);

philoApp.factory('request', ['$http', 'URL', function($http, URL) {
    return {
        report: function(queryParams, extraParams) {
            var request = URL.report(queryParams, extraParams);
            var promise = $http.get(request).success(function(data, status, headers, config) {
                return data;
            });
            return promise;
        },
        script: function(queryParams, extraParams) {
            var request = URL.script(queryParams, extraParams);
            var promise = $http.get(request).success(function(data, status, headers, config) {
                return data;
            });
            return promise;
        }   
    }
}]);

philoApp.factory('URL', function() {
    return {
        mergeParams: function(queryParams, extraParams) {
            var localParams = angular.copy(queryParams);
            if (typeof extraParams !== 'undefined') {
                angular.forEach(extraParams, function(value, param) {
                    localParams[param] = value;
                });
            }
            return localParams;            
        },
        objectToString: function(localParams) {
            var str = [];
            for (var p in localParams) {
                var k = p, 
                    v = localParams[k];
                if (typeof(v) === 'object') {
                    for (var i=0; i < v.length; i++) {
                        str.push(angular.isObject(v[i]) ? this.query(v[i], k) : (k) + "=" + encodeURIComponent(v[i]));
                    }
                } else {
                    str.push(angular.isObject(v) ? this.query(v, k) : (k) + "=" + encodeURIComponent(v));
                }
            }
            return str.join('&')
        },
        objectToUrlString: function(queryParams, extraParams) {
            var localParams = this.mergeParams(queryParams, extraParams)
            var urlString = this.objectToString(localParams)
            return "query?" + urlString;
        },
        report: function(queryParams, extraParams) {
            var localParams = this.mergeParams(queryParams, extraParams)
            var urlString = this.objectToString(localParams)
            return "reports/" + localParams.report + '.py?' + urlString;
        },
        script: function(queryParams, extraParams) {
            var localParams = this.mergeParams(queryParams, extraParams)
            var urlString = this.objectToString(localParams)
            return "scripts/" + localParams.script + '?' + urlString + '&report=' + localParams.report;
        },
        path: function(pathInfo) {
            pathInfo = pathInfo.split(' ').join('/');
            return "navigate/" + pathInfo;
        }
    }
});

philoApp.factory('progressiveLoad', function() {
    return {
        mergeResults: function(fullResults, newData, sortKey) {
            if (typeof fullResults === 'undefined') {
                fullResults = newData;
            } else {
                angular.forEach(newData, function(value, key) {
                    if (typeof value.count !== 'undefined') {
                        if (key in fullResults) {
                            fullResults[key].count += value.count;
                            fullResults[key].url = value.url; // Update URL for collocations
                        } else {
                            fullResults[key] = value;
                        }
                    }
                });
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
        }
    }
});

philoApp.factory('saveToLocalStorage', ['$location', function($location) {
    var save = function(results, urlString) {
        if (typeof(urlString) === 'undefined') {
            urlString = $location.url();
        }
        try {
            sessionStorage[urlString] = JSON.stringify(results);
            console.log('saved results to localStorage');
        } catch(e) {
            sessionStorage.clear();
            console.log("Clearing sessionStorage for space...");
            try {
                sessionStorage[urlString] = JSON.stringify(results);
                console.log('saved results to localStorage');
            } catch(e) {
                sessionStorage.clear();
                console.log("Quota exceeded error: the JSON object is too big...")
            }
        }
    }
    return save;
}]);