"use strict"

philoApp.controller('tableOfContents', ['$rootScope', '$http', '$location', '$routeParams', 'accessControl', 'URL', "request",
                                        function($rootScope, $http, $location, $routeParams, accessControl, URL, request) {
    var vm = this;
    if ($rootScope.authorized === true) {
        vm.authorized = true;
    } else {
        $rootScope.accessRequest.then(function(response) {
            $rootScope.authorized = response.data.access;
            vm.authorized = $rootScope.authorized;
        });
    }
    vm.textObjectURL = $routeParams;
    var tempValue = vm.textObjectURL.pathInfo.split('/');
    tempValue.pop();
    vm.philoID = tempValue.join(' ');
    var formData = {report: "table_of_contents", philo_id: vm.philoID};
    vm.loading = true
    request.report(formData).then(function(promise) {
        vm.loading = false;
        vm.tocObject = promise.data;
    }).catch(function(response) {
		vm.loading = false;
	});
    
    vm.headerButton = "Show Header";
    vm.teiHeader = false;
    vm.showHeader = function() {
        if (typeof(vm.teiHeader) === "string") {
            vm.teiHeader = false;
            vm.headerButton = "Show Header";
        } else {
            var UrlString = {script: "get_header.py", philo_id: vm.philoID};
            request.script(UrlString).then(function(promise) {
                vm.teiHeader = promise.data;
                vm.headerButton = "Hide Header";
            });
        }
    }
    
    vm.displayLimit = 50;
    vm.getMoreItems = function() {
        vm.displayLimit += 200;
    }

}]);