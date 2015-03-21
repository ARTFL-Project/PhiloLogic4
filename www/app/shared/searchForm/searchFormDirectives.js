philoApp.directive('searchForm', ['$rootScope', function($rootScope) {
    return {
        templateUrl: 'app/shared/searchForm/searchForm.html',
        scope: false
    }
}]);

philoApp.directive('searchReports', ['$rootScope', '$location', function($rootScope, $location) {
    var reportChange = function(report) {
        $rootScope.formData.report = report;
        var reports = [];
        for (var i=0; i < $rootScope.philoConfig.search_reports.length; i++) {
            var value = $rootScope.philoConfig.search_reports[i];
            var label = value.replace('_', ' ');
            reports.push({value: value, label: label, status: status});
        }
        return reports
    }
    return {
        restrict: 'E',
        templateUrl: 'app/shared/searchForm/searchReports.html',
        link: function(scope, element, attrs) {
            scope.reportChange = reportChange;
            scope.$watch('report', function(report) {
                var reportToSelect = angular.copy(report);
                if (reportToSelect === "bibliography") {
                    reportToSelect = "concordance";
                } else if (reportToSelect === "textNavigation" || reportToSelect === "table-of-contents") {
                    reportToSelect = "concordance";
                } else if (typeof(reportToSelect) == "undefined") {
                    reportToSelect = $location.search().report || "concordance";
                }
                scope.reports = reportChange(reportToSelect);
            });
        }
    }
}]);

philoApp.directive('searchTerms', function() {
    return {
        templateUrl: 'app/shared/searchForm/searchTerms.html'
    }
});

philoApp.directive('searchMethods', ['$rootScope', function($rootScope) {
    return {
        templateUrl: 'app/shared/searchForm/searchMethods.html',
    }
}]);

philoApp.directive('metadataFields', function() {
    var buildMetadata = function(scope, fields) {
        var metadataFields = [];
        for (var i=0; i < fields.length; i++) {
            var metadata = fields[i];
            var metadataObject = {};
            metadataObject.value = metadata;
            if (metadata in scope.philoConfig.metadata_aliases) {
                metadataObject.label = scope.philoConfig.metadata_aliases[metadata];
            } else {
                metadataObject.label = metadata;
            }
            metadataObject.example = scope.philoConfig.search_examples[metadata];
            metadataFields.push(metadataObject);
        }
        return metadataFields
    }
    return {
        templateUrl: 'app/shared/searchForm/metadataFields.html',
        link: function(scope, element, attrs) {
            if (!attrs.field && !attrs.exclude) {
                scope.metadataFields = buildMetadata(scope, scope.philoConfig.metadata);
                scope.head = false;
                scope.exclude = false;
            } else if (attrs.field === "head") {
                var head = [];
                for (var i=0; i < scope.philoConfig.metadata.length; i++) {
                    if (scope.philoConfig.metadata[i] === 'head') {
                        head.push(scope.philoConfig.metadata[i]);
                        break
                    }
                }
                scope.head = true;
                scope.exclude = false;
                scope.metadataFields = buildMetadata(scope, head);
            } else if (attrs.exclude === "head") {
                var fields = [];
                for (var i=0; i < scope.philoConfig.metadata.length; i++) {
                    if (scope.philoConfig.metadata[i] !== 'head') {
                        fields.push(scope.philoConfig.metadata[i]);
                    }
                }
                scope.head = false;
                scope.exclude = true;
                scope.metadataFields = buildMetadata(scope, fields);
            }
        }
    }
});

