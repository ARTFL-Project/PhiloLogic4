var philoApp = angular.module('philoApp', ['ngRoute', 'ngTouch', 'ngSanitize', 'angular-velocity']);

philoApp.controller('philoMain', ['$rootScope', '$scope', '$location', 'textNavigationValues', function($rootScope, $scope, $location, textNavigationValues) {
    $rootScope.philoConfig = philoConfig;
    $rootScope.formData = {
        report: philoConfig.search_reports[0],
        method: "proxy"
        };
    $rootScope.results = {};
    $rootScope.report = philoReport;
    $scope.$on('$locationChangeStart', function() {
        $rootScope.report = $location.search().report;
    });
    //$rootScope.$watch('report', function(report) { // Doesn't recognize textNavigation
    //    if (report !== 'textNavigation') {
    //        console.log(report)
    //        textNavigationValues.citation = {};
    //        textNavigationValues.tocObject = false;
    //        textNavigationValues.navBar = false;
    //    }
    //});
}]);

philoApp.config(['$routeProvider', '$locationProvider',
  function($routeProvider, $locationProvider) {
    $routeProvider.
      when('/', {
        templateUrl: function(array) {
            return 'app/components/landingPage/landing_page.html'
        },
        controller: 'landingPage'
      }).
      when('/dispatcher.py?:queryArgs', {
        templateUrl: function(queryArgs) {
            var report = queryArgs.report;
            if (report === "concordance" || report === "kwic" || report === "bibliography" || report === "concordance_from_collocation" || report === "word_property_filter") {
                var template = 'app/components/concordanceKwic/concordanceKwic.html';
            } else if (report === "collocation") {
                var template = 'app/components/collocation/collocation.html';
            } else if (report === "time_series") {
                var template = 'app/components/timeSeries/timeSeries.html';
            } else {
                var template = 'app/components/landingPage/landing_page.html'; 
            }
            return template;
        }
      }).
      when('/dispatcher.py/:pathInfo*\/', {
        templateUrl: function(queryArgs) {
            var pathInfo = queryArgs.pathInfo.split('/');
            if (pathInfo[pathInfo.length - 1] == "table-of-contents") {
                return 'app/components/tableOfContents/tableOfContents.html';
            } else {
                return 'app/components/textNavigation/textNavigation.html';
            }
        }
      }).
      otherwise({
        redirectTo: '/'
      });
    $locationProvider.html5Mode({
        enabled: true
      });
  }]);