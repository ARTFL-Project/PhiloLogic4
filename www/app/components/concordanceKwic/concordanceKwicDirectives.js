"use strict";

philoApp.directive('concordance', ['$rootScope', '$http', 'URL', function($rootScope, $http, URL) {
     var moreContext = function($event, resultNumber) {
        var element = $($event.currentTarget).parents('.philologic_occurrence').find('.philologic_context');
        var defaultElement = element.find('.default-length');
        var moreContextElement = element.find('.more-length');
        if (defaultElement.css('display') == "none") {
            moreContextElement.hide()
            defaultElement.velocity('fadeIn', {duration: 300});
        } else {
            if (moreContextElement.is(':empty')) {
                var queryParams = angular.copy($rootScope.formData);
                queryParams.hit_num = resultNumber;
                var request = {
                    method: "GET",
                    url: $rootScope.philoConfig.db_url + '/scripts/get_more_context.py?' + URL.objectToString(queryParams)
                }
                $http(request)
                .success(function(data, status, headers, config) {
                    defaultElement.hide();
                    moreContextElement.html(data).promise().done(function() {
                            $(this).velocity('fadeIn', {duration: 300});
                        });
                })
                .error(function(data, status, headers, config) {
                    console.log("Error", status, headers)
                });
            } else {
                defaultElement.hide();
                moreContextElement.velocity('fadeIn', {duration: 300});
            }
        }
    } 
    return {
        restrict: 'E',
        templateUrl: 'app/components/concordanceKwic/concordance.html',
        link: function(scope) {
            scope.moreContext = moreContext;
        }
    }
}]);

philoApp.directive('kwic', ['$rootScope', function($rootScope) {
    var initializePos = function(start, index) {
        var currentPos = start + index;
        var currentPosLength = currentPos.toString().length;
        var endPosLength = $rootScope.results.description.end.toString().length;
        var spaces = endPosLength - currentPosLength + 1;
        return currentPos + '.' + Array(spaces).join('&nbsp');
    } 
    return {
        restrict: 'E',
        templateUrl: 'app/components/concordanceKwic/kwic.html',
        link: function(scope) {
            scope.initializePos = initializePos;
        }
    }
}]);

philoApp.directive('bibliography', ['$rootScope', function($rootScope) {
    return {
        restrict: 'E',
        templateUrl: 'app/components/concordanceKwic/bibliography.html'
    }
}]);

philoApp.directive('sidebarMenu', ['$rootScope', '$http', 'URL', function($rootScope, $http, URL) {
    var populateFacets = function() {
        var facets = [];
        for (var i=0; i < $rootScope.philoConfig.facets.length; i++) {
            var alias = Object.keys($rootScope.philoConfig.facets[i])[0];
            var facet = $rootScope.philoConfig.facets[i][alias];
            if (typeof(facet) === "objet") {
                facet = JSON.stringify(facet);
            }
            facets.push({facet: facet, alias: alias});
        }
        return facets;
    }
    var populateWordFacets = function() {
        var wordsFacets = [];
        for (var i=0; i < $rootScope.philoConfig.words_facets.length; i++) {
            var alias = Object.keys($rootScope.philoConfig.words_facets[i])[0];
            var facet = $rootScope.philoConfig.words_facets[i][alias];
            wordsFacets.push({facet: facet, alias: alias});
        }
        return wordsFacets;
    }
    return {
        restrict: 'E',
        templateUrl: 'app/components/concordanceKwic/sidebarMenu.html',
        link: function(scope) {
            scope.facets = populateFacets();
            scope.wordsFacets = populateWordFacets();
        }
    }
}]);

