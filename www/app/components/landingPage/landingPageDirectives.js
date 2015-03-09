"use strict";

philoApp.directive('defaultLandingPage', ['$rootScope', function($rootScope) {
    var setupPage = function(scope) {
        scope.authorRanges = $rootScope.philoConfig.landing_page_browsing.author;
        scope.titleRanges = $rootScope.philoConfig.landing_page_browsing.title;
        scope.authorOffset = "";
        scope.titleOffset = "";
        
        if (!scope.titleRanges) {
            scope.authorOffset = "col-sm-offset-3";
        }
        if (!scope.authorRanges) {
            scope.titleOffset = "col-sm-offset-3";
        }
        scope.dateRanges = [];
        var start = $rootScope.philoConfig.landing_page_browsing.date.start;
        var end = $rootScope.philoConfig.landing_page_browsing.date.end;
        var interval = $rootScope.philoConfig.landing_page_browsing.date.interval;
        var row = [];
        var position = 0;
        for (var i=start; i < end; i += interval) {
            position++;
            row.push({start: i, end: i+interval});
            if (position === 4) {
                scope.dateRanges.push(row);
                row = [];
                position = 0;
            }
        }
        if (row.length) {
            scope.dateRanges.push(row);
        }
        if (!scope.dateRanges.length) {
            scope.dateRanges = false;
        }
    }
    return {
        templateUrl: 'app/components/landingPage/defaultLandingPage.html',
        link: function(scope) {
            setupPage(scope);
        }
    }
}]);

philoApp.directive('dictionaryLandingPage', ['$rootScope', 'request', function($rootScope, request) {
    var setupPage = function(scope) {
        request.script({
            script: 'get_bibliography.py',
            object_level: 'doc'})
        .then(function(response) {
            scope.volumeData = [];
            for (var i=0; i < response.data.length; i++) {
                scope.volumeData.push(response.data[i]);
            }
        });
        
        var dicoLetterRange = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M",
                                "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"];
        scope.dicoLetterRows = [];
        var row = [];
        var position = 0;
        for (var i=0; i < dicoLetterRange.length; i++) {
            position++;
            row.push({
                letter: dicoLetterRange[i],
                url: "dispatcher.py?report=bibliography&head=^" + dicoLetterRange[i] + '.*'
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
        link: function(scope) {
            setupPage(scope);
        }
    }
}]);

philoApp.directive('landingPageContent', ['$rootScope', 'request', function($rootScope, request) {
    var getContent = function(scope) {
        var contentType = scope.contentType;
        request.script({
            script: 'get_landing_page_content.py',
            landing_page_content_type: scope.contentType,
            range: scope.range
        })
        .then(function(response) {
            var content = response.data;
            var resultGroups = [];
            var results = [];
            var oldPrefix = "";
            for (var i=0; i < content.length; i++) {
                if (contentType == "author" || contentType == "title") {
                    var prefix = content[i][contentType].slice(0,1).toUpperCase();
                } else {
                    var prefix = content[i].date;
                }
                if (prefix !== oldPrefix && oldPrefix !== '') {
                    scope.resultGroups.push({prefix: oldPrefix, results: results});
                    results = [];
                }
                results.push(content[i])
                oldPrefix = prefix;
            }
            scope.resultGroups.push({prefix: prefix, results: results});
        })
    }
    return {
        templateUrl: 'app/components/landingPage/landingPageContent.html',
        link: function(scope, element, attrs) {
            scope.resultGroups = [];
            var contentTypeClass = {
                author: "col-xs-12 col-sm-6",
                title: "col-xs-12",
                year: "col-xs-12"
                }
            attrs.$observe('name', function(query) {
                if (query !== '') {
                    getContent(scope);
                    scope.contentClass= contentTypeClass[scope.contentType];
                }
            });
        }
    }
}]);