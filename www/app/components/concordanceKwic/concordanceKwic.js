(function() {
    "use strict";

    angular
        .module('philoApp')
        .controller('ConcordanceKwicController', ConcordanceKwicController);

    function ConcordanceKwicController($rootScope, $location, accessControl, request, URL, facetedBrowsing, dictionaryLookup, philoConfig) {
        var vm = this;
        if ($rootScope.authorized === true) {
            vm.authorized = true;
        } else {
            $rootScope.accessRequest.then(function(response) {
                $rootScope.authorized = response.data.access;
                vm.authorized = $rootScope.authorized;
            });
        }
        $rootScope.formData = angular.copy($location.search());
        if ($rootScope.report !== "bibliography") {
            if ($rootScope.formData.q === "" || typeof($rootScope.formData.q) === 'undefined') {
                var urlString = URL.objectToUrlString($rootScope.formData, {
                    report: "bibliography"
                });
                $location.url(urlString);
            }
        }
        vm.showFacetedBrowsing = facetedBrowsing.show;
        vm.loading = true;
        vm.resultsLength = 0;
        vm.resultsPromise = request.report($rootScope.formData);

        vm.frequencyResults = [];

        vm.selectedFacet = '';
        vm.selectFacet = function(facetObj) {
            vm.selectedFacet = facetObj;
        }
        vm.showFacets = function() {
            vm.showFacetedBrowsing = true;
            facetedBrowsing.show = true;
        }

        vm.removeSidebar = function() {
            vm.frequencyResults = [];
            angular.element('#selected-sidebar-option').data('interrupt', true);
            vm.selectedFacet = '';
        }

        vm.dicoLookup = function(event, year) {
            dictionaryLookup.evaluate(event, year);
        }
        vm.evaluateWidth = function() {
            var returnValue = 'col-sm-12';
            if (philoConfig.facets.length > 0) {
                if (vm.showFacetedBrowsing == true) {
                    returnValue = 'col-sm-8'
                }
            }
            return returnValue
        }
    }
})();