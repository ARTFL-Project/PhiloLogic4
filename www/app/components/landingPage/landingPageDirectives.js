(function() {
    "use strict";

    angular
        .module('philoApp')
        .directive('defaultLandingPage', defaultLandingPage)
        .directive('dictionaryLandingPage', dictionaryLandingPage)
        .directive('simpleLandingPage', simpleLandingPage)
        .directive('landingPageContent', landingPageContent)


    function defaultLandingPage($rootScope) {
        var createRanges = function(list, columnLimit) {
            var ranges = [];
            var row = [];
            var position = 0;
            for (var i = 0; i < list.length; i += 1) {
                position++;
                row.push(list[i]);
                if (position === columnLimit) {
                    ranges.push(row);
                    row = [];
                    position = 0;
                }
            }
            if (row.length) {
                ranges.push(row);
            }
            return ranges;
        }
        return {
            templateUrl: 'app/components/landingPage/defaultLandingPage.html',
            replace: true,
            link: function(scope) {
                scope.defaultLandingPageBrowsing = $rootScope.philoConfig.default_landing_page_browsing;
                // Cache generated ranges since they were disappearing with the back button
                if (typeof($rootScope.philoConfig.default_landing_page_browsing.splitRanges) === 'undefined') {
                    $rootScope.philoConfig.default_landing_page_browsing.splitRanges = [];
                }
                for (var i = 0; i < scope.defaultLandingPageBrowsing.length; i += 1) {
                    if (typeof($rootScope.philoConfig.default_landing_page_browsing.splitRanges[i]) === 'undefined') {
                        var browseType = scope.defaultLandingPageBrowsing[i];
                        scope.defaultLandingPageBrowsing[i].queries = createRanges(browseType.queries, 5);
                        $rootScope.philoConfig.default_landing_page_browsing.splitRanges[i] = scope.defaultLandingPageBrowsing[i].queries
                    } else {
                        scope.defaultLandingPageBrowsing[i].queries = $rootScope.philoConfig.default_landing_page_browsing.splitRanges[i];
                    }
                }
            }
        }
    }

    function dictionaryLandingPage($rootScope, request) {
        var setupPage = function(scope) {
            request.script({
                    script: 'get_bibliography.py',
                    object_level: 'doc'
                })
                .then(function(response) {
                    scope.volumeData = [];
                    for (var i = 0; i < response.data.length; i++) {
                        scope.volumeData.push(response.data[i]);
                    }
                });

            var dicoLetterRange = $rootScope.philoConfig.dico_letter_range;
            scope.dicoLetterRows = [];
            scope.showDicoLetterRows = true;
            var row = [];
            var position = 0;
            for (var i = 0; i < dicoLetterRange.length; i++) {
                position++;
                row.push({
                    letter: dicoLetterRange[i],
                    url: "query?report=bibliography&head=^" + dicoLetterRange[i] + '.*'
                });
                if (position === 4) {
                    scope.dicoLetterRows.push(row);
                    row = [];
                    position = 0;
                }
            }
            if (row.length) {
                scope.dicoLetterRows.push(row);
            }
            if (scope.dicoLetterRows.length == 0) {
                scope.showDicoLetterRows = false;
            }
        }
        return {
            templateUrl: 'app/components/landingPage/dictionaryLandingPage.html',
            replace: true,
            link: function(scope) {
                setupPage(scope);
            }
        }
    }

    function simpleLandingPage(request) {
        var setupPage = function(scope) {
            request.report({
                    report: 'bibliography',
                    simple_bibliography: 'all'
                })
                .then(function(response) {
                    scope.bibliography = response.data;
                });
        }
        return {
            templateUrl: 'app/components/landingPage/simpleLandingPage.html',
            replace: true,
            link: function(scope) {
                setupPage(scope);
            }
        }
    }

    function landingPageContent($rootScope, request) {
        var getContent = function(scope, query) {
            scope.loadingContent = true;
            request.script({
                    script: 'get_landing_page_content.py',
                    group_by_field: query.browseType.group_by_field,
                    display_count: query.browseType.display_count,
                    is_range: query.browseType.is_range,
                    query: query.query,
                    citation: JSON.stringify(query.browseType.citation)
                })
                .then(function(response) {
                    scope.resultGroups = response.data.content;
                    scope.displayCount = response.data.display_count;
                    scope.contentType = response.data.content_type;
                    scope.loadingContent = false;
                })
                .catch(function(response) {
                    scope.loadingContent = false;
                });
        }
        return {
            templateUrl: 'app/components/landingPage/landingPageContent.html',
            replace: true,
            link: function(scope, element, attrs) {
                scope.resultGroups = [];
                scope.displayLimit = 8;
                var contentTypeClass = {
                    author: "col-xs-12 col-sm-6",
                    title: "col-xs-12",
                    year: "col-xs-12"
                }
                if (!$.isEmptyObject(scope.philoConfig.default_landing_page_display)) {
                    var query = {
                        browseType: scope.philoConfig.default_landing_page_display,
                        query: scope.philoConfig.default_landing_page_display.queries
                    }
                    getContent(scope, query);
                }
                attrs.$observe('name', function(query) {
                    if (query !== '') {
                        if (scope.displayLimit > 8) {
                            scope.displayLimit = 8;
                        }
                        query = scope.$eval(query);
                        scope.loadingContent = true;
                        getContent(scope, query);
                    }
                });
                scope.displayMoreItems = function() {
                    scope.displayLimit += 1;
                }
            }
        }
    }
})();
