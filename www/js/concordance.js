philoApp.controller('concordanceCtrl', ['$scope', '$rootScope', 'biblioCriteria', function($scope, $rootScope, biblioCriteria) {
    $scope.$watch(function() {
        return $rootScope.queryParams;
        }, function() {
      $rootScope.biblio = biblioCriteria.build($rootScope.queryParams);
    }, true);
    $scope.removeMetadata = biblioCriteria.remove;
}]);


