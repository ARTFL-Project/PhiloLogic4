"use strict";

philoApp.controller('timeSeriesCtrl', ['$rootScope', '$location', 'accessControl', 'URL', function($rootScope, $location, accessControl, URL) {
    var vm = this;
    if ($rootScope.authorized === true) {
        vm.authorized = true;
    } else {
        $rootScope.accessRequest.then(function(response) {
            $rootScope.authorized = response.data.access;
            vm.authorized = $rootScope.authorized;
        });
    }
    $rootScope.formData = angular.copy($location.search());
    if ($rootScope.formData.q === "" && $rootScope.report !== "bibliography") {
        $location.url(URL.objectToUrlString($rootScope.formData, {report: "bibliography"}));
    }
    if (typeof($rootScope.formData.year_interval) === "undefined") {
        var urlString = URL.objectToUrlString($rootScope.formData, {year_interval: 10});
        $location.url(urlString);
    }
    
    vm.loading = true;
    vm.percent = 0;
    
    vm.frequencyType = 'absolute_time';
    vm.toggleFrequency = function(frequencyType) {
        $('#time-series-buttons button').removeClass('active');
        $('#' + frequencyType).addClass('active');
        vm.frequencyType = frequencyType;
    }
    
}]);