"use strict"

philoApp.controller('tableOfContents', ['$scope', '$rootScope', '$http', '$location', '$routeParams', 'URL', 'textObjectCitation',
                                            function($scope, $rootScope, $http, $location, $routeParams, URL, textObjectCitation) {
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
            console.log(JSON.stringify(data))
        })
        .error(function(data, status, headers, config) {
            console.log("Error", status, headers)
        });

}]);