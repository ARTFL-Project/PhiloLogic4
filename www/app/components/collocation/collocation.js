"use strict";

philoApp.controller('collocationCtrl', ['$scope', '$rootScope', '$http', '$location', 'accessControl', 'URL',
                                        function($scope, $rootScope, $http, $location, accessControl, URL) {
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
    
	var localParams = angular.copy($location.search());
    vm.resolveCollocateLink = function(word) {
		var q = localParams.q + ' "' + word + '"';
		if (typeof(localParams.word_num) === 'undefined' || isNaN(localParams.word_num)) {
            var method = "cooc";
			var arg = 6
        } else {
			var method = "proxy";
			var arg = localParams.word_num;
		}
		var newUrl = URL.objectToUrlString(localParams,
										   {
											method: method,
											arg: arg,
											start: "0",
											end: '0',
											q: q,
											report: "concordance"
										   });
		$location.url(newUrl);
	}

}]);