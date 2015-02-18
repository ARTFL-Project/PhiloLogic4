"use strict";

philoApp.controller('timeSeriesCtrl', ['$scope', '$rootScope', '$http', '$location', 'radio', 'progressiveLoad', 'URL',
                                            function($scope, $rootScope, $http, $location, radio, progressiveLoad, URL) {
    $rootScope.formData = angular.copy($location.search());
    if ($rootScope.formData.q === "" && $rootScope.report !== "bibliography") {
        $rootScope.formData.report = "bibliography";
        $location.url(URL.objectToString($rootScope.formData, true));
    }
    
    radio.setReport('time_series');
    
    $scope.percent = 0;
    $scope.interval = parseInt($rootScope.formData.year_interval);
    
}]);