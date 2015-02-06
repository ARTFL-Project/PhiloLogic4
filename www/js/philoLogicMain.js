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
            console.log(array);
            return 'templates/landing_page.html'
        },
        controller: 'landingPage'
      }).
      when('/dispatcher.py?:queryArgs', {
        templateUrl: function(queryArgs) {
            if (queryArgs.report === "concordance" || queryArgs.report === "kwic") {
                var template = 'templates/concordanceKwic.html';
            } else {
                var template = 'templates/landing_page.html'; 
            }
            return template;
        },
        controller: 'concordanceKwicCtrl'
      }).
      otherwise({
        redirectTo: '/'
      });
    $locationProvider.html5Mode({
        enabled: true,
      });
  }]);