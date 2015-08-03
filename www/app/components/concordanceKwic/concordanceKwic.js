philoApp.controller('concordanceKwicCtrl', ['$rootScope', '$location', 'accessControl', 'request', 'URL',
                                            function($rootScope, $location, accessControl, request, URL) {
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
    if ($rootScope.report !== "bibliography") {
        if ($rootScope.formData.q === "" || typeof($rootScope.formData.q) === 'undefined') {
            var urlString = URL.objectToUrlString($rootScope.formData, {report: "bibliography"});
            $location.url(urlString);
        }        
    }
    vm.loading = true;
	vm.resultsLength = 0;
    vm.resultsPromise = request.report($rootScope.formData);
	    
    vm.frequencyResults = [];
    
    vm.selectedFacet = '';
    vm.selectFacet = function(facetObj) {
        vm.selectedFacet = facetObj;
    }
    
    vm.removeSidebar = function() {
        vm.frequencyResults = [];
        $('#selected-sidebar-option').data('interrupt', true);
        vm.selectedFacet = '';
    }
}]);