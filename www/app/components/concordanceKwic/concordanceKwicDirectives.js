"use strict";

philoApp.directive('concordance', ['$rootScope', '$http', 'request', function($rootScope, $http, request) {
    if ($rootScope.philoConfig.dico_citation) {
        var templateType = "concordance_dico.html";
    } else {
		var templateType = "concordance.html";
	}
    return {
        templateUrl: 'app/components/concordanceKwic/' + templateType,
		replace: true,
        link: function(scope) {
			scope.concKwic.resultsPromise.then(function(results) {
				scope.results = results.data;
				scope.concKwic.description = angular.extend({}, scope.results.description, {resultsLength: scope.results.results_length});
				scope.concKwic.loading = false;
			}).catch(function(response) {
				scope.results = {};
				scope.concKwic.description = {};
				scope.concKwic.loading = false;
			});
            scope.moreContext = function($event, resultNumber) {
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
        }
    }
}]);

philoApp.directive('kwic', ['$rootScope', '$location', '$http', 'URL', 'request', 'defaultDiacriticsRemovalMap', 'descriptionValues',
							function($rootScope, $location, $http, URL, request, defaultDiacriticsRemovalMap, descriptionValues) {
	var removeDiacritics = function(str) {
		var changes = defaultDiacriticsRemovalMap.map;
		for(var i=0; i<changes.length; i++) {
			str = str.replace(changes[i].letters, changes[i].base);
		}
		return str;
	}
	var sortResults = function(results, metadataSortKey) {
		results.sort(function(a,b) {
			if (isNaN(a[0]) && !isNaN(b[0])) {
                return -1;
            }
			if (isNaN(b[0]) && !isNaN(a[0])) {
                return 1;
            }
            var x = removeDiacritics(a[0]);
            var y = removeDiacritics(b[0]);
            
			if (x < y) {
				return -1;
			}
			if (x > y) {
				return 1
			}
			if (metadataSortKey) {
				if (metadataSortKey != 'date') {
                    var m = removeDiacritics(a[2][metadataSortKey]);
					var n = removeDiacritics(b[2][metadataSortKey]);
                } else {
					var m = parseInt(a[2][metadataSortKey]);
					var n = parseInt(b[2][metadataSortKey]);
				}
				if (m < n) {
					return -1;
				}
				if (m > n) {
					return 1
				}
            }
			return 0;
        });
		return results;
	}
	var mergeLists = function(list1, list2) {
		for (var i=0; i < list2.length; i+=1) {
			list1.push(list2[i]);
		}
		return list1;
	}
	var recursiveLookup = function(scope, queryParams, direction, hitsDone) {
		request.script(queryParams, {direction: direction, hits_done: hitsDone})
		.then(function(response) {
			var hitsDone = response.data.hits_done;
			if (scope.sortedResults.length === 0) {
				scope.sortedResults = response.data.results;
			} else {
				scope.sortedResults = mergeLists(scope.sortedResults, response.data.results)
			}
			if (hitsDone < descriptionValues.resultsLength) {
				recursiveLookup(scope, queryParams, direction, hitsDone);
			} else {
				scope.sortedResults = sortResults(scope.sortedResults, scope.formData.metadata_sorting_field);
				queryParams.start = '0';
				queryParams.end = '0';
				var metadataField = angular.copy(queryParams.metadata_sorting_field);
				queryParams.metadata_sorting_field = "";
				descriptionValues.sortedKwic = {
					results: scope.sortedResults,
					queryObject: angular.extend({}, queryParams, {direction: direction}),
					metadataField: metadataField
				}
				
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
			JSON.stringify({
				results: scope.sortedResults.slice(start,end),
				hits_done: hitsDone,
				query_string: URL.objectToString($location.search()),
				start: start,
				end: end
				})
			)
		.then(function(response) {
			scope.results = response.data;
			console.log(scope.results.description.start)
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
				var target = $(event.currentTarget).find('.full_biblio');
				target.addClass('show');
			}
			
			scope.hideFullBiblio = function(event) {
				var target = $(event.currentTarget).find('.full_biblio');
				target.removeClass('show');
			}
			
			// Sorting fields
			scope.metadataSortingFields = [];
			for (var i=0; i < $rootScope.philoConfig.kwic_metadata_sorting_fields.length; i+=1) {
				var field = $rootScope.philoConfig.kwic_metadata_sorting_fields[i];
				if (field in scope.philoConfig.metadata_aliases) {
					var label = scope.philoConfig.metadata_aliases[field];
                    scope.metadataSortingFields.push({label:label, field:field});
                } else {
					scope.metadataSortingFields.push({label: field[0].toUpperCase() + field.slice(1), field: field});
				}
			}
			if ($rootScope.formData.metadata_sorting_field) {
                if ($rootScope.formData.metadata_sorting_field in scope.philoConfig.metadata_aliases) {
					scope.kwicMetaSelection = scope.philoConfig.metadata_aliases[$rootScope.formData.metadata_sorting_field];
                } else {
					scope.kwicMetaSelection = $rootScope.formData.metadata_sorting_field[0].toUpperCase() + $rootScope.formData.metadata_sorting_field.slice(1);
				}
            } else {
				scope.kwicMetaSelection =  "None";
            }
			scope.updateMetadataSorting = function(metadata) {
				scope.kwicMetaSelection = metadata.label;
				$rootScope.formData.metadata_sorting_field = metadata.field
			}
			scope.kwicWordSelection = $rootScope.formData.direction || 'None';
			scope.updateWordSorting = function(direction) {
				if (direction) {
                    scope.kwicWordSelection = direction;
                } else {
					scope.kwicWordSelection = "None";
				}
				$rootScope.formData.direction = direction;
			}
			scope.sortResults = function() {
				var urlString = URL.objectToUrlString($rootScope.formData);
				$location.url(urlString);
			}
			
			if (typeof(scope.formData.direction) !== 'undefined' && scope.formData.direction !== "" || typeof(scope.formData.metadata_sorting_field) !== 'undefined' && scope.formData.metadata_sorting_field !== "") {
                scope.concKwic.resultsPromise.then(function(results) { // Rerun normal KWIC query since this could be a reload
					scope.concKwic.description = angular.extend({}, results.data.description, {resultsLength: results.data.results_length});
					var queryParams = $location.search();
					queryParams.script = 'get_neighboring_words.py';
					queryParams.max_time = 10;
					scope.sortedResults = [];
					queryParams.start = '0';
					queryParams.end = "0";
					queryParams.metadata_sorting_field = "";
					var currentQueryObject = angular.extend({}, queryParams, {direction: scope.formData.direction});
					if (angular.equals(descriptionValues.sortedKwic.queryObject, currentQueryObject)) {
						scope.sortedResults = descriptionValues.sortedKwic.results;
						if (scope.formData.metadata_sorting_field !== descriptionValues.sortedKwic.metadataField) {
                            scope.sortedResults = sortResults(scope.sortedResults, scope.formData.metadata_sorting_field)
                        }
                        getKwicResults(scope, results.data.results_length)
						scope.concKwic.loading = false;
                    } else {
						recursiveLookup(scope, queryParams, scope.formData.direction, 0);
					}
				}).catch(function(response) {
					scope.results = {};
					scope.concKwic.description = {};
					scope.concKwic.loading = false;
				});
            } else {
				scope.concKwic.resultsPromise.then(function(results) {
					scope.results = results.data;
					scope.concKwic.description = angular.extend({}, scope.results.description, {resultsLength: scope.results.results_length});
					scope.concKwic.loading = false;
				}).catch(function(response) {
					scope.results = {};
					scope.concKwic.description = {};
					scope.concKwic.loading = false;
				});				
            }
        }
    }
}]);

philoApp.directive('bibliography', ['$rootScope', function($rootScope) {
	if ($rootScope.philoConfig.dico_citation) {
        var templateType = "bibliography_dico.html";
    } else {
		var templateType = "bibliography.html";
	}
    return {
        templateUrl: 'app/components/concordanceKwic/' + templateType,
		replace: true,
		link: function(scope) {
			scope.concKwic.resultsPromise.then(function(results) {
				scope.results = results.data;
				scope.concKwic.description = angular.extend({}, scope.results.description, {resultsLength: scope.results.results_length});
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
			href: URL.objectToUrlString(scope.formData, {report: 'kwic', direction: '', metadata_sorting_field: ''})
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
        template: ['<div id="page-links" class="btn-group">',
						'<a href="{{ page.href }}" class="btn btn-default btn-lg {{ page.active }}" ng-repeat="page in pages">{{ page.display }}</a>',
				   '</div>'].join(''),
		replace: true,
        link: function(scope, element, attrs) {
                scope.$watch(function() {
                    return scope.results;
                    }, function() {
                    scope.pages = buildPages(scope, scope.concKwic.description.more_pages);
                }, true);
        }
    }
}]);
