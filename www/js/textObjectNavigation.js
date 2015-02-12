"use strict";

philoApp.controller('textObjectNavigation', ['$scope', '$rootScope', '$http', '$location', '$routeParams', 'URL', 'textObjectCitation',
                                            function($scope, $rootScope, $http, $location, $routeParams, URL, textObjectCitation) {
    
    $scope.spinner = true; // Start a spinner while text is getting fetched
    
    $scope.textObjectURL = $routeParams;
    $scope.philoID = $scope.textObjectURL.pathInfo.split('/').join(' ');
    if ("byte" in $scope.textObjectURL) {
        $scope.byteOffset = $scope.textObjectURL.byte;
    } else {
        $scope.byteOffset = ''
    }
    $scope.textObject = {citation: textObjectCitation.citation}; // Make sure we don't change citation if it has been already filled
    var request = {
        method: "GET",
        url: $rootScope.philoConfig.db_url + '/' + URL.query({
            report: "navigation",
            philo_id: $scope.philoID,
            byte: $scope.byteOffset})
    }
    $http(request)
        .success(function(data, status, headers, config) {
            $scope.textObject = data;
            textObjectCitation.citation = data.citation;
            affixTopBar();
            if ($scope.byteOffset.length > 0 ) {
                setTimeout(scrollToHighlight, 500);
                setTimeout(createNoteLink, 500)
            }
            getTableOfContents();
            checkEndBeginningOfDoc();
            $scope.spinner = false;
        })
        .error(function(data, status, headers, config) {
            console.log("Error", status, headers)
        });
        
    var getTableOfContents = function() {
        if ($('#toc-content').find('div').length > 0) {
            console.log('not reloaded')
        } else {
            var request = {
                method: "GET",
                url: $rootScope.philoConfig.db_url + '/' + URL.query({philo_id: $scope.philoID, script: 'get_table_of_contents.py'})
                }
            $http(request)
                .success(function(data, status, headers, config) {
                    $scope.tocObject = data;
                    $("#show-toc").removeAttr("disabled");
                    adjustTocHeight(100);
                })
                .error(function(data, status, headers, config) {
                    console.log("Error", status, headers)
                });
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
    
    var affixTopBar = function() {
        // Previous and next button follow scroll
        $('#nav-buttons, #toc-container').affix({
            offset: {
            top: function() {
                return (this.top = $('#nav-buttons').offset().top)
                }
            }
        });
        $('#nav-buttons').on('affix.bs.affix', function() {
            $(this).addClass('fixed');
            $("#toc-container").addClass('fixed');
            adjustTocHeight();
            $('#back-to-top').velocity("stop").velocity('fadeIn', {duration: 200});
        });
        $('#nav-buttons').on('affix-top.bs.affix', function() {
            $(this).removeClass('fixed');
            $("#toc-container").removeClass('fixed').css('position', 'static');
            adjustTocHeight();
            $('#back-to-top').velocity("stop").velocity('fadeOut', {duration: 200});
        });
        
        $('#back-to-top').click(function() {
            $("body").velocity('scroll', {duration: 800, easing: 'easeOutCirc', offset: 0});
        })
    }
    
    var adjustTocHeight = function (num) {
        // Make sure the TOC is no higher than viewport
        if ($(document).height() == $(window).height()) {
            var toc_height = $(window).height() - $('#nav-buttons').position().top - $('#nav-buttons').height() - $('#toc-titlebar').height() - 59;
        } else {
            var toc_height = $(window).height() - $('#nav-buttons').position().top - $('#toc-titlebar').height() - 59;
        }
        if (typeof num !="undefined") {
            toc_height = toc_height - num;
        }
        $('#toc-content').velocity("stop").velocity({'max-height': toc_height + 'px'});
    }
    
    if ($('#toc-content').find('div').length === 0) {
        $scope.tocOpen = false;
    } else {
        $scope.tocOpen = true;
    }
    $scope.toggleTableOfContents = function() {
        if ($scope.tocOpen) {
            closeTableOfContents();
        } else {
            openTableOfContents();
        }
    }    
    var openTableOfContents = function() {
        if ($(document).height() == $(window).height()) {
            $('#toc-container').css('position', 'static');
        }
        $('#toc-wrapper').css('opacity', 1);
        $('#nav-buttons').addClass('col-md-offset-4');
        $('#toc-wrapper').addClass('show');
        $scope.tocOpen = true;
        setTimeout(function() {
            adjustTocHeight();
            // TODO: find why this doesn't work
            var scrollToID = $('#' + $scope.tocObject.philo_id.join('-'));
            scrollToID.velocity("scroll", {duration: 500, container: $("#toc-content") });
            scrollToID.addClass('current-obj');
        }, 300);
    }
    var closeTableOfContents = function() {
        $scope.tocOpen = false;
        setTimeout(function() {
            if ($(document).height() == $(window).height()) {
                $('#toc-container').css('position', 'static');
            }
        });
        $('#nav-buttons').removeClass('col-md-offset-4');
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
    
    var checkEndBeginningOfDoc = function() {
        if ($scope.textObject.next === "") {
            $('#next-obj').attr('disabled', 'disabled');
        } else {
            $('#next-obj').removeAttr('disabled');
        }
        if ($scope.textObject.prev === "") {
            $("#prev-obj").attr('disabled', 'disabled');
        } else {
            $("#prev-obj").removeAttr('disabled');
        }
    }
    
    $scope.goToTextObject = function(philoID) {
        $location.url(URL.path(philoID));
    }
}]);


philoApp.animation('.toc-slide', function() {
    return {
        beforeAddClass : function(element, className, done) {
            if (className == 'ng-hide') {
                $(element).velocity('transition.slideLeftBigOut', {duration: 300, complete: done});
            }
            else {
                done();
            }
        },
        removeClass : function(element, className, done) {
            if (className == 'ng-hide') {
                $(element).velocity('transition.slideLeftBigIn', {duration: 300, complete: done});
            }
            else {
                done();
            }
        }
    };
});