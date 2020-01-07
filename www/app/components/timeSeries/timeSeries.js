(function() {
    "use strict";

    angular
        .module('philoApp')
        .controller('TimeSeriesController', TimeSeriesController);

    function TimeSeriesController($rootScope, $location, accessControl, URL, philoConfig) {
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
        if (typeof($rootScope.formData.year_interval) === "undefined") {
            var urlString = URL.objectToUrlString($rootScope.formData, {
                year_interval: philoConfig.time_series_interval
            });
            $location.url(urlString);
        }

        vm.loading = true;
        vm.percent = 0;

        vm.frequencyType = 'absolute_time';
        vm.toggleFrequency = function(frequencyType) {
            angular.element('#time-series-buttons button').removeClass('active');
            angular.element('#' + frequencyType).addClass('active');
            vm.frequencyType = frequencyType;
        }

    }
})();