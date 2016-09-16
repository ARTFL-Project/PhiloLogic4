(function() {
    "use strict";

    angular
        .module("philoApp")
        .factory("accessControl", accessControl)
        .factory("radio", radio)
        .factory("URL", URL)
        .factory("request", request)
        .factory("progressiveLoad", progressiveLoad)
        .factory("saveToLocalStorage", saveToLocalStorage);


    function accessControl($rootScope, $cookies) {
        return {
            cookieCheck: function() {
                if (typeof($cookies.hash) !== "undefined") {
                    return true;
                } else {
                    return false;
                }
            }
        };
    }

    function radio($rootScope) {
        return {
            click: function(key, value) {
                $rootScope.formData[key] = value;
            }
        };
    }

    function URL() {
        return {
            mergeParams: function(queryParams, extraParams) {
                var localParams = angular.copy(queryParams);
                if (typeof extraParams !== "undefined") {
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
                    if (angular.isObject(v)) {
                        for (var i = 0; i < v.length; i++) {
                            str.push(angular.isObject(v[i]) ? this.query(v[i], k) : (k) + "=" + encodeURIComponent(v[i]));
                        }
                    } else {
                        str.push(angular.isObject(v) ? this.query(v, k) : (k) + "=" + encodeURIComponent(v));
                    }
                }
                return str.join("&")
            },
            objectToUrlString: function(queryParams, extraParams) {
                var localParams = this.mergeParams(queryParams, extraParams);
                var urlString = this.objectToString(localParams);
                return "query?" + urlString;
            },
            report: function(queryParams, extraParams) {
                var localParams = this.mergeParams(queryParams, extraParams);
                var urlString = this.objectToString(localParams);
                return "reports/" + localParams.report + ".py?" + urlString;
            },
            script: function(queryParams, extraParams) {
                var localParams = this.mergeParams(queryParams, extraParams);
                var urlString = this.objectToString(localParams);
                return "scripts/" + localParams.script + "?" + urlString + "&report=" + localParams.report;
            },
            path: function(pathInfo) {
                pathInfo = pathInfo.split(" ").join("/");
                return "navigate/" + pathInfo;
            }
        };
    }

    function request($http, URL) {
        return {
            report: function(queryParams, extraParams) {
                var UrlRequest = URL.report(queryParams, extraParams);
                var promise = $http.get(UrlRequest).success(function(data) {
                    return data;
                });
                return promise;
            },
            script: function(queryParams, extraParams) {
                var UrlRequest = URL.script(queryParams, extraParams);
                var promise = $http.get(UrlRequest).success(function(data) {
                    return data;
                });
                return promise;
            }
        };
    }

    function progressiveLoad() {
        return {
            mergeResults: function(fullResults, newData, sortKey) {
                if (typeof fullResults === "undefined") {
                    fullResults = newData;
                } else {
                    angular.forEach(newData, function(value, key) {
                        if (typeof value.count !== "undefined") {
                            if (key in fullResults) {
                                fullResults[key].count += value.count;
                            } else {
                                fullResults[key] = value;
                            }
                        }
                    });
                }
                var sortedList = this.sortResults(fullResults, sortKey);
                return {
                    "sorted": sortedList,
                    "unsorted": fullResults
                };
            },
            sortResults: function(fullResults, sortKey) {
                var sortedList = [];
                for (var key in fullResults) {
                    sortedList.push({
                        label: key,
                        count: parseFloat(fullResults[key].count),
                        url: fullResults[key].url
                    });
                }
                if (sortKey === "label") {
                    sortedList.sort(function(a, b) {
                        return a.label - b.label;
                    });
                } else {
                    sortedList.sort(function(a, b) {
                        return b.count - a.count;
                    });
                }
                return sortedList;
            }
        };
    }

    function saveToLocalStorage($location, $log) {
        var save = function(results, urlString) {
            if (typeof(urlString) === "undefined") {
                urlString = $location.url();
            }
            try {
                sessionStorage[urlString] = toJson(results);
                $log.debug("saved results to localStorage");
            } catch (e) {
                sessionStorage.clear();
                $log.debug("Clearing sessionStorage for space...");
                try {
                    sessionStorage[urlString] = toJson(results);
                    $log.debug("saved results to localStorage");
                } catch (e) {
                    sessionStorage.clear();
                    $log.debug("Quota exceeded error: the JSON object is too big...");
                }
            }
        };
        return save;
    }
})();
