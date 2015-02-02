philoApp.controller('concordanceKwicCtrl', ['$scope', '$rootScope', 'biblioCriteria', function($scope, $rootScope, biblioCriteria) {
    $scope.$watch(function() {
        return $rootScope.queryParams;
        }, function() {
      $rootScope.biblio = biblioCriteria.build($rootScope.queryParams);
    }, true);
    $scope.removeMetadata = biblioCriteria.remove;
    
    
}]);

philoApp.controller('concordanceKwicSwitcher', ['$scope', '$rootScope', '$http', '$location', 'URL', function($scope, $rootScope, $http, $location, URL) {
    $scope.switchTo = function(report) {
        $rootScope.queryParams.report = report;
        $('#report label.active').removeClass('active');
        $('#' + report).parent().addClass('active');
        var request = {
            method: "GET",
            url: $rootScope.philoConfig.db_url + '/dispatcher.py?' + URL.objectToString($rootScope.queryParams)
        }
        if ("results" in $rootScope) {
            $rootScope.results.results = [];
        }
        $rootScope.report = report;
        $http(request)
        .success(function(data, status, headers, config) {
            $rootScope.results = data;
            $location.url(URL.objectToString($rootScope.queryParams, true));
        })
        .error(function(data, status, headers, config) {
            console.log("Error", status, headers)
        });
    }
}]);

philoApp.controller('kwicCtrl', ['$scope', '$rootScope', function($scope, $rootScope) {
    $scope.initializePos = function(start, index) {
        var currentPos = start + index;
        var currentPosLength = currentPos.toString().length;
        var endPosLength = $rootScope.results.description.end.toString().length;
        var spaces = endPosLength - currentPosLength + 1;
        return currentPos + '.' + Array(spaces).join('&nbsp');
    } 
}]);

philoApp.controller('concordanceCtrl', ['$scope', '$rootScope', '$http', '$location', 'URL', function($scope, $rootScope, $http, $location, URL) {
    $scope.moreContext = function($event, resultNumber) {
        element = $($event.currentTarget).parents('.philologic_occurrence').find('.philologic_context');
        defaultElement = element.find('.default-length');
        moreContextElement = element.find('.more-length');
        if (defaultElement.css('display') == "none") {
            moreContextElement.hide()
            defaultElement.velocity('fadeIn', {duration: 300});
        } else {
            if (moreContextElement.is(':empty')) {
                var queryParams = angular.copy($rootScope.queryParams);
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
}]);

philoApp.controller('facets', ['$scope', '$rootScope', function($scope, $rootScope) {
    $scope.facets = [];
    for (var i=0; i < $rootScope.philoConfig.facets.length; i++) {
        var facet = Object.keys($rootScope.philoConfig.facets[i])[0];
        var alias = $rootScope.philoConfig.facets[i][facet];
        $scope.facets.push({facet: facet, alias: alias});
    }
    $scope.wordsFacets = [];
    for (var i=0; i < $rootScope.philoConfig.words_facets.length; i++) {
        var facet = Object.keys($rootScope.philoConfig.words_facets[i])[0];
        var alias = $rootScope.philoConfig.words_facets[i][facet];
        $scope.wordsFacets.push({facet: facet, alias: alias});
    }
    $scope.selectFacet = function(facet) {
        console.log(facet);
    }
}]);

philoApp.controller('paging', ['$scope', '$rootScope', '$http', '$location', 'URL', function($scope, $rootScope, $http, $location, URL) {
    $scope.buildPages = function() {
        var start = $rootScope.results.description.start;
        var resultsPerPage = parseInt($rootScope.queryParams.results_per_page);
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
        $scope.pages = [];
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
            $scope.pages.push({display: page, start: pageStart, end: pageEnd, active: active});
        }
    }
    $scope.buildPages();
    
    $scope.goToPage = function(start, end) {
        $rootScope.queryParams.start = start;
        $rootScope.queryParams.end = end;
        var request = {
            method: "GET",
            url: $rootScope.philoConfig.db_url + '/dispatcher.py?' + URL.objectToString($rootScope.queryParams)
        }
        $("body").velocity('scroll', {duration: 200, easing: 'easeOutCirc', offset: 0, complete: function() {
            $rootScope.results = {};
        }});
        $http(request)
        .success(function(data, status, headers, config) {
            $rootScope.results = data;
            $location.url(URL.objectToString($rootScope.queryParams, true));
        })
        .error(function(data, status, headers, config) {
            console.log("Error", status, headers)
        });
    }
    
    $scope.$watch(function() {
        return $rootScope.results;
        }, function() {
      $scope.buildPages();
    }, true);
}]);