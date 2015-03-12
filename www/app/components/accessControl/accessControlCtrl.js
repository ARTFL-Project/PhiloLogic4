philoApp.controller('accessControlCtrl', ['$location', '$cookies', '$rootScope', 'request', function($location, $cookies, $rootScope, request) {
	var vm = this;
	
	vm.hostname = window.location.hostname;
	vm.accessInput = {};
	vm.accessDenied = false;
	
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
				$location.url('/');
			} else {
				vm.accessDenied = true;
			}
		});
	}
}]);