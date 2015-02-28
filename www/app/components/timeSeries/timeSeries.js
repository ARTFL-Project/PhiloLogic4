"use strict";

philoApp.controller('timeSeriesCtrl', ['$scope', '$rootScope', '$location', 'radio', 'URL', function($scope, $rootScope, $location, radio, URL) {
    $rootScope.formData = angular.copy($location.search());
    if ($rootScope.formData.q === "" && $rootScope.report !== "bibliography") {
        $rootScope.formData.report = "bibliography";
        $location.url(URL.objectToString($rootScope.formData, true));
    }
    if (typeof($rootScope.formData.year_interval) === "undefined") {
        $rootScope.formData.year_interval = $rootScope.philoConfig.time_series_intervals[0];
        $location.url(URL.objectToString($rootScope.formData));
    }
    
    $scope.percent = 0;
    $scope.interval = parseInt($rootScope.formData.year_interval);
    
    $scope.frequencyType = 'absolute_time';
    $scope.toggleFrequency = function(frequencyType) {
        $('#time-series-buttons button').removeClass('active');
        $('#' + frequencyType).addClass('active');
        console.log(frequencyType)
        $scope.frequencyType = frequencyType;
    }
    
}]);