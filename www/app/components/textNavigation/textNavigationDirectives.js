"use strict";

philoApp.directive('textObject', ['$routeParams', '$timeout', '$location', 'request', 'textNavigationValues',
								  function($routeParams, $timeout, $location, request, textNavigationValues) {
    var getTextObject = function(scope) {
		scope.textNav.textRendered = false;
        scope.textObjectURL = $routeParams;
        scope.philoID = scope.textObjectURL.pathInfo.split('/').join(' ');
        if ("byte" in scope.textObjectURL) {
            scope.byteOffset = scope.textObjectURL.byte;
        } else {
            scope.byteOffset = ''
        }
        scope.textObject = {citation: textNavigationValues.citation}; // Make sure we don't change citation if it has been already filled
        request.report({
            report: "navigation",
            philo_id: scope.philoID,
            byte: scope.byteOffset
        })
        .then(function(response) {
            scope.textObject = response.data;
            textNavigationValues.textObject = response.data;
            textNavigationValues.citation = response.data.citation;
            textNavigationValues.navBar = true;
            if (scope.byteOffset.length > 0 ) {
                scope.highlight = true;
            } else {
                scope.highlight = false;
            }
            scope.textNav.loading = false;
			$timeout(function() {
				scope.$broadcast('domloaded');
			}, 0);
			
			var hash = $location.hash(); // For note link back
			if (hash) {
				$timeout(function() {
					$('#' + hash).css({backgroundColor: 'red', color: 'white'})
					.velocity("scroll", {duration: 200, offset: -50});
				});
			}
			insertPageLinks(scope, response.data.imgs);
        })
		.catch(function(response) {
			scope.textNav.loading = false;
		});
    }
	var insertPageLinks = function(scope, imgObj) {
		var currentObjImgs = imgObj.current_obj_img;
		var allImgs = imgObj.all_imgs;
		scope.beforeObjImgs = [];
		scope.afterObjImgs = [];
		if (currentObjImgs.length > 0) {
            var beforeIndex = 0;
			for (var i=0; i < allImgs.length; i++) {
				var img = allImgs[i];
				if (currentObjImgs.indexOf(img) === -1) {
					scope.beforeObjImgs.push(scope.philoConfig.page_images_url_root + '/' + img);
				} else {
					beforeIndex = i;
					break;
				}
			}
			for (var i=beforeIndex; i < allImgs.length; i++) {
				var img = allImgs[i];
				if (currentObjImgs.indexOf(img) === -1) {
					scope.afterObjImgs.push(scope.philoConfig.page_images_url_root + '/' + img);
				}
			}
        }
	}
    return {
        templateUrl: 'app/components/textNavigation/textObject.html',
        replace: true,
        link: function(scope,element, attrs) {
            getTextObject(scope);
        }
    }    
}]);

philoApp.directive('tocSidebar', ['$routeParams', '$timeout', 'request', 'textNavigationValues',
								  function($routeParams, $timeout, request, textNavigationValues) {
    var getTableOfContents = function(scope, philoId) {
        request.script({
            philo_id: philoId,
            script: 'get_table_of_contents.py'
        })
        .then(function(response) {
            scope.tocElements = response.data.toc;
			scope.currentPhiloId = response.data.philo_id.join(' ');
			scope.start = response.data.current_obj_position - 100;
			if (scope.start < 0) {
                scope.start = 0;
            }
			scope.end = response.data.current_obj_position + 100;
			
			textNavigationValues.tocElements = {
				docId: philoId.split(' ')[0],
				elements: scope.tocElements,
				start: scope.start,
				end: scope.end
			};
			$("#show-toc").removeAttr("disabled");
        });
    }
    return {
        templateUrl: 'app/components/textNavigation/tocSidebar.html',
        replace: true,
        link: function(scope, element, attrs) {
			scope.tocPosition = '';
			var philoId = $routeParams.pathInfo.split('/').join(' ');
			var docId = philoId.split(' ')[0];
			scope.$on('domloaded', function() {
				$timeout(function() {
					if (docId !== textNavigationValues.tocElements.docId) {
						getTableOfContents(scope, philoId);
					} else {
						scope.currentPhiloId = philoId;
						scope.tocElements = textNavigationValues.tocElements.elements;
						scope.start = textNavigationValues.tocElements.start;
						scope.end = textNavigationValues.tocElements.end;
						$("#show-toc").removeAttr("disabled");
					}
				}, 0);
				scope.loadBefore = function() {
					var firstElement = scope.tocElements[scope.start - 2].philo_id;
					scope.start -= 200;
					if (scope.start < 0) {
                        scope.start = 0;
                    }
					scope.tocPosition = firstElement;
				}
				scope.loadAfter = function() {
					scope.end += 200;
				}
				scope.textObjectSelection = function(philoId, index) {
					textNavigationValues.tocElements.start = index - 100;
					if (textNavigationValues.tocElements.start < 0) {
                        textNavigationValues.tocElements.start = 0;
                    }
					textNavigationValues.tocElements.end = index + 100;
					scope.textNav.goToTextObject(philoId);
				}
			});
        }
    }
}]);

philoApp.directive('scrollTo', ['$timeout', function($timeout) {
	return {
		link: function(scope, element, attrs) {
			attrs.$observe('scrollTo', function(id) {
				if (id) {
                    $timeout(function() {
						var target = $('[id="' + id + '"]');
						element.scrollTo(target);
					}, 0)
                }
			});
		}
	}
}]);

