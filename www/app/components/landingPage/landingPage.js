"use strict";

philoApp.controller('landingPage', ['$rootScope', '$location', function($rootScope, $location) {
    
    var vm = this;
    vm.dictionary = $rootScope.philoConfig.dictionary;
    $rootScope.report = "landing_page";

    vm.getContent = function(contentType, range) {
        vm.query = {contentType: contentType, range: range};
    }
    
    vm.goToBibliography = function(url) {
        $location.url(url);
    }
}]);