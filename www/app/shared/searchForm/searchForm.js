(function() {
    "use strict";

    angular
        .module("philoApp")
        .controller('SearchFormController', SearchFormController)

    function SearchFormController($scope, $rootScope, $http, $location, radio, URL) {
        var vm = this;
        vm.formOpen = false;
        vm.searchOptionsButton = "Show search options";
        vm.toggleForm = function() {
            if (!angular.element("#search-elements").length) {
                vm.formOpen = true;
                vm.searchOptionsButton = "Hide search options";
            } else {
                vm.formOpen = false;
                vm.searchOptionsButton = "Show search options";
            }
        }

        // Handle radio clicks to workaround clash between angular and bootstrap
        vm.radioClick = radio.click;

        vm.clearFormData = function() {
            $rootScope.formData = {
                report: $rootScope.philoConfig.search_reports[0],
                method: "proxy",
                results_per_page: "25",
                stopwords: $rootScope.philoConfig.stopwords,
                wordFiltering: ['25', '50', '75', '100', '125', '150', '175', '200'],
                collocWordNum: ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10'],
                year_interval: 10
            };
            vm.toggleForm();
        }

        vm.submit = function() {
            angular.element('.ui-autocomplete').hide();
            var extraParams = {start: '0', end: '0'};
            if (typeof($rootScope.formData.q) === "undefined" || $rootScope.formData.q === '') {
                extraParams.report = "bibliography";
            } else if ($rootScope.formData.report === "bibliography" && typeof($rootScope.formData.q) !== "undefined") {
                if (angular.element("#report label.active").length === 0) {
                    extraParams.report = "concordance";
                } else {
                    extraParams.report = angular.element("#report label.active").attr('id');
                }
            } else if ($rootScope.formData.report === "undefined") {
                extraParams.report = "concordance";
            }
            vm.formOpen = false;
            vm.searchOptionsButton = "Show search options";
            $location.url(URL.objectToUrlString($rootScope.formData, extraParams));
        }

    	$scope.$on('backToHome', function() {
    		vm.formOpen = false;
            vm.searchOptionsButton = "Show search options";
    	})
    }
})();
