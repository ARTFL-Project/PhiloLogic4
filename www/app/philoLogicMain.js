var philoApp = angular.module('philoApp', ['ngRoute', 'ngTouch', 'ngSanitize', 'angular-velocity']);

philoApp.controller('philoMain', ['$rootScope', '$scope', '$location', function($rootScope, $scope, $location) {
    $rootScope.report = philoReport;
    $rootScope.philoConfig = philoConfig;
    $rootScope.formData = {
        report: philoConfig.search_reports[0],
        method: "proxy",
        results_per_page: "25"
        };
    $rootScope.results = {}
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
            if (queryArgs.report === "concordance" || queryArgs.report === "kwic" || queryArgs.report === "bibliography") {
                var template = 'app/components/concordanceKwic/concordanceKwic.html';
            } else if (queryArgs.report === "collocation") {
                var template = 'app/components/collocation/collocation.html';
            } else if (queryArgs.report === "time_series") {
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
                return 'app/components/textObject/textObject.html';
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