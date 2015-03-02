philoApp.controller('concordanceKwicCtrl', ['$scope', '$rootScope', '$location', 'request', 'URL', function($scope, $rootScope, $location, request, URL) {
                                                
    $rootScope.formData = angular.copy($location.search());
    if ($rootScope.formData.q === "" && $rootScope.report !== "bibliography") {
        var queryParams = angular.copy($rootScope.formData);
        queryParams.report = "bibliography";
        $location.url(URL.objectToString(queryParams, true));
    }
    
    var promise = request.query($rootScope.formData);
    promise.then(function(results) {
        $scope.results = results.data;
        $scope.description = $scope.results.description;
    })

    $scope.showFullBiblio = function(event) {
        target = $(event.currentTarget).find('.full_biblio');
        target.addClass('show');
    }
    $scope.hideFullBiblio = function(event) {
        target = $(event.currentTarget).find('.full_biblio');
        target.removeClass('show');
    }
    $rootScope.frequencyResults = []; // TODO: move this out of rootScope
    $scope.resultsContainerWidth = "";
    $scope.sidebarWidth = '';
    $scope.$watch('frequencyResults', function(frequencyResults) {
        if (frequencyResults.length > 0) {
            $scope.resultsContainerWidth = "col-xs-8";
            $scope.sidebarWidth = "col-xs-4";
        } else {
            $scope.resultsContainerWidth = "";
            $scope.sidebarWidth = "";
        }
    });
    
    $scope.goToPage = function(start, end) {
        $rootScope.formData.start = start;
        $rootScope.formData.end = end;
        $("body").velocity('scroll', {duration: 200, easing: 'easeOutCirc', offset: 0, complete: function() {
            $rootScope.results = {};
        }});
        $location.url(URL.objectToString($rootScope.formData, true));
    }
    
    $scope.switchTo = function(report) {
        $rootScope.formData.report = report;
        $('#report label').removeClass('active');
        $('#' + report).addClass('active');
        $location.url(URL.objectToString($rootScope.formData, true));
    }
    
    $scope.selectedFacet = '';
    $scope.selectFacet = function(facetObj) {
        $scope.selectedFacet = facetObj;
    }
    
    $scope.removeSidebar = function() {
        $scope.frequencyResults = [];
        $('#selected-sidebar-option').data('interrupt', true);
        $scope.selectedFacet = '';
    }
}]);