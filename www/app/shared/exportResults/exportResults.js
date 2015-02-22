philoApp.controller('exportResults', ['$scope', '$location', function($scope, $location) {
    $scope.exportResults = function() {
        var exportLink = window.location.href + "&content_type=json";
        window.open(exportLink);
    }
}])