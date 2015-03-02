"use strict";

philoApp.controller('collocationCtrl', ['$scope', '$rootScope', '$http', '$location', 'radio', 'URL',
                                            function($scope, $rootScope, $http, $location, radio, URL) {
    $rootScope.formData = angular.copy($location.search());
    if ($rootScope.formData.q === "" && $rootScope.report !== "bibliography") {
        $location.url(URL.objectToUrlString($rootScope.formData, {report: "bibliography"}));
    }
    
    $scope.done = false;
    $scope.filterList = false;
    $scope.percent = 0;
    $scope.sortedLists = {};
    $scope.resultsLength = false; // set to false for now
    
    $scope.showFilter = false;
    $scope.toggleFilterList = function() {
        if (!$scope.showFilter) {
            $scope.showFilter = true;
        } else {
            $scope.showFilter = false;
        }
    }
    
    $scope.concordanceFromCollocation = function(url) {
        url = url.replace($rootScope.philoConfig.db_url, '');
        $location.url(url);
    }

}]);