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

philoApp.directive('metadataFields', ['$rootScope', function($rootScope) {
    var buildMetadata = function() {
        var metadataFields = [];
        for (var i=0; i < $rootScope.philoConfig.metadata.length; i++) {
            var metadata = $rootScope.philoConfig.metadata[i];
            var metadataObject = {};
            metadataObject.value = metadata;
            if (metadata in $rootScope.philoConfig.metadata_aliases) {
                metadataObject.label = $rootScope.philoConfig.metadata_aliases[metadata];
            } else {
                metadataObject.label = metadata;
            }
            metadataObject.example = $rootScope.philoConfig.search_examples[metadata];
            metadataFields.push(metadataObject);
        }
        return metadataFields
    }
    return {
        templateUrl: 'app/shared/searchForm/metadataFields.html',
        link: function(scope, element, attrs) {
            scope.metadataFields = buildMetadata();
        }
    }
}]);

philoApp.directive('collocationOptions', ['$rootScope', function($rootScope) {
    return {
        templateUrl: 'app/shared/searchForm/collocationOptions.html',
        link: function(scope, element, attrs) {
            scope.collocWordNum = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
            $rootScope.formData.word_num = scope.collocWordNum[4];
            scope.stopwords = $rootScope.philoConfig.stopwords;
            $rootScope.formData.colloc_filter_choice = "frequency";
            scope.wordFiltering = [25, 50, 75, 100, 125, 150, 175, 200];
            $rootScope.formData.filter_frequency = scope.wordFiltering[3];
        }
    }
}]);

philoApp.directive('timeSeriesOptions', ['$rootScope', function($rootScope) {
    var buildOptions = function() {
        var options = {1: "Year", 10: "Decade", 50: "Half Century", 100: "Century"};
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
            $rootScope.formData.year_interval = scope.timeSeriesIntervals[0].date;
        }
    }
}]);

philoApp.directive('resultsPerPage', ['$rootScope', function($rootScope) {
    return {
        templateUrl: 'app/shared/searchForm/resultsPerPage.html',
        link: function() {
            $rootScope.results_per_page = "25";
        }
    }
}]);

philoApp.directive('fixedSearchBar', ['$rootScope', '$timeout', function($rootScope, $timeout) {
    var affixSearchBar = function(scope) {
        if ($('#description').length) {
            $('#fixed-search').affix({
                offset: {
                top: function() {
                    return (this.top = $('#description').offset().top)
                    },
                bottom: function() {
                    return (this.bottom = $('#footer').outerHeight(true))
                  }
                }
            });
            $('#fixed-search').on('affix.bs.affix', function() {
                $(this).addClass('fixed');
                $(this).css({'opacity': 1, "pointer-events": "auto"});
            });
            $('#fixed-search').on('affixed-top.bs.affix', function() {
                $(this).css({'opacity': 0, "pointer-events": "none"});
                setTimeout(function() {
                   $(this).removeClass('fixed'); 
                });
            });
            $("#top-of-page").click(function() {
                $("body").velocity('scroll', {duration: 800, easing: 'easeOutCirc', offset: 0});
            });
        }
    }
    return {
        restrict: 'E',
        templateUrl: 'app/shared/searchForm/fixedSearchBar.html',
        link: function(scope, element, attrs) {
                $timeout(function() {
                    affixSearchBar(scope);
                }); 
            }
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
        };
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