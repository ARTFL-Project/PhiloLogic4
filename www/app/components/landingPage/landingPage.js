"use strict";

philoApp.controller('landingPage', ['$rootScope', '$scope', '$location', function($rootScope, $scope, $location) {
    $scope.dictionary = $scope.philoConfig.dictionary;
    $rootScope.report = "landing_page";
    
    $scope.query = "";
    $scope.getContent = function(contentType, range) {
        $scope.contentType = contentType;
        $scope.range = range;
        $scope.resultGroups = [];
        $scope.query = contentType + range;
    }
    
    $scope.goToBibliography = function(url) {
        $location.url(url);
    }
}]);