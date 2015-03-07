"use strict";

philoApp.controller('timeSeriesCtrl', ['$scope', '$rootScope', '$location', 'radio', 'URL', function($scope, $rootScope, $location, radio, URL) {
    $rootScope.formData = angular.copy($location.search());
    if ($rootScope.formData.q === "" && $rootScope.report !== "bibliography") {
        $location.url(URL.objectToUrlString($rootScope.formData, {report: "bibliography"}));
    }
    if (typeof($rootScope.formData.year_interval) === "undefined") {
        var urlString = URL.objectToUrlString($rootScope.formData, {year_interval: $rootScope.philoConfig.time_series_intervals[0]});
        $location.url(urlString);
    }
    
    $scope.percent = 0;
    $scope.interval = parseInt($rootScope.formData.year_interval);
    
    $scope.frequencyType = 'absolute_time';
    $scope.toggleFrequency = function(frequencyType) {
        $('#time-series-buttons button').removeClass('active');
        $('#' + frequencyType).addClass('active');
        $scope.frequencyType = frequencyType;
    }
    
    $scope.hoverChart = function($event, title) {
        var element = $($event.currentTarget);
        element.popover('toggle')
    }
    
}]);