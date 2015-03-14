philoApp.controller('concordanceKwicCtrl', ['$rootScope', '$location', 'accessControl', 'request', 'URL',
                                            function($rootScope, $location, accessControl, request, URL) {
    
    var vm = this;
    vm.authorized = $rootScope.access.concordance;
    $rootScope.formData = angular.copy($location.search());
    if ($rootScope.formData.q === "" && $rootScope.report !== "bibliography") {
        var urlString = URL.objectToUrlString($rootScope.formData, {report: "bibliography"});
        $location.url(urlString);
    }
    
    request.report($rootScope.formData).then(function(results) {
        vm.results = results.data;
        vm.description = vm.results.description;
    });
    
    vm.frequencyResults = [];
    
    vm.goToPage = function(start, end) {
        $rootScope.formData.start = start;
        $rootScope.formData.end = end;
        $("body").velocity('scroll', {duration: 200, easing: 'easeOutCirc', offset: 0, complete: function() {
            $rootScope.results = {};
        }});
        $location.url(URL.objectToUrlString($rootScope.formData));
    }
    
    vm.switchTo = function(report) {
        $('#report label').removeClass('active');
        $('#' + report).addClass('active');
        $location.url(URL.objectToUrlString($rootScope.formData, {report: report}));
    }
    
    vm.selectedFacet = '';
    vm.selectFacet = function(facetObj) {
        vm.selectedFacet = facetObj;
    }
    
    vm.removeSidebar = function() {
        vm.frequencyResults = [];
        $('#selected-sidebar-option').data('interrupt', true);
        vm.selectedFacet = '';
    }
}]);