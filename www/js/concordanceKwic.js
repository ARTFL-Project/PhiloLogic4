philoApp.controller('concordanceKwicCtrl', ['$scope', '$rootScope', 'biblioCriteria', function($scope, $rootScope, biblioCriteria) {
    $scope.$watch(function() {
        return $rootScope.queryParams;
        }, function() {
      $rootScope.biblio = biblioCriteria.build($rootScope.queryParams);
    }, true);
    $scope.removeMetadata = biblioCriteria.remove;
}]);

philoApp.controller('concordanceKwicSwitcher', ['$scope', '$rootScope', '$http', '$location', 'URL', function($scope, $rootScope, $http, $location, URL) {
    $scope.switchTo = function(report) {
        console.log(report)
        $rootScope.queryParams.report = report;
        var request = {
            method: "GET",
            url: $rootScope.philoConfig.db_url + '/dispatcher.py?' + URL.objectToString($rootScope.queryParams)
        }
        $rootScope.results = {};
        $rootScope.report = report;
        $http(request)
        .success(function(data, status, headers, config) {
            $rootScope.results = data;
            $location.url(URL.objectToString($rootScope.queryParams, true));
        })
        .error(function(data, status, headers, config) {
            console.log("Error", status, headers)
        });
    }
}]);

philoApp.controller('kwicCtrl', ['$scope', '$rootScope', function($scope, $rootScope) {
    $scope.initializePos = function(start, index) {
        var currentPos = start + index;
        var currentPosLength = currentPos.toString().length;
        var endPosLength = $rootScope.results.description.end.toString().length;
        var spaces = endPosLength - currentPosLength + 1;
        return currentPos + '.' + Array(spaces).join('&nbsp');
    } 
}]);



