philoApp.controller('concordanceKwicCtrl', ['$scope', '$rootScope', '$http', '$location', 'biblioCriteria', 'progressiveLoad', 'URL',
                                            function($scope, $rootScope, $http, $location, biblioCriteria, progressiveLoad, URL) {
                                                
    $rootScope.textObjectCitation = {} // Clear citation in text Objects
    
    $rootScope.formData = $location.search();
    if (typeof($rootScope.formData.q) === "undefined") {
        $rootScope.formData.report = "bibliography";
        $location.path('/bibliography')
    }
    var request = {
        method: "GET",
        url: $scope.philoConfig.db_url + '/' + URL.query($rootScope.formData)
    }
    var oldResults = angular.copy($rootScope.results)
    if ("results" in oldResults) {
        delete $rootScope.results.results;
        $rootScope.results = {description: oldResults.description, results_length: oldResults.results_length};
    } else {
        $rootScope.results = {};
    }
    $rootScope.report = $rootScope.formData.report;
    $http(request)
        .success(function(data, status, headers, config) {
            $rootScope.results = data;
        })
        .error(function(data, status, headers, config) {
            console.log("Error", status, headers)
        });
    
    $scope.$watch(function() {
        return $rootScope.formData;
        }, function() {
      $rootScope.biblio = biblioCriteria.build($rootScope.formData);
    }, true);
    $scope.removeMetadata = biblioCriteria.remove;
    
    $rootScope.frequencyResults = [];
    $scope.resultsContainerWidth = "col-xs-12";
    $scope.sidebarWidth = '';    
    $scope.$watch(function() {
        return $rootScope.frequencyResults;
        }, function() {
            if ($rootScope.frequencyResults.length > 0) {
                $scope.resultsContainerWidth = "col-xs-8";
                $scope.sidebarWidth = "col-xs-4";
            } else {
                $scope.resultsContainerWidth = "col-xs-12";
                $scope.sidebarWidth = "";
            }
    }, true);
    
    $rootScope.percentComplete = 0;
    $scope.$watch(function() {
        return $rootScope.percentComplete;
        }, function() {
            progressiveLoad.updateProgressBar($("#frequency_container .progress-bar"), $rootScope.percentComplete);
    }, true);
}]);

philoApp.controller('concordanceKwicSwitcher', ['$scope', '$rootScope', '$http', '$location', 'URL', function($scope, $rootScope, $http, $location, URL) {
    $scope.switchTo = function(report) {
        $rootScope.formData.report = report;
        $('#report label.active').removeClass('active');
        $('#' + report).parent().addClass('active');
        $rootScope.report = report;
        $location.url(URL.objectToString($rootScope.formData, true));
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
}]);

philoApp.controller('facets', ['$scope', '$rootScope', '$http', 'URL', 'progressiveLoad', function($scope, $rootScope, $http, URL, progressiveLoad) {
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
    
    $scope.selectedFacet = {};
    
    $scope.spinner = false;
    
    var populateSidebar = function(facet, fullResults, totalResults, intervalStart, intervalEnd, queryParams) {
        if (intervalStart < totalResults) {
            queryParams.start = intervalStart;
            queryParams.end = intervalEnd;
            var request = {
                method: "GET",
                url: "scripts/get_frequency.py?" + URL.objectToString(queryParams)
            }
            $http(request)
                .success(function(data, status, headers, config) {
                    $scope.spinner = false;
                   if ($('#selected-sidebar-option').data('interrupt') != true && $('#selected-sidebar-option').data('selected') == facet) {
                        if (facet.match(/collocates$/)) {
                            var merge = progressiveLoad.mergeResults(fullResults.unsorted, data[facet]);
                        } else {
                            var merge = progressiveLoad.mergeResults(fullResults.unsorted, data);
                        }
                        $rootScope.frequencyResults = merge.sorted;
                        fullResults = merge;
                        if (intervalEnd < totalResults) {
                            $rootScope.percentComplete = intervalEnd / totalResults * 100;
                        }
                        if (intervalStart === 0) {
                            intervalStart = 3000;
                            intervalEnd = 13000;
                        } else {
                            intervalStart += 10000;
                            intervalEnd += 10000;
                        }
                        populateSidebar(facet, fullResults, totalResults, intervalStart, intervalEnd, queryParams);
                   } else {
                        // This won't affect the full collocation report which can't be interrupted
                        // when on the page
                        $('#selected-sidebar-option').data('interrupt', false);
                   }
                })
                .error(function(data, status, headers, config) {
                    console.log("Error", status, headers)
                });
        } else {
            $rootScope.percentComplete = 100;
            $("#frequency_container .progress").delay(500).velocity('slideUp', {complete: function() {
                $("#frequency_container .progress-bar").width(0).text("0%");}});
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
    
    $scope.selectFacet = function(facetObj) {
        $scope.selectedFacet = facetObj;
        var facet = facetObj.facet;
        // store the selected field to check whether to kill the ajax calls in populate_sidebar
        $('#selected-sidebar-option').data('selected', facet);
        $('#selected-sidebar-option').data('interrupt', false);
        
        var queryParams = angular.copy($rootScope.formData);
        queryParams.frequency_field = facet;
        var urlString = URL.objectToString(queryParams);
        if (urlString in sessionStorage) {
            $rootScope.frequencyResults = JSON.parse(sessionStorage[urlString]);
             $rootScope.percentComplete = 100;
        } else {
            var totalResults = $rootScope.results.results_length;
            var percent = 100 / totalResults * 100;
            $rootScope.percentComplete = 0;
            
            var fullResults = {};
            var intervalStart = 0;
            var intervalEnd = 3000;
            $scope.spinner = true;
            populateSidebar(facet, fullResults, totalResults, intervalStart, intervalEnd, queryParams);
        }
    }
    $scope.removeSidebar = function() {
        $rootScope.frequencyResults = [];
        $('#selected-sidebar-option').data('interrupt', true);
    }
}]);

philoApp.controller('paging', ['$scope', '$rootScope', '$http', '$location', 'URL', function($scope, $rootScope, $http, $location, URL) {
    $scope.buildPages = function() {
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
        $rootScope.formData.start = start;
        $rootScope.formData.end = end;
        var request = {
            method: "GET",
            url: $rootScope.philoConfig.db_url + '/' + URL.query($rootScope.formData)
        }
        $("body").velocity('scroll', {duration: 200, easing: 'easeOutCirc', offset: 0, complete: function() {
            $rootScope.results = {};
        }});
        $http(request)
        .success(function(data, status, headers, config) {
            $rootScope.results = data;
            $location.url(URL.objectToString($rootScope.formData, true));
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