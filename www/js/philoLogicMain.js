philoApp.controller('philoMain', ['$rootScope', '$scope', '$location', function($rootScope, $scope, $location) {
    $rootScope.report = philoReport;
    $rootScope.philoConfig = philoConfig;
    $rootScope.queryParams = {}
    $location.path(philoReport)
}]);

philoApp.factory('biblioCriteria', function() {
        return {
            build: function(queryParams) {
                var queryArgs = angular.copy(queryParams);
                var biblio = []
                if (queryArgs.report === "time_series") {
                    delete queryParams.date;
                }
                for (var i=0; i < philoConfig.metadata.length; i++) {
                    var k = philoConfig.metadata[i];
                    var v = queryArgs[k];
                    if (v) {
                        if (queryArgs.report !== "concordance_from_collocation") {
                            var close_icon = '<span class="glyphicon glyphicon-remove-circle remove_metadata" data-metadata="' + k + '"></span>';
                        } else {
                            var close_icon = ""
                        }
                        if (k in philoConfig.metadata_aliases) {
                            k = philoConfig.metadataAliases[k];
                        }
                        var htmlContent = '<span class="biblio-criteria">' + k.charAt(0).toUpperCase() + k.slice(1) + ': <b>' + v + '</b> ' + close_icon + '</span>';
                        biblio.push(htmlContent);
                    }
                }
                console.log(biblio)
                if (biblio.length) {
                    return biblio.join(' ');
                } else {
                    return "None";
                }
            }
        }
});