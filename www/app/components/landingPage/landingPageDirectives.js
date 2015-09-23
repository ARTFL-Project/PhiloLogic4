(function() {
    "use strict";

    angular
        .module('philoApp')
        .directive('defaultLandingPage', defaultLandingPage)
        .directive('dictionaryLandingPage', dictionaryLandingPage)
        .directive('landingPageContent', landingPageContent)


    function defaultLandingPage($rootScope) {
        var createRanges = function(list, columnLimit) {
            var ranges = [];
            var row = [];
            var position = 0;
            for (var i = 0; i < list.length; i++) {
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
                // Create author range boxes
                if (typeof($rootScope.philoConfig.landing_page_browsing.author) !== 'undefined' && $rootScope.philoConfig.landing_page_browsing.author.length > 0) {
                    var authorRanges = $rootScope.philoConfig.landing_page_browsing.author;
                } else {
                    scope.authorRanges = false;
                }
                if (typeof(authorRanges) !== 'undefined') {
                    scope.authorRanges = createRanges(authorRanges, 5);
                }

                // Create title range boxes
                if (typeof($rootScope.philoConfig.landing_page_browsing.title) !== 'undefined' && $rootScope.philoConfig.landing_page_browsing.title.length > 0) {
                    var titleRanges = $rootScope.philoConfig.landing_page_browsing.title;
                } else {
                    scope.titleRanges = false;
                }
                if (typeof(titleRanges) !== 'undefined') {
                    scope.titleRanges = createRanges(titleRanges, 5);
                }

                // Create date range boxes
                var start = $rootScope.philoConfig.landing_page_browsing.date.start;
                var end = $rootScope.philoConfig.landing_page_browsing.date.end;
                var interval = $rootScope.philoConfig.landing_page_browsing.date.interval;
                if (typeof(start) === 'undefined' || typeof(end) === 'undefined' || typeof(interval) === 'undefined') {
                    scope.dateRanges = false;
                } else if (start.length === 0 || end.length === 0 || interval.length === 0) {
                    scope.dateRanges = false;
                } else {
                    var dateList = []
                    for (var i = start; i < end; i += interval) {
                        var value = i.toString() + '-' + (i + interval)
                        dateList.push(value)
                    }
                    scope.dateRanges = createRanges(dateList, 5);
                }

                // Set up margin offset in case author or title is not displayed
                scope.authorOffset = "";
                scope.titleOffset = "";
                if (!scope.titleRanges) {
                    scope.authorOffset = "col-sm-offset-3";
                }
                if (!scope.authorRanges) {
                    scope.titleOffset = "col-sm-offset-3";
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
        }
        return {
            templateUrl: 'app/components/landingPage/dictionaryLandingPage.html',
            replace: true,
            link: function(scope) {
                setupPage(scope);
            }
        }
    }

    function landingPageContent($rootScope, request) {
        var getContent = function(scope, query) {
            scope.contentType = query.contentType;
            scope.range = query.range;
            scope.loadingContent = true;
            request.script({
                    script: 'get_landing_page_content.py',
                    landing_page_content_type: scope.contentType,
                    range: scope.range
                })
                .then(function(response) {
                    scope.resultGroups = [];
                    var content = response.data;
                    var resultGroups = [];
                    var results = [];
                    var oldPrefix = "";
                    for (var i = 0; i < content.length; i++) {
                        var prefix = content[i].initial;
                        if (prefix !== oldPrefix && oldPrefix !== '') {
                            scope.resultGroups.push({
                                prefix: oldPrefix,
                                results: results
                            });
                            results = [];
                        }
                        results.push(content[i])
                        oldPrefix = prefix;
                    }
                    scope.resultGroups.push({
                        prefix: prefix,
                        results: results
                    });
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
                scope.displayLimit = 4;
                var contentTypeClass = {
                    author: "col-xs-12 col-sm-6",
                    title: "col-xs-12",
                    year: "col-xs-12"
                }
                if (!$.isEmptyObject(scope.philoConfig.landing_page_browsing.default_display)) {
                    var query = {
                        contentType: scope.philoConfig.landing_page_browsing.default_display.type,
                        range: scope.philoConfig.landing_page_browsing.default_display.range
                    }
                    getContent(scope, query);
                }
                attrs.$observe('name', function(query) {
                    if (query !== '') {
                        if (scope.displayLimit > 4) {
                            scope.displayLimit = 4;
                        }
                        query = scope.$eval(query);
                        scope.loadingContent = true;
                        getContent(scope, query);
                        scope.contentClass = contentTypeClass[scope.contentType];
                    }
                });
                scope.displayMoreItems = function() {
                    scope.displayLimit += 1;
                }
            }
        }
    }
})();