philoApp.directive('facets', ['$rootScope', '$http', 'URL', 'progressiveLoad', function($rootScope, $http, URL, progressiveLoad) {
    var retrieveFacet = function(scope, facetObj) {
        scope.loading = false;
        scope.done = false;
        var queryParams = angular.copy($rootScope.formData);
        queryParams.frequency_field = facetObj.alias;
        var urlString = URL.objectToString(queryParams);
        if (urlString in sessionStorage) {
            $rootScope.frequencyResults = JSON.parse(sessionStorage[urlString]);
             $rootScope.percentComplete = 100;
        } else {
            // store the selected field to check whether to kill the ajax calls in populate_sidebar
            $('#selected-sidebar-option').data('selected', facetObj.alias);
            $('#selected-sidebar-option').data('interrupt', false);
            var totalResults = $rootScope.results.results_length;
            $rootScope.percentComplete = 0;
            var fullResults = {};
            scope.loading = true;
            scope.percent = 0;
            populateSidebar(scope, facetObj.alias, fullResults, totalResults, 0, 3000, queryParams);
        }
    }
    var populateSidebar = function(scope, facet, fullResults, totalResults, start, end, queryParams) {
        if (start < totalResults) {
            queryParams.start = start;
            queryParams.end = end;
            queryParams.script = "get_frequency.py"
            var request = URL.query(queryParams);
            $http.get(request)
            .then(function(results) {
                var data = results.data;
                scope.loading = false;
                if ($('#selected-sidebar-option').data('interrupt') != true && $('#selected-sidebar-option').data('selected') == facet) {
                    if (facet.match(/collocates$/)) {
                        var merge = progressiveLoad.mergeResults(fullResults.unsorted, data[facet]);
                    } else {
                        var merge = progressiveLoad.mergeResults(fullResults.unsorted, data);
                    }
                    scope.frequencyResults = merge.sorted;
                    console.log(JSON.stringify(merge.sorted))
                    fullResults = merge;
                    if (end < totalResults) {
                        $rootScope.percentComplete = end / totalResults * 100;
                        scope.percent = Math.floor($rootScope.percentComplete);
                    }
                    if (start === 0) {
                        start = 3000;
                        end = 13000;
                    } else {
                        start += 10000;
                        end += 10000;
                    }
                    populateSidebar(scope, facet, fullResults, totalResults, start, end, queryParams);
                    } else {
                        // This won't affect the full collocation report which can't be interrupted
                        // when on the page
                        $('#selected-sidebar-option').data('interrupt', false);
                    }
            });
        } else {
            scope.percent = 100;
            //$('#frequency_table').slimScroll({height: $('#results_container').height() - 14});
            if ($rootScope.philoConfig.debug === true) {
                if (typeof(localStorage) == 'undefined' ) {
                    alert('Your browser does not support HTML5 localStorage. Try upgrading.');
                } else {
                    var qParams = angular.copy($rootScope.formData);
                    qParams.frequency_field = facet;
                    var urlString = URL.objectToString(qParams);
                    try {
                        sessionStorage[urlString] = JSON.stringify(fullResults.sorted);
                    } catch(e) {
                        sessionStorage.clear();
                        sessionStorage[urlString] = JSON.stringify(fullResults.sorted);
                    }
                    console.log('results saved to localStorage')
                }
            }
        }
    }
    return {
        restrict: 'E',
        templateUrl: 'app/components/concordanceKwic/facets.html',
        link: function(scope, element, attrs) {
            attrs.$observe('facet', function(facetObj) {
                if (facetObj !== '') {
                    facetObj = JSON.parse(facetObj);
                    retrieveFacet(scope, facetObj);
                }
            });
            scope.$watch('frequencyResults', function(frequencyResults) {
                if (frequencyResults.length > 0) {
                    scope.resultsContainerWidth = "col-xs-8";
                    scope.sidebarWidth = "col-xs-4";
                } else {
                    scope.resultsContainerWidth = "col-xs-12";
                    scope.sidebarWidth = "";
                }
            });
        }
    }
}]);

philoApp.directive('pages', ['$rootScope', function($rootScope) {
    var buildPages = function() {
        var start = $rootScope.results.description.start;
        var resultsPerPage = parseInt($rootScope.formData.results_per_page);
        var resultsLength = $rootScope.results.results_length;
    
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
        $.each(pages, function(i, el){
            if($.inArray(el, uniquePages) === -1) uniquePages.push(el);
        });
        var pages = uniquePages.sort(function (a, b) { 
            return a - b;
        });
        
        // now we construct the actual links from the page numbers
        var pageObject = [];
        for (var i=0; i < pages.length; i++) {
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
                page = "Last";
            }
            pageObject.push({display: page, start: pageStart, end: pageEnd, active: active});
        }
        return pageObject;
    }
    return {
        restrict: 'E',
        template: '<div id="page_links" class="btn-group">' +
                  '<a id="current_results_page" class="btn btn-default btn-lg {{ page.active }}" ng-repeat="page in pages" ng-click="goToPage(page.start, page.end)">{{ page.display }}</a>' +
                  '</div>',
        link: function(scope, element, attrs) {
                scope.$watch(function() {
                    return $rootScope.results;
                    }, function() {
                    scope.pages = buildPages();
                }, true);
        }
    }
}]);