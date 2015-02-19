philoApp.directive('searchReports', ['$rootScope', function($rootScope) {
    var reportSetUp = function(reportSelected) {
        reportSelected = angular.copy(reportSelected);
        if (reportSelected === "bibliography" || reportSelected === "landing_page") {
            reportSelected = $rootScope.philoConfig.search_reports[0];
        }
        var reports = [];
        for (var i=0; i < $rootScope.philoConfig.search_reports.length; i++) {
            var value = $rootScope.philoConfig.search_reports[i];
            var label = value.replace('_', ' ');
            var status = '';
            if (reportSelected === value) {
                status = 'active';
            }
            reports.push({value: value, label: label, status: status});
        }
        return reports
    }
    var reportChange = function(report) {
        $rootScope.formData.report = report;
        return reportSetUp(report);
    }
    return {
        restrict: 'E',
        templateUrl: 'app/shared/searchForm/searchReports.html',
        link: function(scope, element, attrs) {
            scope.reports = reportSetUp($rootScope.formData.report); // First report is active
            setTimeout(function() { // Workaround to make sure the reports are loaded properly before being displayed
                $('#search').show();
            }, 250);
            scope.reportChange = reportChange;
            scope.report = $rootScope.formData.report;
            scope.$watch('report', function(report) {
                var reportToSelect = angular.copy(report);
                if (reportToSelect === "bibliography") {
                    reportToSelect = "concordance"
                }
                scope.reports = reportChange(reportToSelect);
            });
        }
    }
}]);