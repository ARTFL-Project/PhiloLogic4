(function() {
    "use strict";

    angular
        .module('philoApp')
        .directive('textObject', textObject)
        .directive('tocSidebar', tocSidebar)
        .directive('scrollTo', scrollTo)
        .directive('navigationBar', navigationBar)
        .directive('highlight', highlight)
        .directive('compileTemplate', compileTemplate)
        .directive('pageImageLink', pageImageLink)
        .directive('inlineImg', inlineImg)
        .directive('noteRef', noteRef)
        .directive('note', note);


    function textObject($routeParams, $timeout, $location, request, textNavigationValues) {
        var getTextObject = function(scope) {
            scope.textNav.textRendered = false;
            scope.textObjectURL = $routeParams;
            scope.philoID = scope.textObjectURL.pathInfo.split('/').join(' ');
            if ("byte" in scope.textObjectURL) {
                scope.byteOffset = scope.textObjectURL.byte;
            } else {
                scope.byteOffset = ''
            }
            scope.textObject = {
                citation: textNavigationValues.citation
            }; // Make sure we don't change citation if it has been already filled
            scope.$broadcast('domloaded');
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
                    scope.textNav.graphics = response.data.imgs.graphics;
                    if (scope.byteOffset.length > 0) {
                        scope.highlight = true;
                    } else {
                        scope.highlight = false;
                    }
                    scope.textNav.loading = false;

                    var hash = $location.hash(); // For note link back
                    if (hash) {
                        $timeout(function() {
                            angular.element('#' + hash).css({
                                    backgroundColor: 'red',
                                    color: 'white'
                                })
                                .velocity("scroll", {
                                    duration: 200,
                                    offset: -50
                                });
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
                for (var i = 0; i < allImgs.length; i++) {
                    var img = allImgs[i];
                    if (currentObjImgs.indexOf(img) === -1) {
                        scope.beforeObjImgs.push(scope.philoConfig.page_images_url_root + '/' + img);
                    } else {
                        beforeIndex = i;
                        break;
                    }
                }
                for (var i = beforeIndex; i < allImgs.length; i++) {
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
            link: function(scope, element, attrs) {
                getTextObject(scope);
            }
        }
    }

    function tocSidebar($routeParams, $timeout, request, textNavigationValues) {
        var getTableOfContents = function(scope, philoId) {
            request.script({
                    philo_id: philoId,
                    script: 'get_table_of_contents.py'
                })
                .then(function(response) {
                    scope.tocElements = response.data.toc;
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
                    angular.element("#show-toc").removeAttr("disabled");
                });
        }
        return {
            templateUrl: 'app/components/textNavigation/tocSidebar.html',
            replace: true,
            link: function(scope, element, attrs) {
                scope.tocPosition = '';
                var philoId = $routeParams.pathInfo.split('/').join(' ');
                var docId = philoId.split(' ')[0];
                scope.currentPhiloId = philoId;
                if (docId !== textNavigationValues.tocElements.docId) {
                    getTableOfContents(scope, philoId);
                } else {
                    scope.tocElements = textNavigationValues.tocElements.elements;
                    scope.start = textNavigationValues.tocElements.start;
                    scope.end = textNavigationValues.tocElements.end;
                    angular.element("#show-toc").removeAttr("disabled");
                }
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
                    textNavigationValues.tocElements.start = textNavigationValues.tocElements.start + index - 100;
                    if (textNavigationValues.tocElements.start < 0) {
                        textNavigationValues.tocElements.start = 0;
                    }
                    textNavigationValues.tocElements.end = textNavigationValues.tocElements.end - index + 100;
                    scope.textNav.goToTextObject(philoId);
                }
            }
        }
    }

    function scrollTo($timeout) {
        return {
            link: function(scope, element, attrs) {
                attrs.$observe('scrollTo', function(id) {
                    if (id) {
                        $timeout(function() {
                            var target = angular.element('[id="' + id + '"]');
                            element.scrollTo(target);
                        }, 0)
                    }
                });
            }
        }
    }

    function navigationBar() {
        var setUpNavBar = function(scope) {
            if (scope.textObject.next === "" || typeof(scope.textObject.next) === 'undefined') {
                angular.element('#next-obj').attr('disabled', 'disabled');
            } else {
                angular.element('#next-obj').removeAttr('disabled');
            }
            if (scope.textObject.prev === "" || typeof(scope.textObject.prev) === 'undefined') {
                angular.element("#prev-obj").attr('disabled', 'disabled');
            } else {
                angular.element("#prev-obj").removeAttr('disabled');
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
    }

    function highlight($timeout) {
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
                    angular.element("body").velocity('scroll', {
                        duration: 800,
                        easing: 'easeOutQuad',
                        offset: wordOffset - 60,
                        complete: function() {
                            element.parents('.note-content').prev('.note').trigger('focus');
                        }
                    });
                } else {
                    angular.element("body").velocity('scroll', {
                        duration: 800,
                        easing: 'easeOutQuad',
                        offset: wordOffset - 100
                    });
                }
            }, 200);
        }
        return {
            restrict: 'C',
            link: function(scope, element) {
                if (element.is(angular.element('#book-page .highlight').eq(0))) {
                    scroll(element);
                }
            }
        }
    }

    function compileTemplate($compile, $parse) {
        // Credits to http://stackoverflow.com/questions/20297638/call-function-inside-sce-trustashtml-string-in-angular-js
        return {
            link: function(scope, element, attr) {
                var parsed = $parse(attr.ngBindHtml);

                function getStringValue() {
                    return (parsed(scope) || '').toString();
                }

                //Recompile if the template changes
                scope.$watch(getStringValue, function() {
                    $compile(element, null, -9999)(scope); //The -9999 makes it skip directives so that we do not recompile ourselves
                });
            }
        }
    }

    function pageImageLink($window) {
        var launchGallery = function() {
            var imageList = [];
            angular.element('#book-page').find('a.page-image-link').each(function() {
                imageList.push(angular.element(this).attr('href'));
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
                    angular.element('#full-size-image').off();
                    angular.element('#full-size-image').click(function() {
                        var imageIndex = scope.gallery.getIndex();
                        var img = angular.element("#blueimp-gallery").find("[data-index='" + imageIndex + "'] img");
                        $window.open(img.attr('src'));
                    });
                });
                element.on('$destroy', function() {
                    angular.element('#full-size-image').off();
                });
            }
        }
    }

    function inlineImg($window) {
        var launchGallery = function(scope) {
            var imageList = [];
            angular.element('#book-page').find('img.inline-img').each(function() {
                imageList.push(angular.element(this).attr('src'));
            });
            return imageList;
        }
        return {
            restrict: 'A',
            link: function(scope, element) {
                var index = scope.textNav.graphics.indexOf(element.attr('src'));
                element.click(function(e) {
                    e.preventDefault();
                    scope.gallery = blueimp.Gallery(scope.textNav.graphics, {
                        onopen: function() {
                            this.index = index;
                        },
                        continuous: false,
                        thumbnailIndicators: false
                    });
                    angular.element('#full-size-image').off();
                    angular.element('#full-size-image').click(function() {
                        var imageIndex = scope.gallery.getIndex();
                        var img = angular.element("#blueimp-gallery").find("[data-index='" + imageIndex + "'] img");
                        $window.open(img.attr('src'));
                    });
                });
                element.on('$destroy', function() {
                    angular.element('#full-size-image').off();
                });
            }
        }
    }

    function noteRef(request, $location) {
        return {
            restrict: 'C',
            link: function(scope, element) {
                element.on('click', function() {
                    var philoID = $location.path().replace("/navigate/", "").replace("/", " ");
                    request.script({
                            script: "get_notes.py",
                            target: element.attr('target'),
                            philo_id: philoID
                        })
                        .then(function(response) {
                            var data = response.data;
                            element.popover({
                                trigger: 'manual',
                                content: function() {
                                    return data.text;
                                }
                            });
                            if (data.text != '') {
                                element.popover("show");
                            } else {
                                alert('PhiloLogic was unable to retrieve a note at the given link')
                            }
                            angular.element('body').on('click', function(e) {
                                //did not click a popover toggle, or icon in popover toggle, or popover
                                if (angular.element(e.target).data('toggle') !== 'popover') {
                                    element.popover('hide');
                                }
                            });
                        });
                });
                element.on('$destroy', function() {
                    element.popover('destroy');
                    element.off();
                    angular.element('body').off('click');
                })
            }
        }
    }

    function note() {
        return {
            restrict: 'C',
            link: function(scope, element) {
                element.popover({
                    animate: true,
                    trigger: 'focus',
                    html: true,
                    content: function() {
                        return element.next('.note-content').html();
                    }
                });
                element.on('$destroy', function() {
                    element.popover('destroy');
                });
            }
        }
    }
})();