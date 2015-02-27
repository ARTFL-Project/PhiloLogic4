philoApp.controller('concordanceKwicCtrl', ['$scope', '$rootScope', '$http', '$location', 'radio', 'URL', function($scope, $rootScope, $http, $location, radio, URL) {
                                                
    $rootScope.formData = angular.copy($location.search());
    if ($rootScope.formData.q === "" && $rootScope.report !== "bibliography") {
        var queryParams = angular.copy($rootScope.formData);
        queryParams.report = "bibliography";
        $location.url(URL.objectToString(queryParams, true));
    }
    if ($rootScope.formData.report !== $('#reports label.active input').attr('id')) {
        $('#report label').removeClass('active');
        $('#' + $rootScope.formData.report).parent().addClass('active');
    }
    
    var oldResults = angular.copy($rootScope.results)
    if ("results" in oldResults) {
        delete $rootScope.results.results;
        $rootScope.results = {description: oldResults.description, results_length: oldResults.results_length};
    } else {
        $rootScope.results = {};
    }
    
    var request = $scope.philoConfig.db_url + '/' + URL.query($rootScope.formData);
    $http.get(request)
        .then(function(results) {
            $rootScope.results = results.data;
        })

    $scope.showFullBiblio = function(event) {
        target = $(event.currentTarget).find('.full_biblio');
        target.addClass('show');
    }
    $scope.hideFullBiblio= function(event) {
        target = $(event.currentTarget).find('.full_biblio');
        target.removeClass('show');
    }
    $rootScope.frequencyResults = [];
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