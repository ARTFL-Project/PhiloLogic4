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

philoApp.value('formData', {
        report: philoConfig.search_reports[0],
        method: "proxy",
        results_per_page: "25"
});

philoApp.value('concordanceResults', {});

philoApp.value('kwicResults', {});

philoApp.value('timeSeriesResults', {})

philoApp.value('collocationResults', {})

philoApp.value('textObjectCitation', {citation: {}})

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
            if (queryArgs.report === "concordance" || queryArgs.report === "kwic" || queryArgs.report === "bibliography") {
                var template = 'templates/concordanceKwic.html';
            } else if (queryArgs.report === "collocation") {
                var template = 'templates/collocation.html';
            } else if (queryArgs.report === "time_series") {
                var template = 'templates/time_series.html';
            } else {
                var template = 'templates/landing_page.html'; 
            }
            return template;
        }
      }).
      when('/dispatcher.py/:pathInfo*\/', {
        templateUrl: function(queryArgs) {
            var pathInfo = queryArgs.pathInfo.split('/');
            if (pathInfo[pathInfo.length - 1] == "table-of-contents") {
                return 'templates/tableOfContents.html';
            } else {
                return 'templates/textObject.html';
            }
        }
      }).
      otherwise({
        redirectTo: '/'
      });
    $locationProvider.html5Mode({
        enabled: true,
      });
  }]);