"use strict";

philoApp.controller('textNavigation', ['$scope', '$rootScope', '$http', '$location', '$routeParams', 'URL', 'textObjectCitation',
                                            function($scope, $rootScope, $http, $location, $routeParams, URL, textObjectCitation) {
    
    $rootScope.report = "textObject";
    $scope.textObject = {};
    $scope.navBar = false; // Don't draw navBar until text has been fetched
    $scope.loading = true; // Start a spinner while text is getting fetched
    $scope.tocDone = false // Only fetch TOC once navBar has been drawn
    
    
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
            $scope.adjustTocHeight();
            // TODO: find why this doesn't work
            var scrollToID = $('#' + $scope.tocObject.philo_id.join('-'));
            scrollToID.velocity("scroll", {duration: 500, container: $("#toc-content"), offset: -50});
            scrollToID.find('a').addClass('current-obj');
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
    $scope.adjustTocHeight = function(num) {
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