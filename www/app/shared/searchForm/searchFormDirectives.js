(function () {
    "use strict";

    angular
        .module("philoApp")
        .directive('searchForm', searchForm)
        .directive('searchReports', searchReports)
        .directive('searchTerms', searchTerms)
        .directive('searchMethods', searchMethods)
        .directive('metadataFields', metadataFields)
        .directive('collocationOptions', collocationOptions)
        .directive('timeSeriesOptions', timeSeriesOptions)
        .directive('resultsPerPage', resultsPerPage)
        .directive('autocompleteTerm', autocompleteTerm)
        .directive('autocompleteMetadata', autocompleteMetadata)
        .directive('sortResults', sortResults);


    function searchForm($rootScope) {
        return {
            templateUrl: 'app/shared/searchForm/searchForm.html',
            replace: true,
            scope: false,
            link: function (scope) {
                scope.approximateValues = [50, 60, 70, 80, 90];
                scope.approximateValue = "How approximate?";
                scope.selectApproximate = function (value) {
                    scope.approximateValue = value;
                    $rootScope.formData.approximate_ratio = value;
                }
            }
        };
    }

    function searchReports($rootScope, $location) {
        var reportChange = function (report) {
            if (report === 'landing_page') {
                report = $rootScope.philoConfig.search_reports[0];
            }
            $rootScope.formData.report = report;
            var reports = [];
            for (var i = 0; i < $rootScope.philoConfig.search_reports.length; i++) {
                var value = $rootScope.philoConfig.search_reports[i];
                var label = value.replace('_', ' ');
                reports.push({
                    value: value,
                    label: label
                });
            }
            return reports
        }
        return {
            restrict: 'E',
            templateUrl: 'app/shared/searchForm/searchReports.html',
            replace: true,
            link: function (scope, element, attrs) {
                scope.reportChange = reportChange;
                scope.$watch('report', function (report) {
                    var reportToSelect = angular.copy(report);
                    if (reportToSelect === "bibliography") {
                        reportToSelect = "concordance";
                    } else if (reportToSelect === "textNavigation" || reportToSelect === "table-of-contents") {
                        reportToSelect = "concordance";
                    } else if (typeof (reportToSelect) == "undefined") {
                        reportToSelect = $location.search().report || "concordance";
                    }
                    scope.reports = reportChange(reportToSelect);
                });
            }
        };
    }

    function searchTerms() {
        return {
            templateUrl: 'app/shared/searchForm/searchTerms.html',
            replace: true
        }
    }

    function searchMethods() {
        return {
            templateUrl: 'app/shared/searchForm/searchMethods.html',
            replace: true
        }
    }

    function metadataFields(philoConfig, $rootScope) {
        var buildMetadata = function (scope, fields) {
            var metadataFields = [];
            for (var i = 0; i < fields.length; i++) {
                var metadata = fields[i];
                var metadataObject = {};
                metadataObject.value = metadata;
                if (metadata in scope.philoConfig.metadata_aliases) {
                    metadataObject.label = scope.philoConfig.metadata_aliases[metadata];
                } else {
                    metadataObject.label = metadata[0].toUpperCase() + metadata.slice(1);
                }
                metadataObject.example = scope.philoConfig.search_examples[metadata];
                metadataFields.push(metadataObject);
            }
            return metadataFields
        }
        return {
            templateUrl: 'app/shared/searchForm/metadataFields.html',
            replace: true,
            link: function (scope, element, attrs) {
                scope.dropdownValues = {};
                scope.selectedDropdownValue = {};
                for (var metadata in philoConfig.metadata_dropdown_values) {
                    scope.dropdownValues[metadata] = [];
                    var dropdownValue = philoConfig.metadata_dropdown_values[metadata];
                    if (typeof($rootScope.formData[metadata]) == 'undefined' || $rootScope.formData[metadata].length == 0) {
                        scope.selectedDropdownValue[metadata] = 'select';
                    }
                    for (var i = 0; i < dropdownValue.length; i++) {
                        var quotedValue = dropdownValue[i].value;
                        if (typeof($rootScope.formData[metadata]) != 'undefined' && $rootScope.formData[metadata] == quotedValue) {
                            scope.selectedDropdownValue[metadata] = dropdownValue[i].label;
                        }
                        scope.dropdownValues[metadata].push({
                            label: dropdownValue[i].label,
                            value: quotedValue
                        });
                    }
                }
                scope.metadataDropdownChoice = function(metadata, field) {
                    $rootScope.formData[metadata] = field.value;
                    scope.selectedDropdownValue[metadata] = field.label;
                }
                if (!attrs.field && !attrs.exclude) {
                    scope.metadataFields = buildMetadata(scope, scope.philoConfig.metadata);
                    scope.head = false;
                    scope.exclude = false;
                } else if (attrs.field === "head") {
                    var head = [];
                    for (var i = 0; i < scope.philoConfig.metadata.length; i++) {
                        if (scope.philoConfig.metadata[i] === 'head') {
                            head.push(scope.philoConfig.metadata[i]);
                            break
                        }
                    }
                    scope.head = true;
                    scope.exclude = false;
                    scope.metadataFields = buildMetadata(scope, ["head"]);
                } else if (attrs.exclude === "head") {
                    var fields = [];
                    for (var i = 0; i < scope.philoConfig.metadata.length; i++) {
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
    }

    function collocationOptions($rootScope) {
        return {
            templateUrl: 'app/shared/searchForm/collocationOptions.html',
            replace: true,
            link: function (scope, element, attrs) {
                scope.stopwords = $rootScope.philoConfig.stopwords;
                if (!'colloc_filter_choice' in $rootScope.formData || typeof ($rootScope.formData.colloc_filter_choice) === 'undefined') {
                    $rootScope.formData.colloc_filter_choice = "frequency";
                }
                if (!'filter_frequency' in $rootScope.formData || typeof ($rootScope.formData.filter_frequency) === 'undefined') {
                    $rootScope.formData.filter_frequency = 100;
                }
            }
        }
    }

    function timeSeriesOptions($rootScope, philoConfig) {
        return {
            templateUrl: 'app/shared/searchForm/timeSeriesOptions.html',
            replace: true,
            link: function () {
                if (!$rootScope.formData.year_interval) {
                    $rootScope.formData.year_interval = philoConfig.time_series_interval;
                }
            }
        }
    }

    function resultsPerPage() {
        return {
            templateUrl: 'app/shared/searchForm/resultsPerPage.html'
        }
    }

    function autocompleteTerm($rootScope) {
        var autocomplete = function (element) {
            element.autocomplete({
                source: 'scripts/autocomplete_term.py',
                minLength: 2,
                "dataType": "json",
                focus: function (event, ui) {
                    var q = ui.item.label.replace(/<\/?span[^>]*?>/g, '');
                    return false;
                },
                select: function (event, ui) {
                    var q = ui.item.label.replace(/<\/?span[^>]*?>/g, '');
                    element.val(q);
                    $rootScope.formData.q = q;
                    return false;
                }
            }).data("ui-autocomplete")._renderItem = function (ul, item) {
                var term = item.label.replace(/^[^<]*/g, '');
                return angular.element("<li></li>")
                    .data("item.autocomplete", item)
                    .append(term)
                    .appendTo(ul);
            }
        }
        return {
            restrict: 'A',
            link: function (scope, element) {
                autocomplete(element);
            }
        }
    }

    function autocompleteMetadata($rootScope) {
        var autocomplete = function (element, field) {
            element.autocomplete({
                source: 'scripts/autocomplete_metadata.py?field=' + field,
                minLength: 2,
                timeout: 1000,
                dataType: "json",
                focus: function (event, ui) {
                    var q = ui.item.label.replace(/<\/?span[^>]*?>/g, '');
                    q = q.replace(/ CUTHERE /, ' ');
                    return false;
                },
                select: function (event, ui) {
                    var q = ui.item.label.replace(/<\/?span[^>]*?>/g, '');
                    q = q.split(/(\||NOT)/);
                    q[q.length - 1] = q[q.length - 1].replace(/.*CUTHERE /, '');
                    q[q.length - 1] = '\"' + q[q.length - 1].replace(/^\s*/g, '') + '\"';
                    q = q.join(' ').replace(/""/g, '"');
                    element.val(q);
                    $rootScope.formData[field] = q
                    return false;
                }
            }).data("ui-autocomplete")._renderItem = function (ul, item) {
                var term = item.label.replace(/.*(?=CUTHERE)CUTHERE /, '');
                return angular.element("<li></li>")
                    .data("item.autocomplete", item)
                    .append(term)
                    .appendTo(ul);
            };
        }
        return {
            restrict: 'A',
            link: function (scope, element, attrs) {
                autocomplete(element, attrs.id);
            }
        }
    }

    function sortResults($rootScope, philoConfig) {
        return {
            templateUrl: 'app/shared/searchForm/sortResults.html',
            link: function (scope) {
                if ("sort_order" in $rootScope.formData && $rootScope.formData.sort_order.length >= 1) {
                    var label = []
                    if (typeof($rootScope.formData.sort_order) == "string") {
                        if ($rootScope.formData.sort_order in philoConfig.metadata_aliases) {
                            label = philoConfig.metadata_aliases[$rootScope.formData.sort_order];
                        } else {
                            label = $rootScope.formData.sort_order;
                        }
                    } else {
                        for (var j = 0; j < $rootScope.formData.sort_order.length; j += 1) {
                            if ($rootScope.formData.sort_order[j] in philoConfig.metadata_aliases) {
                                label.push(philoConfig.metadata_aliases[$rootScope.formData.sort_order[j]]);
                            } else {
                                label.push($rootScope.formData.sort_order[j]);
                            }
                        }
                        label = label.join(', ')
                    }
                    scope.selectedSortValues = label;
                    if (scope.selectedSortValues == "rowid") {
                        scope.selectedSortValues = "select";
                    }
                } else {
                    scope.selectedSortValues = "select";
                }


                scope.sortValues = [{
                    value: [],
                    label: "select"
                }];
                for (var i = 0; i < philoConfig.concordance_biblio_sorting.length; i += 1) {
                    var sortValue = philoConfig.concordance_biblio_sorting[i];
                    if (typeof(sortValue) == 'string') {
                        sortValue = [sortValue];
                    }
                    var label = [];
                    for (var j = 0; j < sortValue.length; j += 1) {
                        if (sortValue[j] in philoConfig.metadata_aliases) {
                            label.push(philoConfig.metadata_aliases[sortValue[j]]);
                        } else {
                            label.push(sortValue[j]);
                        }
                    }
                    var value = {
                        label: label.join(', '),
                        value: sortValue
                    }
                    scope.sortValues.push(value);
                }
                scope.sortChoice = function (value) {
                    $rootScope.formData.sort_order = value.value;
                    scope.selectedSortValues = value.label;
                    if (scope.selectedSortValues == "rowid") {
                        scope.selectedSortValues = "select";
                    }
                }
            }
        }
    }

})();