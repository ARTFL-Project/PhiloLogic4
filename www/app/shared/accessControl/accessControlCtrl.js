(function() {
    "use strict";

    angular
        .module("philoApp")
        .controller('AccessController', AccessController);


    function AccessController($window, $http, $cookies, $rootScope, $route, accessControl, request) {
    	var vm = this;
    	vm.hostname = $window.location.hostname;
    	vm.accessInput = {};
    	vm.accessDenied = false;

    	vm.clientIp = false; // don't show anything before retrieval
    	$http.get('http://api.ipify.org?format=json').then(function(response) {
    		vm.clientIp = response.data.ip;
    	});

    	vm.submit = function() {
    		var username = encodeURIComponent(vm.accessInput.username);
    		var password = encodeURIComponent(vm.accessInput.password);
    		request.script({
    			script: 'access_request.py',
    			username: username,
    			password: password
    		}).then(function(response) {
    			var authorization = response.data;
    			if (authorization.access) {
    				$rootScope.authorized = true;
    				$route.reload();
    			} else {
    				vm.accessDenied = true;
    			}
    		});
    	}
    }
})();
