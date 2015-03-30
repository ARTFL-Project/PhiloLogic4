"use strict";

philoApp.controller('collocationCtrl', ['$rootScope', '$http', '$location', 'accessControl', 'URL',
                                        function($rootScope, $http, $location, accessControl, URL) {
    
    var vm = this;
    vm.authorized = $rootScope.access.collocation;
    $rootScope.formData = angular.copy($location.search());
    if ($rootScope.formData.q === "" && $rootScope.report !== "bibliography") {
        $location.url(URL.objectToUrlString($rootScope.formData, {report: "bibliography"}));
    }
    
    vm.done = false;
    vm.filterList = false;
    vm.loading = true;
    vm.percent = 0;
    vm.sortedLists = {};
    vm.resultsLength = false; // set to false for now
    
    vm.showFilter = false;
    vm.toggleFilterList = function() {
        if (!vm.showFilter) {
            vm.showFilter = true;
        } else {
            vm.showFilter = false;
        }
    }
    
    vm.concordanceFromCollocation = function(word, count, direction) {
        var url = URL.objectToUrlString($location.search(), {report: 'concordance_from_collocation', collocate: word, collocate_num: count, direction: direction});
        console.log(url)
        $location.url(url);
    }

}]);