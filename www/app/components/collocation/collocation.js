(function() {
    "use strict";

    angular
        .module('philoApp')
        .controller('CollocationController', CollocationController);

    function CollocationController($scope, $rootScope, $http, $location, accessControl, URL) {
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
            $location.url(URL.objectToUrlString($rootScope.formData, {
                report: "bibliography"
            }));
        }

        vm.done = false;
        vm.filterList = false;
        vm.loading = true;
        vm.percent = 0;
        vm.sortedList = {};
        vm.resultsLength = false; // set to false for now

        vm.showFilter = false;
        vm.toggleFilterList = function() {
            if (!vm.showFilter) {
                vm.showFilter = true;
            } else {
                vm.showFilter = false;
            }
        }

        var localParams = angular.copy($location.search());
        vm.resolveCollocateLink = function(word) {
            var q = localParams.q + ' "' + word + '"';
            if ('collocate_distance' in localParams && !(isNaN(localParams.collocate_distance))) {
                var newUrl = URL.objectToUrlString(localParams, {
                    method: "proxy",
                    arg: localParams.collocate_distance,
                    start: "0",
                    end: '0',
                    q: q,
                    report: "concordance",
                    collocation_type: "combined",
                    left: '"' + word + '" ' + localParams.q
                });
            } else {
                var method = "cooc";
                var arg = 6;
                var newUrl = URL.objectToUrlString(localParams, {
                    method: method,
                    arg: arg,
                    start: "0",
                    end: '0',
                    q: q,
                    report: "concordance"
                });
            }
            $location.url(newUrl);
        }

    }
})();
