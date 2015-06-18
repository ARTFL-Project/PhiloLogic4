"use strict";

philoApp.controller('landingPage', ['$rootScope', '$location', 'accessControl', function($rootScope, $location, accessControl) {
    
    var vm = this;
    if ($rootScope.authorized === true) {
        vm.authorized = true;
    } else {
        $rootScope.accessRequest.then(function(response) {
            $rootScope.authorized = response.data.access;
            vm.authorized = $rootScope.authorized;
        });
    }
	if ($rootScope.philoConfig.landing_page_browsing_type !== 'dictionary') {
        vm.dictionary = false;
    } else {
		vm.dictionary = true;
	}
    $rootScope.report = "landing_page";

    vm.getContent = function(contentType, range) {
        vm.query = {contentType: contentType, range: range};
    }
    
    vm.goToBibliography = function(url) {
        $location.url(url);
    }
}]);

philoApp.animation('.repeated-item', function() {
  return {
    enter : function(element, done) {
        element.velocity('transition.slideLeftIn', {duration: 400})
    },
    leave : function(element, done) {
        element.velocity('transition.slideRightOut', {duration: 400})
    }
  }
});