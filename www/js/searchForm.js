philoApp.controller('searchForm', ['$scope', '$rootScope', function($scope, $rootScope) {
    $scope.formOpen = false;
    $scope.changeFormOpen = function(bool) {
        $scope.formOpen = bool;
    }
    $scope.radioClick = function(key, value) {
        $rootScope.formData[key] = value;
    }
    $scope.clearFormData = function() {
        $rootScope.formData = {
            report: $rootScope.philoConfig.search_reports[0],
            method: "proxy",
            results_per_page: "25"
        };
    }
}]);

philoApp.controller('request', ['$scope', '$rootScope', '$http', '$location', 'URL', function($scope, $rootScope, $http, $location, URL) {
    $scope.submit = function() {
        if (typeof($rootScope.formData.q) === "undefined") {
            $scope.formData.report = "bibliography";
        }
        delete $rootScope.formData.start;
        delete $rootScope.formData.end;
        $scope.changeFormOpen(false);
        $rootScope.report = $rootScope.formData.report;
        console.log(URL.objectToString($rootScope.formData, true))
        $location.url(URL.objectToString($rootScope.formData, true));
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

philoApp.controller('timeSeriesInterval', ['$scope', '$rootScope', function($scope, $rootScope) {
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
    $rootScope.formData.year_interval = $rootScope.intervals[0].date;
}]);

philoApp.controller('collocationFilter', ['$scope', '$rootScope', function($scope, $rootScope) {
    $scope.stopwords = philoConfig.stopwords;
    $rootScope.formData.colloc_filter_choice = "frequency";
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