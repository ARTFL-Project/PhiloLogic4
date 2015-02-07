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
      when('/dispatcher.py/:pathInfo*\/', {
        templateUrl: function(queryArgs) {
            var pathInfo = queryArgs.pathInfo.split('/');
            console.log(pathInfo)
            if (pathInfo[pathInfo.length - 1] == "table-of-contents") {
                console.log('toc')
            } else {
                console.log(queryArgs)
            }
            return 'templates/textObject.html';
        },
        controller: 'textObjectNavigation'
      }).
      otherwise({
        redirectTo: '/'
      });
    $locationProvider.html5Mode({
        enabled: true,
      });
  }]);