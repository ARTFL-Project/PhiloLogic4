philoApp.directive('loading', function() {
    return {
        restrict: 'E',
        template: '<div class="spinner"><div class="bounce1"></div><div class="bounce2"></div><div class="bounce3"></div></div>'
    }
});

philoApp.directive('progressBar', function() {
    return {
        restrict: 'E',
        template: '<div class="progress"><div class="progress-bar" role="progressbar" aria-valuenow="20" aria-valuemin="0" aria-valuemax="100" style="width: 0%;"></div></div>',
        link: function(scope, element, attrs) {
            attrs.$observe('progress', function(percent){
                var progressElement = $(element).find('.progress-bar');
                progressElement.velocity({'width': percent.toString() + '%'}, {
                    queue: false,
                    complete: function() {
                        progressElement.text(percent.toString() + '%');
                        if (percent == 100) {
                            progressElement.delay(500).velocity('slideUp');
                        }
                    }
                }); 
            });     
        }
    }
});

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

philoApp.directive('biblioCriteria', ['$rootScope','$http', '$location', 'URL', function($rootScope, $http, $location, URL) {
    var buildCriteria = function(queryParams) {
        var queryArgs = angular.copy(queryParams);
        var biblio = []
        if (queryArgs.report === "time_series") {
            delete queryParams.date;
        }
        var config = $rootScope.philoConfig;
        for (var i=0; i < config.metadata.length; i++) {
            var k = config.metadata[i];
            var v = queryArgs[k];
            var alias = k;
            if (v) {
                if (k in config.metadata_aliases) {
                    alias = config.metadata_aliases[k];
                }
                biblio.push({key: k, alias: alias, value: v});
            }
        }
        return biblio
    }
    var removeMetadata = function(metadata, queryParams) {
        delete queryParams[metadata];
        var request = $rootScope.philoConfig.db_url + '/' + URL.query(queryParams);
        if (queryParams.report === "concordance" || queryParams.report === "kwic") {
            $http.get(request).success(function(data) {
                $rootScope.results = data;
                $location.url(URL.objectToString(queryParams, true));
            })
        } else if (queryParams.report === "collocation") {
            $('#collocate_counts').empty();
        }
    }
    return {
        restrict: 'E',
        template: 'Bibliography criteria: <span class="biblio-criteria" ng-repeat="metadata in biblio" style="margin: 1px">{{ ::metadata.alias }} : <b>{{ ::metadata.value }}</b>' +
                  '&nbsp;<span class="glyphicon glyphicon-remove-circle" ng-click="removeMetadata(metadata.key, formData)"></span></span><b ng-if="biblio.length === 0">None</b>',
        scope: {
        control: '='
        },
        link: function(scope, element, attrs) {
                scope.$watch(function() {
                    return $rootScope.formData;
                    }, function() {
                    scope.biblio = buildCriteria($rootScope.formData);
                }, true);
                scope.formData = $rootScope.formData;
                scope.removeMetadata = removeMetadata;
        } 
    }
}]);

philoApp.directive('collocationCloud', ['defaultDiacriticsRemovalMap', function(defaultDiacriticsRemovalMap) {
    var buildCloud = function(sortedList) {
        var cloudList = angular.copy(sortedList);
        $.fn.tagcloud.defaults = {
            size: {start: 1.0, end: 3.5, unit: 'em'},
            color: {start: '#C4DFF3', end: '#286895'}
          };
        $('#collocate_counts').hide().empty();
        var removeDiacritics = function(str) {
            var changes = defaultDiacriticsRemovalMap.map;
            for(var i=0; i<changes.length; i++) {
                str = str.replace(changes[i].letters, changes[i].base);
            }
            return str;
        }
        cloudList.sort(function(a,b) {
            var x = removeDiacritics(a.label);
            var y = removeDiacritics(b.label);
            return x < y ? -1 : x > y ? 1 : 0;
        });
        var html = ''
        for (var i in cloudList) {
            var word = cloudList[i].label;
            var count = cloudList[i].count;
            var href = cloudList[i].url;
            var searchLink = '<span class="cloud_term" rel="' + count + '" data-href="' + href + '&collocate_num=' + count + '">';
            html += searchLink + word + ' </span>';
        }
        $("#collocate_counts").html(html);
        $("#collocate_counts span").tagcloud();
        $("#collocate_counts").velocity('fadeIn');
    }
    return {
        restrict: 'E',
        template: '<div id="word_cloud" class="word_cloud">' +
                  '<div id="collocate_counts" class="collocation_counts">{{ cloud }}</div></div>',
        link: function(scope, element, attrs) {
                scope.$watch('sortedLists', function() {
                    if (!$.isEmptyObject(scope.sortedLists)) {
                        scope.cloud = buildCloud(scope.sortedLists.all);
                    }
                });
        }
        
    }
}]);
    