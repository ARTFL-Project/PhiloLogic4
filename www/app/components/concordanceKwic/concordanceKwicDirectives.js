"use strict";

philoApp.directive('concordance', ['$rootScope', '$http', 'request', function($rootScope, $http, request) {
     var moreContext = function($event, resultNumber) {
        var element = $($event.currentTarget).parents('.philologic_occurrence').find('.philologic_context');
        var defaultElement = element.find('.default-length');
        var moreContextElement = element.find('.more-length');
        if (defaultElement.css('display') == "none") {
            moreContextElement.hide()
            defaultElement.velocity('fadeIn', {duration: 300});
        } else {
            if (moreContextElement.is(':empty')) {
                var extraParams = {script: 'get_more_context.py', hit_num: resultNumber};
				request.script($rootScope.formData, extraParams).then(function(response) {
                    defaultElement.hide();
                    moreContextElement.html(response.data).promise().done(function() {
                            $(this).velocity('fadeIn', {duration: 300});
                        });
                });
            } else {
                defaultElement.hide();
                moreContextElement.velocity('fadeIn', {duration: 300});
            }
        }
    } 
    return {
        templateUrl: 'app/components/concordanceKwic/concordance.html',
		replace: true,
        link: function(scope) {
            scope.moreContext = moreContext;
        }
    }
}]);

philoApp.directive('kwic', ['$rootScope', function($rootScope) {
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
				var target = $(event.currentTarget).find('.full_biblio');
				target.addClass('show');
			}
			scope.hideFullBiblio = function(event) {
				var target = $(event.currentTarget).find('.full_biblio');
				target.removeClass('show');
			}
        }
    }
}]);

philoApp.directive('bibliography', ['$rootScope', function($rootScope) {
    return {
        templateUrl: 'app/components/concordanceKwic/bibliography.html',
		replace: true,
		link: function(scope) {
			scope.metadataAddition = [];
			scope.addToSearch = function(title) {
				title = '"' + title + '"';
				var itemIndex = scope.metadataAddition.indexOf(title);
				console.log(itemIndex)
				if (itemIndex === -1) {
					scope.metadataAddition.push(title);
				} else {
					scope.metadataAddition.splice(itemIndex, 1);
				}
				
				$rootScope.formData.title = scope.metadataAddition.join(' | ');
			}
		}
    }
}]);

philoApp.directive('resultsDescription', ['request', 'descriptionValues', function(request, descriptionValues) {
	var buildDescription = function(scope) {
		if (scope.resultsLength && scope.end <= scope.resultsPerPage && scope.end <= scope.resultsLength) {
			var description = 'Hits ' + scope.start + ' - ' + scope.end  + ' of ' + scope.resultsLength;
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
                    newDescription = JSON.parse(newDescription);
                    if (scope.resultsLength !== scope.concKwic.results.results_length) {
                        scope.resultsLength = scope.concKwic.results.results_length;
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
				if (!loading) {
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
    
}]);

philoApp.directive('concordanceKwicSwitch', ['$location', 'URL', function($location, URL) {
    var buildReportSwitch = function(scope) {
        var concordance = {
            labelBig: "View occurrences with context",
            labelSmall: "Concordance",
            name: "concordance",
			href: URL.objectToUrlString(scope.formData, {report: 'concordance'})
            }
        var kwic = {
            labelBig: "View occurrences line by line (KWIC)",
            labelSmall: "Keyword in context",
            name: "kwic",
			href: URL.objectToUrlString(scope.formData, {report: 'kwic'})
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
}]);

philoApp.directive('pages', ['$location', 'URL', function($location, URL) {
    var buildPages = function(scope, morePages) {
        var start = scope.concKwic.results.description.start;
        var resultsPerPage = parseInt(scope.formData.results_per_page) || 25;
        var resultsLength = scope.concKwic.results.results_length;
    
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
                if (morePages !== 'undefined' && morePages) { // Account for concordance from collocation case
                    page = "More";
                } else {
                    page = "Last";
                }
            }
			var href = URL.objectToUrlString($location.search(), {start: pageStart, end: pageEnd});
            pageObject.push({display: page, href: href, active: active});
        }
        return pageObject;
    }
    return {
        restrict: 'E',
        template: ['<div id="page_links" class="btn-group">',
						'<a href="{{ page.href }}" id="current_results_page" class="btn btn-default btn-lg {{ page.active }}" ng-repeat="page in pages">{{ page.display }}</a>',
				   '</div>'].join(''),
		replace: true,
        link: function(scope, element, attrs) {
                scope.$watch(function() {
                    return scope.results;
                    }, function() {
                    scope.pages = buildPages(scope, scope.concKwic.results.description.more_pages);
                }, true);
        }
    }
}]);
