philoApp.controller('accessControlCtrl', ['$window', '$http', '$cookies', '$rootScope', 'request', function($window, $http, $cookies, $rootScope, request) {
	var vm = this;
	
	vm.hostname = window.location.hostname;
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
			if (response.data === "authorized") {
				$cookies[$rootScope.philoConfig.db_url] = "authorized";
				$window.location.href = $rootScope.philoConfig.db_url;
			} else {
				vm.accessDenied = true;
			}
		});
	}
}]);