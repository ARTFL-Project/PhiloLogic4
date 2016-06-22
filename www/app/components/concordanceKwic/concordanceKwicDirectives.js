(function() {
    "use strict";

    angular
        .module('philoApp')
        .directive('concordance', concordance)
        .directive('kwic', kwic)
        .directive('bibliography', bibliography)
        .directive('resultsDescription', resultsDescription)
        .directive('concordanceKwicSwitch', concordanceKwicSwitch)
        .directive('pages', pages);


    function concordance($rootScope, $http, request) {
        return {
            templateUrl: 'app/components/concordanceKwic/concordance.html',
            replace: true,
            link: function(scope) {
                scope.concKwic.resultsPromise.then(function(results) {
                    scope.results = results.data;
                    scope.concKwic.description = angular.extend({}, scope.results.description, {
                        resultsLength: scope.results.results_length
                    });
                    scope.concKwic.loading = false;
                }).catch(function(response) {
                    scope.results = {};
                    scope.concKwic.description = {};
                    scope.concKwic.loading = false;
                });
                scope.moreContext = function($event, resultNumber) {
                    var clickTarget = angular.element($event.currentTarget);
                    var element = clickTarget.parents('.philologic-occurrence').find('.philologic_context');
                    var defaultElement = element.find('.default-length');
                    var moreContextElement = element.find('.more-length');
                    if (defaultElement.css('display') == "none") {
                        moreContextElement.hide();
                        defaultElement.velocity('fadeIn', {
                            duration: 300
                        });
                        clickTarget.text("More");
                    } else {
                        if (moreContextElement.children().length == 0) {
                            var extraParams = {
                                script: 'get_more_context.py',
                                hit_num: resultNumber
                            };
                            request.script($rootScope.formData, extraParams).then(function(response) {
                                defaultElement.hide();
                                moreContextElement.html(response.data).promise().done(function() {
                                    angular.element(this).velocity('fadeIn', {
                                        duration: 300
                                    });
                                });
                                clickTarget.text("Less");
                            });
                        } else {
                            defaultElement.hide();
                            moreContextElement.velocity('fadeIn', {
                                duration: 300
                            });
                            clickTarget.text("Less");
                        }
                    }
                }
            }
        }
    }

    function kwic($rootScope, $location, $http, URL, request, defaultDiacriticsRemovalMap, descriptionValues, sortedKwicCached) {
        var mergeLists = function(list1, list2) {
            for (var i = 0; i < list2.length; i += 1) {
                list1.push(list2[i]);
            }
            return list1;
        }
        var recursiveLookup = function(scope, queryParams, hitsDone) {
            request.script(queryParams, {
                    hits_done: hitsDone
                })
                .then(function(response) {
                    var hitsDone = response.data.hits_done;
                    if (scope.sortedResults.length === 0) {
                        scope.sortedResults = response.data.results;
                    } else {
                        scope.sortedResults = mergeLists(scope.sortedResults, response.data.results)
                    }
                    if (hitsDone < descriptionValues.resultsLength) {
                        recursiveLookup(scope, queryParams, hitsDone);
                    } else {
                        queryParams.start = '0';
                        queryParams.end = '0';
                        sortedKwicCached.results = scope.sortedResults;
                        sortedKwicCached.queryObject = angular.extend({}, queryParams, {
                            first: queryParams.first_kwic_sorting_option,
                            second: queryParams.second_kwic_sorting_option,
                            third: queryParams.third_kwic_sorting_option
                        })
                        getKwicResults(scope, hitsDone);
                        scope.concKwic.loading = false;
                    }
                });
        }
        var getKwicResults = function(scope, hitsDone) {
            var start = parseInt(scope.formData.start);
            if (typeof(scope.formData.results_per_page) === 'undefined') {
                var end = start + 25;
            } else {
                var end = start + parseInt(scope.formData.results_per_page);
            }
            $http.post('scripts/get_sorted_kwic.py',
                    angular.toJson({
                        results: scope.sortedResults,
                        hits_done: hitsDone,
                        query_string: URL.objectToString($location.search()),
                        start: start,
                        end: end,
                        sort_keys: [scope.formData.first_kwic_sorting_option, scope.formData.second_kwic_sorting_option, scope.formData.third_kwic_sorting_option]
                    })
                )
                .then(function(response) {
                    scope.results = response.data;
                });
        }
        var initializePos = function(results, index) {
            var start = results.description.start;
            var currentPos = start + index;
            var currentPosLength = currentPos.toString().length;
            var endPos = start + parseInt($rootScope.formData.results_per_page || 25);
            var endPosLength = endPos.toString().length;
            var spaces = endPosLength - currentPosLength + 1;
            return currentPos + '.' + Array(spaces).join('&nbsp');
        }
        return {
            templateUrl: 'app/components/concordanceKwic/kwic.html',
            link: function(scope) {

                scope.initializePos = initializePos;
                scope.showFullBiblio = function(event) {
                    var target = angular.element(event.currentTarget).find('.full_biblio');
                    target.addClass('show');
                }

                scope.hideFullBiblio = function(event) {
                    var target = angular.element(event.currentTarget).find('.full_biblio');
                    target.removeClass('show');
                }

                // Sorting fields
                var sortingFields = [{
                    label: 'None',
                    field: ''
                }, {
                    label: 'searched term(s)',
                    field: 'q'
                }, {
                    label: 'words to the left',
                    field: 'left'
                }, {
                    label: 'words to the right',
                    field: 'right'
                }];
                var sortKeys = {
                    "q": "searched term(s)",
                    "left": 'words to the left',
                    "right": 'words to the right'
                }
                for (var i = 0; i < $rootScope.philoConfig.kwic_metadata_sorting_fields.length; i += 1) {
                    var field = $rootScope.philoConfig.kwic_metadata_sorting_fields[i];
                    if (field in scope.philoConfig.metadata_aliases) {
                        var label = scope.philoConfig.metadata_aliases[field];
                        sortingFields.push({
                            label: label,
                            field: field
                        });
                        sortKeys[field] = label;
                    } else {
                        sortingFields.push({
                            label: field[0].toUpperCase() + field.slice(1),
                            field: field
                        });
                        sortKeys[field] = field[0].toUpperCase() + field.slice(1);
                    }
                }
                scope.sortingFields = [sortingFields, sortingFields, sortingFields];
                scope.sortingSelection = [];
                if (typeof(scope.formData.first_kwic_sorting_option) !== 'undefined') {
                    scope.sortingSelection.push(sortKeys[scope.formData.first_kwic_sorting_option])
                }
                if (typeof(scope.formData.second_kwic_sorting_option) !== 'undefined') {
                    scope.sortingSelection.push(sortKeys[scope.formData.second_kwic_sorting_option])
                }
                if (typeof(scope.formData.third_kwic_sorting_option) !== 'undefined') {
                    scope.sortingSelection.push(sortKeys[scope.formData.third_kwic_sorting_option])
                }
                if (scope.sortingSelection.length === 0) {
                    scope.sortingSelection = ["None", "None", "None"]
                } else if (scope.sortingSelection.length === 1) {
                    scope.sortingSelection.push('None');
                    scope.sortingSelection.push("None");
                } else if (scope.sortingSelection.length === 2) {
                    scope.sortingSelection.push("None");
                }
                scope.updateSortingSelection = function(index, selection) {
                    scope.sortingSelection[index] = selection.label;
                    if (index === 0) {
                        if (selection.label == "None") {
                            delete $rootScope.formData.first_kwic_sorting_option;
                        } else {
                            $rootScope.formData.first_kwic_sorting_option = selection.field;
                        }
                    } else if (index == 1) {
                        if (selection.label == "None") {
                            delete $rootScope.formData.second_kwic_sorting_option;
                        } else {
                            $rootScope.formData.second_kwic_sorting_option = selection.field;
                        }
                    } else {
                        if (selection.label == "None") {
                            delete $rootScope.formData.third_kwic_sorting_option;
                        } else {
                            $rootScope.formData.third_kwic_sorting_option = selection.field;
                        }
                    }
                }
                scope.sortResults = function() {
                    if (scope.concKwic.description.resultsLength < 30000) {
                        var urlString = URL.objectToUrlString($rootScope.formData);
                        $location.url(urlString);
                    } else {
                        alert("For performance reasons, you cannot sort KWIC reports of more than 30,000 results. Please narrow your query to filter results.")
                    }
                }

                if (typeof(scope.formData.first_kwic_sorting_option) !== 'undefined' && scope.formData.first_kwic_sorting_option !== "") {
                    scope.concKwic.resultsPromise.then(function(results) { // Rerun normal KWIC query since this could be a reload
                        scope.concKwic.description = angular.extend({}, results.data.description, {
                            resultsLength: results.data.results_length
                        });
                        var queryParams = $location.search();
                        queryParams.script = 'get_neighboring_words.py';
                        queryParams.max_time = 10;
                        scope.sortedResults = [];
                        queryParams.start = '0';
                        queryParams.end = "0";
                        var currentQueryObject = angular.extend({}, queryParams, {
                            first: queryParams.first_kwic_sorting_option,
                            second: queryParams.second_kwic_sorting_option,
                            third: queryParams.third_kwic_sorting_option
                        });
                        if (angular.equals(sortedKwicCached.queryObject, currentQueryObject)) {
                            scope.sortedResults = sortedKwicCached.results;
                            getKwicResults(scope, results.data.results_length)
                            scope.concKwic.loading = false;
                        } else {
                            recursiveLookup(scope, queryParams, 0);
                        }
                    }).catch(function(response) {
                        scope.results = {};
                        scope.concKwic.description = {};
                        scope.concKwic.loading = false;
                    });
                } else {
                    scope.concKwic.resultsPromise.then(function(results) {
                        scope.results = results.data;
                        scope.concKwic.description = angular.extend({}, scope.results.description, {
                            resultsLength: scope.results.results_length
                        });
                        scope.concKwic.loading = false;
                    }).catch(function(response) {
                        scope.results = {};
                        scope.concKwic.description = {};
                        scope.concKwic.loading = false;
                    });
                }
            }
        }
    }

    function bibliography($rootScope) {
        return {
            templateUrl: 'app/components/concordanceKwic/bibliography.html',
            replace: true,
            link: function(scope) {
                scope.concKwic.resultsPromise.then(function(results) {
                    scope.results = results.data;
                    scope.concKwic.description = angular.extend({}, scope.results.description, {
                        resultsLength: scope.results.results_length
                    });
                    scope.concKwic.loading = false;
                }).catch(function(response) {
                    scope.results = {};
                    scope.concKwic.description = {};
                    scope.concKwic.loading = false;
                });
                scope.metadataAddition = [];
                scope.addToSearch = function(title) {
                    title = '"' + title + '"';
                    var itemIndex = scope.metadataAddition.indexOf(title);
                    if (itemIndex === -1) {
                        scope.metadataAddition.push(title);
                    } else {
                        scope.metadataAddition.splice(itemIndex, 1);
                    }

                    $rootScope.formData.title = scope.metadataAddition.join(' | ');
                }
            }
        }
    }

    function resultsDescription(request, descriptionValues) {
        var buildDescription = function(scope) {
            if (scope.resultsLength && scope.end <= scope.resultsPerPage && scope.end <= scope.resultsLength) {
                var description = 'Hits ' + scope.start + ' - ' + scope.end + ' of ' + scope.resultsLength;
            } else if (scope.resultsLength) {
                if (scope.resultsPerPage > scope.resultsLength) {
                    var description = 'Hits ' + scope.start + ' - ' + scope.resultsLength + ' of ' + scope.resultsLength;
                } else {
                    var description = 'Hits ' + scope.start + ' - ' + scope.end + ' of ' + scope.resultsLength;
                }
            } else {
                var description = 'No results for your query.';
            }
            return description;
        }
        return {
            template: '<div id="search-hits">{{ hits }}</div>',
            replace: true,
            link: function(scope, element, attrs) {
                scope.start = descriptionValues.start;
                scope.end = descriptionValues.end;
                scope.resultsPerPage = descriptionValues.resultsPerPage;
                scope.resultsLength = descriptionValues.resultsLength;
                scope.hits = buildDescription(scope);
                attrs.$observe('description', function(newDescription) {
                    if (newDescription.length > 0) {
                        newDescription = angular.fromJson(newDescription);
                        if (scope.resultsLength !== newDescription.resultsLength) {
                            scope.resultsLength = newDescription.resultsLength;
                            descriptionValues.resultsLength = scope.resultsLength;
                        }
                        if (newDescription.start !== scope.start) {
                            scope.start = newDescription.start;
                            descriptionValues.start = scope.start;
                        }
                        if (newDescription.end !== scope.end) {
                            scope.end = newDescription.end;
                            descriptionValues.end = scope.end
                        }
                        if (newDescription.results_per_page !== scope.resultsPerPage) {
                            scope.resultsPerPage = newDescription.results_per_page;
                            descriptionValues.resultsPerPage = scope.resultsPerPage;
                        }
                    }
                    scope.hits = buildDescription(scope);
                });
                attrs.$observe('queryStatus', function(loading) {
                    loading = eval(loading);
                    if (!loading && scope.concKwic.description.resultsLength > 0) {
                        request.script(scope.formData, {
                            script: 'get_total_results.py'
                        }).then(function(response) {
                            scope.resultsLength = response.data;
                            descriptionValues.resultsLength = scope.resultsLength;
                            scope.hits = buildDescription(scope)
                        });
                    }
                });
            }
        }
    }

    function concordanceKwicSwitch($location, URL) {
        var buildReportSwitch = function(scope) {
            var concordance = {
                labelBig: "View occurrences with context",
                labelSmall: "Concordance",
                name: "concordance",
                href: URL.objectToUrlString(scope.formData, {
                    report: 'concordance'
                })
            }
            var kwic = {
                labelBig: "View occurrences line by line (KWIC)",
                labelSmall: "Keyword in context",
                name: "kwic",
                href: URL.objectToUrlString(scope.formData, {
                    report: 'kwic',
                    direction: '',
                    metadata_sorting_field: ''
                })
            }
            return [concordance, kwic];
        }
        return {
            templateUrl: 'app/components/concordanceKwic/concordanceKwicSwitch.html',
            replace: true,
            link: function(scope) {
                scope.reportSwitch = buildReportSwitch(scope);
            }
        }
    }

    function pages($location, URL) {
        var buildPages = function(scope, morePages) {
            var start = scope.concKwic.description.start;
            var resultsPerPage = parseInt(scope.formData.results_per_page) || 25;
            var resultsLength = scope.concKwic.description.resultsLength;

            // first find out what page we are on currently.
            var currentPage = Math.floor(start / resultsPerPage) + 1 || 1;

            // then how many total pages the query has
            var totalPages = Math.floor(resultsLength / resultsPerPage);
            var remainder = resultsLength % resultsPerPage;
            if (remainder !== 0) {
                totalPages += 1;
            }
            totalPages = totalPages || 1;

            // construct the list of page numbers we will output.
            var pages = []
                // up to four previous pages
            var prev = currentPage - 4;
            while (prev < currentPage) {
                if (prev > 0) {
                    pages.push(prev);
                }
                prev += 1;
            }
            // the current page
            pages.push(currentPage);
            // up to five following pages
            var next = currentPage + 5;
            while (next > currentPage) {
                if (next < totalPages) {
                    pages.push(next);
                }
                next -= 1;
            }
            // first and last if not already there
            if (pages[0] !== 1) {
                pages.unshift(1);
            }
            if (pages[-1] !== totalPages) {
                pages.push(totalPages);
            }
            var uniquePages = [];
            $.each(pages, function(i, el) {
                if ($.inArray(el, uniquePages) === -1) uniquePages.push(el);
            });
            var pages = uniquePages.sort(function(a, b) {
                return a - b;
            });

            // now we construct the actual links from the page numbers
            var pageObject = [];
            for (var i = 0; i < pages.length; i++) {
                var page = pages[i];
                var pageStart = page * resultsPerPage - resultsPerPage + 1;
                var pageEnd = page * resultsPerPage;
                if (page === currentPage) {
                    var active = "active";
                } else {
                    var active = "";
                }
                var pageStart = resultsPerPage * (page - 1) + 1;
                var pageEnd = pageStart + resultsPerPage - 1;
                if (pageEnd > resultsLength) {
                    pageEnd = resultsLength;
                }
                if (page === 1 && !2 in pages) {
                    page = "First";
                }
                if (page === totalPages) {
                    if (morePages !== 'undefined' && morePages) { // Account for concordance from collocation case
                        page = "More";
                    } else {
                        page = "Last";
                    }
                }
                var href = URL.objectToUrlString($location.search(), {
                    start: pageStart,
                    end: pageEnd
                });
                pageObject.push({
                    display: page,
                    href: href,
                    active: active
                });
            }
            return pageObject;
        }
        return {
            restrict: 'E',
            template: ['<div id="page-links" class="btn-group">',
                '<a href="{{ page.href }}" class="btn btn-default btn-lg {{ page.active }}" ng-repeat="page in pages">{{ page.display }}</a>',
                '</div>'
            ].join(''),
            replace: true,
            link: function(scope, element, attrs) {
                scope.$watch(function() {
                    return scope.results;
                }, function() {
                    scope.pages = buildPages(scope, scope.concKwic.description.more_pages);
                }, true);
            }
        }
    }
})();
