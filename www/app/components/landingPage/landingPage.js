"use strict";

philoApp.controller('landingPage', ['$rootScope', '$location', 'accessControl', function($rootScope, $location, accessControl) {
    
    var vm = this;
    vm.authorized = $rootScope.authorized;
    vm.dictionary = $rootScope.philoConfig.dictionary;
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