"use strict";

philoApp.controller('collocationCtrl', ['$rootScope', '$http', '$location', 'accessControl', 'URL',
                                        function($rootScope, $http, $location, accessControl, URL) {
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
    
    vm.concordanceFromCollocation = function(url) {
		console.log(url)
        $location.url(url);
    }

}]);