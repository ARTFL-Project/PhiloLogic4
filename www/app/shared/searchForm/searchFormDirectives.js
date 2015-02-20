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

philoApp.directive('fixedSearchBar', function() {
    var affixSearchBar = function(scope) {
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
    return {
        restrict: 'E',
        templateUrl: 'app/shared/searchForm/fixedSearchBar.html',
        link: function(scope, element, attrs) {
                affixSearchBar(scope);
                }
    }
});

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
        //var field = element.attr('id');
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
            console.log(attrs.id)
            autocomplete(element, attrs.id); 
        }
    }
}]);