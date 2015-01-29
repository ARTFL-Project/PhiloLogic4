philoApp.controller('concordanceCtrl', ['$scope', '$rootScope', 'biblioCriteria', function($scope, $rootScope, biblioCriteria) {
    $scope.biblioCriteria = biblioCriteria.build($rootScope.queryParams);
}]);


