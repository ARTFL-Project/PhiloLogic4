"use strict"

philoApp.controller('tableOfContents', ['$scope', '$rootScope', '$http', '$location', '$routeParams', 'URL', 'textObjectCitation',
                                            function($scope, $rootScope, $http, $location, $routeParams, URL, textObjectCitation) {
    
    $rootScope.report = "table_of_contents";
    $scope.textObjectURL = $routeParams;
    var tempValue = $scope.textObjectURL.pathInfo.split('/');
    tempValue.pop();
    $scope.philoID = tempValue.join(' ');
    var request = {
        method: "GET",
        url: $rootScope.philoConfig.db_url + '/' + URL.query({
            report: "table_of_contents",
            philo_id: $scope.philoID})
    }
    $http(request)
        .success(function(data, status, headers, config) {
            $scope.tocObject = data;
        })
        .error(function(data, status, headers, config) {
            console.log("Error", status, headers)
        });
    
    $scope.teiHeader = false;
    $scope.showHeader = function() {
        if (typeof($scope.teiHeader) === "string") {
            $scope.teiHeader = false;
        } else {
            var request = {
                method: "GET",
                url: $rootScope.philoConfig.db_url + '/' + URL.query({
                    script: "get_header.py",
                    philo_id: $scope.philoID
                })
            }
            $http(request)
            .success(function(data, status, headers, config) {
                $scope.teiHeader = data;
            })
            .error(function(data, status, headers, config) {
                console.log("Error", status, headers)
            });
        }
    }

}]);