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
            } else {
                scope.highlight = false;
            }
            scope.textNav.loading = false;
        });
    }
    return {
        templateUrl: 'app/components/textNavigation/textObject.html',
        replace: true,
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
            if (match !== false) {
                count++;
            }
            var element = tocElements[i];
            if (element.philo_id === philoId) {
                element.currentObj = "current-obj";
                match = i;
            } else {
                element.currentObj = "";
            }
            filtered.push(element)
            if (count === limit) {
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
        replace: true,
        link: function(scope, element, attrs) {
            if (!scope.tocElements) {
                getTableOfContents(scope);
            } else {
                var philoId = $routeParams.pathInfo.split('/').join(' ');
                scope.tocElements = filterTocElements(scope.tocElements, philoId);
                textNavigationValues = scope.tocElements;
            }
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
            attrs.$observe('tocDone', function(tocDone) {
                if (tocDone) {
                    $("#show-toc").removeAttr("disabled");
                }
            });
            attrs.$observe('prev', function(prev) {
                setUpNavBar(scope);
            });
            attrs.$observe('next', function(prev) {
                setUpNavBar(scope);
            });
        }
    }
});

philoApp.directive('highlight', function() {
    var scroll = function(element) {
        var wordOffset = element.eq(0).offset().top;
        if (wordOffset == 0) {
            var note = element.parents('.note-content');
            note.show(); // The highlight is in a hidden note
            wordOffset = element.offset().top;
            element.parents('.note-content').hide();
        }
        if (element.eq(0).parents('.note-content').length) {
            $("body").velocity('scroll', {duration: 800, easing: 'easeOutCubic', offset: wordOffset - 60, complete: function() {
                element.parents('.note-content').prev('.note').trigger('focus');}}
            );
        } else {
            $("body").velocity('scroll', {duration: 800, easing: 'easeOutCirc', offset: wordOffset - 100});
        }
    }
    return {
        restrict: 'C',
        link: function(scope, element) {
            if (element.is($('#book-page .highlight').eq(0))) {
                scroll(element);
            }
        }
    }
});

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