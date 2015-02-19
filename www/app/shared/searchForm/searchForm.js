philoApp.controller('searchForm', ['$scope', '$rootScope', '$http', '$location', 'radio', 'URL', 'searchFormConfig', function($scope, $rootScope, $http, $location, radio, URL, searchFormConfig) {
    $scope.formOpen = false;
    $scope.toggleForm = function() {
        if (!$("#search-elements").length) {
            $scope.formOpen = true;
        } else {
            $scope.formOpen = false;
        }  
    }
    
    // Handle radio clicks to workaround clash between angular and bootstrap
    $scope.radioClick = radio.click;
    
    $scope.clearFormData = function() {
        $rootScope.formData = {
            report: $rootScope.philoConfig.search_reports[0],
            method: "proxy",
            results_per_page: "25"
        };
    }
    
    // Load searchFormConfig variables into scope
    $scope.metadataFields = searchFormConfig.metadataFields;
    $scope.collocWordNum = searchFormConfig.collocWordNum;
    $rootScope.formData.word_num = $scope.collocWordNum[4];
    $scope.stopwords = $rootScope.philoConfig.stopwords;
    $rootScope.formData.colloc_filter_choice = "frequency";
    $scope.wordFiltering = searchFormConfig.wordFiltering;
    $rootScope.formData.filter_frequency = $scope.wordFiltering[3];
    $scope.timeSeriesIntervals = searchFormConfig.timeSeriesIntervals;
    $rootScope.formData.year_interval = $scope.timeSeriesIntervals[0].date;

    $scope.submit = function() {
        if (typeof($rootScope.formData.q) === "undefined" || $rootScope.formData.q === '') {
            $rootScope.formData.report = "bibliography";
        } else if ($scope.formData.report === "bibliography" && typeof($rootScope.formData.q) !== "undefined") {
            $rootScope.formData.report = $("#report label.active input").attr('id');
        }
        delete $rootScope.formData.start;
        delete $rootScope.formData.end;
        $scope.formOpen = false;
        $rootScope.report = $rootScope.formData.report;
        console.log(URL.objectToString($rootScope.formData, true))
        $location.url(URL.objectToString($rootScope.formData, true));
    }
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