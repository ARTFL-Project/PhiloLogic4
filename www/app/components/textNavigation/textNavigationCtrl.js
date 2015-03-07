"use strict";

philoApp.controller('textNavigation', ['$scope', '$rootScope', '$http', '$location', '$routeParams', '$timeout', 'URL', 'textNavigationValues',
                                            function($scope, $rootScope, $http, $location, $routeParams, $timeout, URL, textNavigationValues) {
    
    $scope.textObject = {};
    $scope.loading = true;
    $scope.navBar = textNavigationValues.navBar; // Don't draw navBar until text has been fetched
    $scope.tocElements = textNavigationValues.tocElements;
    $scope.tocOpen = textNavigationValues.tocOpen;
    $scope.tocDone = false // Only fetch TOC once navBar has been drawn
    
    $scope.philoId = $routeParams.pathInfo.replace('/', ' ');
    
    if ($scope.tocOpen) {
        setTimeout(function() {
            // TODO: find why this doesn't work
            $('.current-obj').velocity("scroll", {duration: 0, container: $("#toc-content"), offset: -50});
        });
    }
    
    $scope.toggleTableOfContents = function() {
        console.log('toggled', $scope.tocOpen)
        if ($scope.tocOpen) {
            closeTableOfContents();
        } else {
            openTableOfContents();
        }
    }    
    var openTableOfContents = function() {
        $('#toc-wrapper').addClass('display');
        //$scope.adjustTocHeight();
        $scope.tocOpen = true;
        $timeout(function() {
            $('.current-obj').velocity("scroll", {duration: 500, container: $("#toc-content"), offset: -50});
        }, 300);
    }
    var closeTableOfContents = function() {
        $scope.tocOpen = false;
        setTimeout(function() {
            if ($(document).height() == $(window).height()) {
                $('#toc-container').css('position', 'static');
            }
        });
    }
    $scope.adjustTocHeight = function() {
    }
    
    $scope.backToTop = function() {
        $("body").velocity('scroll', {duration: 800, easing: 'easeOutCirc', offset: 0});
    }
    
    $scope.goToTextObject = function(philoID) {
        $scope.tocOpen = false;
        philoID = philoID.split('-').join('/');
        $location.url(URL.path(philoID));
    }
}]);


philoApp.animation('.toc-slide', function() {
    return {
        beforeAddClass : function(element, className, done) {
            if (className == 'ng-hide') {
                $(element).velocity('slideUp', {duration: 300, complete: done});
                $("#toc-wrapper").velocity({opacity: 0}, {duration: 300, queue: false});
            }
            else {
                done();
            }
        },
        removeClass : function(element, className, done) {
            if (className == 'ng-hide') {
                var windowHeight = $(window).height();
                var bookPageHeight = $('#book-page').height() + 50;
                if ((windowHeight -120) < bookPageHeight) {
                    var height = windowHeight - 120;
                } else {
                    var height = windowHeight - $('#book-page').offset().top - 80;
                }
                console.log(height)
                $('#toc-content').css({
                    maxHeight: height + 'px'
                    });
                $(element).velocity('slideDown', {duration: 300, complete: done});
                $("#toc-wrapper").velocity({opacity: 1}, {duration: 300, queue: false});
            }
            else {
                done();
            }
        }
    };
});