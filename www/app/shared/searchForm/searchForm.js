philoApp.controller('searchForm', ['$scope', '$rootScope', '$http', '$location', 'radio', 'URL', function($scope, $rootScope, $http, $location, radio, URL) {
    
    $scope.formOpen = false;
    $scope.searchOptionsButton = "Show search options";
    $scope.toggleForm = function() {
        if (!$("#search-elements").length) {
            $scope.formOpen = true;
            $scope.searchOptionsButton = "Hide search options";
        } else {
            $scope.formOpen = false;
            $scope.searchOptionsButton = "Show search options";
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
    
    // Show or hide search bar
    if ($rootScope.report === "concordance" || $rootScope.report === "kwic" || $rootScope.report === "bibliography" || $rootScope.report === "collocation") {
        $scope.showSearchBar = true;
    } else {
        $scope.showSearchBar = false;
    }
    $rootScope.$watch('report', function(newReport) {
        if (newReport === "concordance" || newReport === "kwic" || newReport === "bibliography" || newReport === 'collocation') {
            $scope.showSearchBar = true;
        } else {
            $scope.showSearchBar = false;
        }
    });
    
    $scope.submit = function() {
        $('.ui-autocomplete').hide();
        var extraParams = {start: '0', end: '0'};
        if (typeof($rootScope.formData.q) === "undefined" || $rootScope.formData.q === '') {
            extraParams.report = "bibliography";
        } else if ($rootScope.formData.report === "bibliography" && typeof($rootScope.formData.q) !== "undefined") {
            if ($("#report label.active").length === 0) {
                extraParams.report = "concordance";
            } else {
                extraParams.report = $("#report label.active").attr('id');
            }
        } else if ($rootScope.formData.report === "undefined") {
            extraParams.report = "concordance";
        }
        $scope.formOpen = false;
        $location.url(URL.objectToUrlString($rootScope.formData, extraParams));
    }
}]);