philoApp.directive('navigationBar', function() {
    var setUpNavBar = function(scope) {
        if (scope.textObject.next === "" || typeof(scope.textObject.next) === 'undefined') {
            $('#next-obj').attr('disabled', 'disabled');
        } else {
            $('#next-obj').removeAttr('disabled');
        }
        if (scope.textObject.prev === "" || typeof(scope.textObject.prev) === 'undefined') {
            $("#prev-obj").attr('disabled', 'disabled');
        } else {
            $("#prev-obj").removeAttr('disabled');
        }
    }    
    return {
        templateUrl: 'app/components/textNavigation/navigationBar.html',
        replace: true,
        link: function(scope, element, attrs) {
            scope.textNav.navBar = true;
            attrs.$observe('prev', function(prev) {
                setUpNavBar(scope);
            });
            attrs.$observe('next', function(prev) {
                setUpNavBar(scope);
            });
        }
    }
});

philoApp.directive('highlight', ['$timeout', function($timeout) {
    var scroll = function(element) {
        $timeout(function() {
            var wordOffset = element.eq(0).offset().top;
            if (wordOffset == 0) {
                var note = element.parents('.note-content');
                note.show(); // The highlight is in a hidden note
                wordOffset = element.offset().top;
                element.parents('.note-content').hide();
            }
            if (element.eq(0).parents('.note-content').length) {
                $("body").velocity('scroll', {duration: 800, easing: 'easeOutQuad', offset: wordOffset - 60, complete: function() {
                    element.parents('.note-content').prev('.note').trigger('focus');}}
                );
            } else {
                $("body").velocity('scroll', {duration: 800, easing: 'easeOutQuad', offset: wordOffset - 100});
            }
        }, 200);
    }
    return {
        restrict: 'C',
        link: function(scope, element) {
            if (element.is($('#book-page .highlight').eq(0))) {
                scroll(element);
            }
        }
    }
}]);

philoApp.directive('compileTemplate', ['$compile', '$parse', function($compile, $parse) {
    // Credits to http://stackoverflow.com/questions/20297638/call-function-inside-sce-trustashtml-string-in-angular-js
    return {
        link: function(scope, element, attr){
            var parsed = $parse(attr.ngBindHtml);
            function getStringValue() { return (parsed(scope) || '').toString(); }

            //Recompile if the template changes
            scope.$watch(getStringValue, function() {
                $compile(element, null, -9999)(scope);  //The -9999 makes it skip directives so that we do not recompile ourselves
            });
        }         
    }
}]);

philoApp.directive('pageImageLink', function() {
    var launchGallery = function() {
        var imageList = [];
        $('#book-page').find('a.page-image-link').each(function() {
            imageList.push($(this).attr('href'));
        });
        return imageList;
    }
    return {
        restrict: 'C',
        link: function(scope, element) {
            element.click(function(e) {
                e.preventDefault();
                scope.gallery = blueimp.Gallery(launchGallery(), {
                    onopen: function() {
                        this.index = element.index('a.page-image-link');
                    },
                    continuous: false,
					thumbnailIndicators: false
                });
                $('#full-size-image').off();
                $('#full-size-image').click(function() {
                    var imageIndex = scope.gallery.getIndex();
                    var img = $("#blueimp-gallery").find("[data-index='" + imageIndex + "'] img");
                    window.open(img.attr('src'));
                });
            });
            element.on('$destroy', function() {
                $('#full-size-image').off();
            });
        }
    }
});

philoApp.directive('inlineImg', function() {
    var launchGallery = function() {
        var imageList = [];
        $('#book-page').find('img.inline-img').parent('.inline-img-container').each(function() {
            imageList.push($(this).attr('href'));
        });
        return imageList;
    }
    return {
        restrict: 'C',
        link: function(scope, element) {
            element.click(function(e) {
                e.preventDefault();
                scope.gallery = blueimp.Gallery(launchGallery(), {
                    onopen: function() {
                        this.index = element.index('img.inline-img');
                    },
                    continuous: false,
					thumbnailIndicators: false
                });
                $('#full-size-image').off();
                $('#full-size-image').click(function() {
                    var imageIndex = scope.gallery.getIndex();
                    var img = $("#blueimp-gallery").find("[data-index='" + imageIndex + "'] img");
                    window.open(img.attr('src'));
                });
            });
            element.on('$destroy', function() {
                $('#full-size-image').off();
            });
        }
    }
});

philoApp.directive('noteRef', ['$http', function($http) {
    return {
        restrict: 'C',
        link: function(scope, element) {
            element.on('click', function() {
                $http.get(element.data('ref')).then(function(response) {
                    var data = response.data;
                    element.popover({trigger: 'manual', content: function() {
                        return data.text;
                    }});
                    if (data.text != '') {
                        element.popover("show");
                    } else {
                        alert('PhiloLogic was unable to retrieve a note at the given link')
                    }
                    $('body').on('click', function (e) {
                        //did not click a popover toggle, or icon in popover toggle, or popover
                        if ($(e.target).data('toggle') !== 'popover') { 
                            element.popover('hide');
                        }
                    });
                });
            });
            element.on('$destroy', function() {
                element.popover('destroy');
                element.off();
                $('body').off('click');
            })
        }
    }    
}]);

philoApp.directive('note', function() {
    return {
        restrict: 'C',
        link: function(scope, element) {
            element.popover({animate: true, trigger: 'focus', html: true, content: function() {
                return element.next('.note-content').html();
            }});
            element.on('$destroy', function() {
                element.popover('destroy');
            });
        }
    }
});

philoApp.directive('noteLinkBack', ['$http', '$location', function($http, $location) {
	return {
		restrict: 'A',
		link: function(scope, element, attrs) {
			var linkBack = attrs['noteLinkBack'];
			element.click(function() {
				$http.get(linkBack).success(function(data) {
					$location.url(data.link);
				});	
			});
			element.on('$destroy', function() {
                element.off('click');
            });
		}
	}
}])