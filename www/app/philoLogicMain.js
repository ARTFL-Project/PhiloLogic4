(function() {
    "use strict";

    angular
        .module("philoApp")
        .config(['$compileProvider', function($compileProvider) {
            $compileProvider.debugInfoEnabled(false);
        }])
        .controller("PhiloMainController", PhiloMainController);


    function PhiloMainController($scope, $rootScope, $location, philoConfig, accessControl,
        textNavigationValues, descriptionValues, request, sortedKwicCached) {

        var vm = this;

        $rootScope.philoConfig = philoConfig;

        // Check access control
        if (!philoConfig.access_control) {
            $rootScope.authorized = true;
        } else {
            $rootScope.accessRequest = request.script({
                script: "access_request.py"
            });
        }

        $rootScope.report = $location.search().report || "landing_page";
        $rootScope.formData = {
            report: $rootScope.report,
            method: "proxy"
        };

        var urlChange = $rootScope.$on("$locationChangeStart", function() {
            var paths = $location.path().split("/").filter(Boolean);
            if (paths[0] === "query") {
                $rootScope.report = $location.search().report;
            } else if (paths[0] === "navigate") {
                if (paths[paths.length - 1] === "table-of-contents") {
                    $rootScope.report = "table-of-contents";
                } else {
                    $rootScope.report = "textNavigation";
                }
            } else {
                $rootScope.report = "landing_page";
            }
            if ($rootScope.report !== "textNavigation") {
                textNavigationValues.citation = {};
                textNavigationValues.tocElements = false;
                textNavigationValues.tocOpen = false;
                textNavigationValues.navBar = false;
            }
            if ($rootScope.report !== "kwic") {
                sortedKwicCached.results = null;
                sortedKwicCached.queryObject = null;
            }
        });

        vm.backToHome = function() {
            $scope.$broadcast("backToHome");
            $location.url("/");
        };
    }
})();
