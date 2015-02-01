philoApp.controller('searchForm', ['$scope', function($scope) {
    $scope.formData = {
        report: $scope.philoConfig.search_reports[0],
        method: "proxy",
        results_per_page: "25",
        format: "json"
        };
    $scope.formOpen = false;
    $scope.changeFormOpen = function(bool) {
        $scope.formOpen = bool;
    }
    $scope.radioClick = function(key, value) {
        $scope.formData[key] = value;
    }
    $scope.clearFormData = function() {
        $scope.formData = {
            report: $scope.philoConfig.search_reports[0],
            method: "proxy",
            results_per_page: "25",
            format: "json"
        };
    }
}]);

philoApp.controller('request', ['$scope', '$rootScope', '$http', '$location', 'URL', function($scope, $rootScope, $http, $location, URL) {
    $scope.submit = function() {
        if (typeof($scope.formData.q) === "undefined") {
            $scope.formData.report = "bibliography";
        }
        var request = {
            method: "GET",
            url: $scope.philoConfig.db_url + '/dispatcher.py?' + URL.objectToString($scope.formData)
        }
        $scope.changeFormOpen(false);
        $rootScope.queryParams = $scope.formData;
        $rootScope.results = {};
        $rootScope.report = $scope.formData.report;
        $http(request)
        .success(function(data, status, headers, config) {
            $rootScope.results = data;
            $location.url(URL.objectToString($scope.formData, true));
        })
        .error(function(data, status, headers, config) {
            console.log("Error", status, headers)
        });
    }
}]);

philoApp.controller('showSearchForm', ['$scope', function($scope) {
    $scope.toggle = function() {
        if (!$("#search-elements").length) {
            $scope.changeFormOpen(true);
        } else {
            $scope.changeFormOpen(false);
        }  
   }
}]);

philoApp.controller('searchMetadata', ['$scope', function($scope) {
    $scope.formData = $scope.$parent.formData;
    $scope.reportSelected = $scope.$parent.reportSelected;
    $scope.metadataFields = {};
    for (var i=0; i < philoConfig.metadata.length; i++) {
        var metadata = philoConfig.metadata[i];
        $scope.metadataFields[metadata] = {}
        if (metadata in philoConfig.metadata_aliases) {
            $scope.metadataFields[metadata].value = philoConfig.metadata_aliases[metadata];
        } else {
            $scope.metadataFields[metadata].value = metadata;
        }
        $scope.metadataFields[metadata].example = philoConfig.search_examples[metadata];
    }
}]);

philoApp.controller('timeSeriesInterval', ['$scope', function($scope) {
    $scope.formData = $scope.$parent.formData;
    $scope.reportSelected = $scope.$parent.reportSelected;
    var options = {1: "Year", 10: "Decade", 50: "Half Century", 100: "Century"};
    $scope.intervals = [];
    for (var i=0; i < philoConfig.time_series_intervals.length; i++) {
        var interval = {
            date: philoConfig.time_series_intervals[i],
            alias: options[philoConfig.time_series_intervals[i]]
        };
        $scope.intervals.push(interval);
    }
    $scope.formData.year_interval = $scope.intervals[0].date;
}]);

philoApp.controller('collocationFilter', ['$scope', function($scope) {
    $scope.stopwords = philoConfig.stopwords;
    $scope.formData.colloc_filter_choice = "frequency";
}]);

philoApp.animation('.overlay-fadeOut', function() {
    return {
        enter: function(element, done) {
            $(element).velocity({
                opacity: 0.3
            }, {duration: 300, complete: done});
        },
        leave: function(element, done) {
            $(element).velocity({
                opacity: 0
            }, {duration: 300, complete: done});
        }
    };
});

philoApp.animation('.report-fade', function() {
    return {
        enter: function(element, done) {
            $(element).velocity({
                opacity: 1
            }, {duration: 200, complete: done});
        },
        leave: function(element, done) {
            $(element).velocity({
                opacity: 0
            }, {duration: 200, complete: done});
        }
    };
});


//var queryString = function(formData, url) {
//    var obj = angular.copy(formData);
//    if (url) {
//        var report = obj.report;
//        delete obj.report;
//        delete obj.format;
//    }
//    var str = [];
//    for (var p in obj) {
//        var k = p, 
//            v = obj[k];
//        str.push(angular.isObject(v) ? qs(v, k) : (k) + "=" + encodeURIComponent(v));
//    }
//    if (url) {
//        return report + '/' + str.join('&');
//    } else {
//        return str.join("&");
//    }
//}