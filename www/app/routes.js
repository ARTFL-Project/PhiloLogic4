(function() {
    "use strict";

    angular
        .module("philoApp")
        .config(philoRoutes);

    function philoRoutes($routeProvider, $locationProvider) {
        $routeProvider.
        when("/", {
            templateUrl: function() {
                return "app/components/landingPage/landing_page.html";
            },
            controller: "LandingPageController",
            controllerAs: "lp"
        }).
        when("/query?:queryArgs", {
            templateUrl: function(queryArgs) {
                var report = queryArgs.report;
                if (report === "concordance" || report === "kwic" || report === "bibliography" || report === "concordance_from_collocation" || report === "word_property_filter") {
                    var template = "app/components/concordanceKwic/concordanceKwic.html";
                } else if (report === "collocation") {
                    template = "app/components/collocation/collocation.html";
                } else if (report === "time_series") {
                    template = "app/components/timeSeries/timeSeries.html";
                } else {
                    template = "app/components/landingPage/landing_page.html";
                }
                return template;
            }
        }).
        when("/navigate/:pathInfo*\/", {
            templateUrl: function(queryArgs) {
                var pathInfo = queryArgs.pathInfo.split("/");
                if (pathInfo[pathInfo.length - 1] === "table-of-contents") {
                    return "app/components/tableOfContents/tableOfContents.html";
                } else {
                    return "app/components/textNavigation/textNavigation.html";
                }
            }
        }).
        when("/access-control", {
            templateUrl: "app/components/accessControl/accessControl.html"
        }).
        otherwise({
            redirectTo: "/"
        });
        $locationProvider.html5Mode({
            enabled: true
        });
    }

})()
