"use strict"

philoApp.controller('tableOfContents', ['$scope', '$rootScope', '$http', '$location', '$routeParams', 'URL', function($scope, $rootScope, $http, $location, $routeParams, URL) {
    
    $rootScope.report = "table_of_contents";
    $scope.textObjectURL = $routeParams;
    var tempValue = $scope.textObjectURL.pathInfo.split('/');
    tempValue.pop();
    $scope.philoID = tempValue.join(' ');
    var request = URL.report({report: "table_of_contents", philo_id: $scope.philoID});
    $http.get(request).then(function(response) {
        $scope.tocObject = response.data;
    });
    
    $scope.teiHeader = false;
    $scope.showHeader = function() {
        if (typeof($scope.teiHeader) === "string") {
            $scope.teiHeader = false;
        } else {
            var request = URL.script({script: "get_header.py", philo_id: $scope.philoID});
            $http.get(request)
            .then(function(response) {
                $scope.teiHeader = response.data;
            });
        }
    }

}]);