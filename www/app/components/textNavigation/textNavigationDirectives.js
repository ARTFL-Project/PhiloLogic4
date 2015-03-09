"use strict";

philoApp.directive('textObject', ['$routeParams', 'request', 'textNavigationValues', function($routeParams, request, textNavigationValues) {
    var getTextObject = function(scope) {
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
                setTimeout(createNoteLink, 500)
            } else {
                scope.highlight = false;
            }
            scope.loading = false;
        });
    }
    var createNoteLink = function() {
        $('.note-ref, .note').click(function() {
            if ($(this).hasClass == ".note") {
                $(this).popover({animate: true, trigger: 'focus', html: true, content: function() {
                    return $(this).next('.note-content').html();
                }});
            } else {
                var link = $(this).data('ref');
                var element = $(this);
                $.getJSON(link, function(data) {
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
            }
        });
    }
    return {
        templateUrl: 'app/components/textNavigation/textObject.html',
        link: function(scope,element, attrs) {
            getTextObject(scope);
        }
    }    
}]);

philoApp.directive('tocSidebar', ['$routeParams', 'request', 'textNavigationValues', function($routeParams, request, textNavigationValues) {
    var getTableOfContents = function(scope) {
        var philoId = $routeParams.pathInfo.split('/').join(' ');
        request.script({
            philo_id: philoId,
            script: 'get_table_of_contents.py'
        })
        .then(function(response) {
            var tocObject = response.data;
            scope.tocElements = filterTocElements(tocObject.toc, philoId);
            textNavigationValues.tocElements = scope.tocElements;
            scope.tocDone = true;
        });
    }
    var filterTocElements = function(tocElements, philoId) {
        var filtered = [];
        var limit = 200;
        var match = false;
        var count = 0;
        for (var i=0; i < tocElements.length; i++) {
            if (match) {
                count += 1
            }
            var element = tocElements[i];
            if (element.philo_id === philoId) {
                element.currentObj = "current-obj";
                match = i;
            } else {
                element.currentObj = "";
            }
            filtered.push(element)
            if (count == limit) {
                break
            }
        }
        if ((match - limit) < 0) {
            return filtered;
        } else {
            return filtered.slice(match - limit);
        }
    }
    return {
        templateUrl: 'app/components/textNavigation/tocSidebar.html',
        link: function(scope, element, attrs) {
            if (!scope.tocElements) {
                getTableOfContents(scope);
            } else {
                var philoId = $routeParams.pathInfo.split('/').join(' ');
                scope.tocElements = filterTocElements(scope.tocElements, philoId);
                textNavigationValues = scope.tocElements;
            }
            element.on('$destroy', function() {
                $(window).off('.affix');
            });
        }
    }
}]);

philoApp.directive('navigationBar', function() {
    var setUpNavBar = function(scope) {
        if (scope.textObject.next === "") {
            $('#next-obj').attr('disabled', 'disabled');
        } else {
            $('#next-obj').removeAttr('disabled');
        }
        if (scope.textObject.prev === "") {
            $("#prev-obj").attr('disabled', 'disabled');
        } else {
            $("#prev-obj").removeAttr('disabled');
        }
    }    
    return {
        templateUrl: 'app/components/textNavigation/navigationBar.html',
        link: function(scope, element, attrs) {
            setUpNavBar(scope);
            scope.navBar = true; // it's now drawn and shouldn't be removed
            attrs.$observe('tocDone', function(tocDone) {
                if (tocDone) {
                    $("#show-toc").removeAttr("disabled");
                }
            });
        }
    }
});

philoApp.directive('affix', function() {
    return {
        restrict: 'A',
        link: function(scope, element, attrs) {
            if (attrs.affix !== '') {
                var offsetTop = element.offset().top - parseInt(attrs.affix);
            } else {
                var offsetTop = element.offset().top;
            }
            element.affix({ offset: { top: function() {
                return (this.top = offsetTop)
                }
            }});
            element.on('affix.bs.affix', function() {
                $(this).addClass('fixed');
                $('#back-to-top').addClass('fixed');
            });
            element.on('affix-top.bs.affix', function() {
                $(this).removeClass('fixed');
                $('#back-to-top').removeClass('fixed');
            });
            element.on('$destroy', function() {
                $(window).off('.affix');
                element.removeData('affix').removeClass('affix affix-top affix-bottom');
            });
        }
    }
});

philoApp.directive('scrollToHighlight', ['$timeout', function($timeout) {
    var scroll = function() {
        $timeout(function() {
            if ($('.highlight').length) {
                var wordOffset = $('.highlight').eq(0).offset().top;
                if (wordOffset == 0) {
                    var note = $('.highlight').parents('.note-content');
                    note.show(); // The highlight is in a hidden note
                    wordOffset = $('.highlight').offset().top;
                    $('.highlight').parents('.note-content').hide();
                }
                if ($('.highlight').eq(0).parents('.note-content').length) {
                    $("body").velocity('scroll', {duration: 800, easing: 'easeOutCirc', offset: wordOffset - 60, complete: function() {
                        $('.highlight').parents('.note-content').prev('.note').trigger('focus');}}
                    );
                } else {
                    $("body").velocity('scroll', {duration: 800, easing: 'easeOutCirc', offset: wordOffset - 100});
                }
            }
        });
    }
    return {
        restrict: 'A',
        link: function(scope, element, attrs) {
            if (attrs.scrollToHighlight) {
                scroll();
            }
            attrs.$observe('scrollToHighlight', function(scrollBool) {
                if (scrollBool) {
                    scroll();
                }
            })
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
                    continuous: false
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