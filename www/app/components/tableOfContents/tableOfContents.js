"use strict"

philoApp.controller('tableOfContents', ['$rootScope', '$http', '$location', '$routeParams', 'accessControl', 'URL', "request",
                                        function($rootScope, $http, $location, $routeParams, accessControl, URL, request) {
    
    var vm = this;
    vm.authorized = $rootScope.authorized; // cannot be blocked specifically if access to database
    vm.textObjectURL = $routeParams;
    var tempValue = vm.textObjectURL.pathInfo.split('/');
    tempValue.pop();
    vm.philoID = tempValue.join(' ');
    var formData = {report: "table_of_contents", philo_id: vm.philoID};
    request.report(formData).then(function(promise) {
        vm.tocObject = promise.data;
    });
    
    vm.teiHeader = false;
    vm.showHeader = function() {
        if (typeof(vm.teiHeader) === "string") {
            vm.teiHeader = false;
        } else {
            var UrlString = {script: "get_header.py", philo_id: vm.philoID};
            request.script(UrlString).then(function(promise) {
                vm.teiHeader = promise.data;
            });
        }
    }

}]);