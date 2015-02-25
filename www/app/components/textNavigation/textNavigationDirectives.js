"use strict";

philoApp.directive('textObject', ['$routeParams', '$http', 'URL', 'textObjectCitation', function($routeParams, $http, URL, textObjectCitation) {
    var getTextObject = function(scope) {
        scope.textObjectURL = $routeParams;
        scope.philoID = scope.textObjectURL.pathInfo.split('/').join(' ');
        if ("byte" in scope.textObjectURL) {
            scope.byteOffset = scope.textObjectURL.byte;
        } else {
            scope.byteOffset = ''
        }
        scope.textObject = {citation: textObjectCitation.citation}; // Make sure we don't change citation if it has been already filled
        var request = scope.philoConfig.db_url + '/' + URL.query({report: "navigation", philo_id: scope.philoID, byte: scope.byteOffset});
        $http.get(request).then(function(response) {
            scope.textObject = response.data;
            textObjectCitation.citation = response.data.citation;
            if (scope.byteOffset.length > 0 ) {
                setTimeout(scrollToHighlight, 500);
                setTimeout(createNoteLink, 500)
            }
            scope.loading = false;
        });
    }
    var scrollToHighlight = function() {
        var word_offset = $('.highlight').eq(0).offset().top;
        if (word_offset == 0) {
            var note = $('.highlight').parents('.note-content');
            note.show(); // The highlight is in a hidden note
            word_offset = $('.highlight').offset().top;
            $('.highlight').parents('.note-content').hide();
        }
        if ($('.highlight').eq(0).parents('.note-content').length) {
            $("body").velocity('scroll', {duration: 800, easing: 'easeOutCirc', offset: word_offset - 60, complete: function() {
                $('.highlight').parents('.note-content').prev('.note').trigger('focus');}}
            );
        } else {
            $("body").velocity('scroll', {duration: 800, easing: 'easeOutCirc', offset: word_offset - 100});
        }
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
                //element.popover({trigger: 'manual'});
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
        link: function(scope) {
            getTextObject(scope);
        }
    }    
}]);

philoApp.directive('tocSidebar', ['$routeParams', '$http', '$timeout', 'URL', 'textObjectCitation', function($routeParams, $http, $timeout, URL, textObjectCitation) {
    var getTableOfContents = function(scope) {
        var philoID = $routeParams.pathInfo.split('/').join(' ');
        var request = scope.philoConfig.db_url + '/' + URL.query({philo_id: philoID, script: 'get_table_of_contents.py'});
        $http.get(request).then(function(response) {
            scope.tocObject = response.data;
            scope.tocDone = true;
            $timeout(function() {
                $('#toc-container').affix({ offset: { top: function() {
                    return (this.top = $('#toc-container').offset().top + 30)
                    }
                }});
                $('#toc-container').on('affix.bs.affix', function() {
                    $("#toc-container").addClass('fixed');
                    scope.adjustTocHeight();
                });
                $('#toc-container').on('affix-top.bs.affix', function() {
                    $("#toc-container").removeClass('fixed').css('position', 'static');
                    scope.adjustTocHeight();
                });
            });
        });
    }
    return {
        templateUrl: 'app/components/textNavigation/tocSidebar.html',
        link: function(scope, element, attrs) {
            getTableOfContents(scope);
        }
    }
}]);

philoApp.directive('navigationBar', ['$routeParams', '$http', '$timeout', 'URL', 'textObjectCitation', function($routeParams, $http, $timeout, URL, textObjectCitation) {
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
            applyAffix()
            function applyAffix() {
                $timeout(function() {
                    $('#nav-buttons').affix({ offset: { top: function() {
                        return (this.top = $('#nav-buttons').offset().top)
                        }
                    }});
                    $('#nav-buttons').on('affix.bs.affix', function() {
                        $(this).addClass('fixed');
                        $('#back-to-top').velocity("stop").velocity('fadeIn', {duration: 200});
                    });
                    $('#nav-buttons').on('affix-top.bs.affix', function() {
                        $(this).removeClass('fixed');
                        $('#back-to-top').velocity("stop").velocity('fadeOut', {duration: 200});
                    });
                });
            }
            
            attrs.$observe('tocDone', function(tocDone) {
                if (tocDone) {
                    $("#show-toc").removeAttr("disabled");
                }
            });
        }
    }
}]);