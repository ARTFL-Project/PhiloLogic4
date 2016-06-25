(function() {
    "use strict";

    angular
        .module("philoApp", ["ngRoute", "ngTouch", "ngSanitize", "ngCookies", "angular-velocity", "ui.utils", "infinite-scroll"]);

    getConfig().then(bootstrapApplication);

    function getConfig() {
        var initInjector = angular.injector(["ng"]);
        var $http = initInjector.get("$http");

        return $http.get("scripts/get_web_config.py").then(function(response) {
            angular
                .module('philoApp')
                .constant("philoConfig", response.data);
        }, function(errorResponse) {
            // Handle error case
        });
    }

    function bootstrapApplication() {
        angular.element(document).ready(function() {
            angular.bootstrap(document, ['philoApp']);
        });
    }
})();