philoApp.directive('collocationOptions', ['$rootScope', function($rootScope) {
    return {
        templateUrl: 'app/shared/searchForm/collocationOptions.html',
        link: function(scope, element, attrs) {
            scope.collocWordNum = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10'];
            if (!'word_num' in $rootScope.formData || typeof($rootScope.formData.word_num) === 'undefined') {
                $rootScope.formData.word_num = scope.collocWordNum[4];
            }
            scope.stopwords = $rootScope.philoConfig.stopwords;
            if (!'colloc_filter_choice' in $rootScope.formData || typeof($rootScope.formData.colloc_filter_choice) === 'undefined') {
                $rootScope.formData.colloc_filter_choice = "frequency";
            }
            scope.wordFiltering = ['25', '50', '75', '100', '125', '150', '175', '200'];
            if (!'filter_frequency' in $rootScope.formData || typeof($rootScope.formData.filter_frequency) === 'undefined') {
                $rootScope.formData.filter_frequency = scope.wordFiltering[3];
            }
        }
    }
}]);

philoApp.directive('timeSeriesOptions', ['$rootScope', function($rootScope) {
    var buildOptions = function() {
        var options = {1: "Year", '10': "Decade", '50': "Half Century", '100': "Century"};
        var intervals = [];
        for (var i=0; i < $rootScope.philoConfig.time_series_intervals.length; i++) {
            var interval = {
                date: $rootScope.philoConfig.time_series_intervals[i],
                alias: options[$rootScope.philoConfig.time_series_intervals[i]]
            };
            intervals.push(interval);
        }
        return intervals
    }
    return {
        templateUrl: 'app/shared/searchForm/timeSeriesOptions.html',
        link: function(scope, element, attrs) {
            scope.timeSeriesIntervals = buildOptions();
            if (typeof($rootScope.formData.year_interval) === 'undefined') {
                $rootScope.formData.year_interval = scope.timeSeriesIntervals[0].date;
            }
        }
    }
}]);

philoApp.directive('resultsPerPage', ['$rootScope', function($rootScope) {
    return {
        templateUrl: 'app/shared/searchForm/resultsPerPage.html',
    }
}]);

philoApp.directive('autocompleteTerm', ['$rootScope', function($rootScope) {
    var autocomplete = function(element) {
        element.autocomplete({
            source: 'scripts/autocomplete_term.py',
            minLength: 2,
            "dataType": "json",
            focus: function( event, ui ) {
                var q = ui.item.label.replace(/<\/?span[^>]*?>/g, '');
                return false;
            },
            select: function( event, ui ) {
                var q = ui.item.label.replace(/<\/?span[^>]*?>/g, '');
                element.val(q);
                $rootScope.formData.q = q;
                return false;
            }
        }).data("ui-autocomplete")._renderItem = function (ul, item) {
            var term = item.label.replace(/^[^<]*/g, '');
            return $("<li></li>")
                .data("item.autocomplete", item)
                .append(term)
                .appendTo(ul);
        }
    }
    return {
        restrict: 'A',
        link: function(scope, element) {
            autocomplete(element); 
        }
    }
}]);

philoApp.directive('autocompleteMetadata', ['$rootScope', function($rootScope) {
    var autocomplete = function(element, field) {
        element.autocomplete({
            source: 'scripts/autocomplete_metadata.py?field=' + field,
            minLength: 2,
            timeout: 1000,
            dataType: "json",
            focus: function( event, ui ) {
                var q = ui.item.label.replace(/<\/?span[^>]*?>/g, '');
                q = q.replace(/ CUTHERE /, ' ');
                return false;
            },
            select: function( event, ui ) {
                var q = ui.item.label.replace(/<\/?span[^>]*?>/g, '');
                q = q.split('|');
                q[q.length - 1] = q[q.length - 1].replace(/.*CUTHERE /, '');
                q[q.length-1] = '\"' + q[q.length-1].replace(/^\s*/g, '') + '\"'; 
                q = q.join('|').replace(/""/g, '"');
                element.val(q);
                $rootScope.formData[field] = q
                return false;
            }
        }).data("ui-autocomplete")._renderItem = function (ul, item) {
            var term = item.label.replace(/.*(?=CUTHERE)CUTHERE /, '');
            return $("<li></li>")
                .data("item.autocomplete", item)
                .append(term)
                .appendTo(ul);
        };
    }
    return {
        restrict: 'A',
        link: function(scope, element, attrs) {
            autocomplete(element, attrs.id); 
        }
    }
}]);