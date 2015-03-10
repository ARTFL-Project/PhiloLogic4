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
        if ($scope.tocOpen) {
            closeTableOfContents();
        } else {
            openTableOfContents();
        }
    }    
    var openTableOfContents = function() {
        $('#toc-wrapper').addClass('display');
        $scope.tocOpen = true;
        $timeout(function() {
            $('.current-obj').velocity("scroll", {duration: 500, container: $("#toc-content"), offset: -50});
        }, 300);
    }
    var closeTableOfContents = function() {
        $('#toc-wrapper').removeClass('display');
        $scope.tocOpen = false;
        setTimeout(function() {
            if ($(document).height() == $(window).height()) {
                $('#toc-container').css('position', 'static');
            }
        });
    }
    
    $scope.backToTop = function() {
        $("body").velocity('scroll', {duration: 800, easing: 'easeOutCirc', offset: 0});
    }
    
    $scope.goToTextObject = function(philoID) {
        $("#toc-wrapper").velocity({opacity: 0}, {duration: 250});
        $("#toc-wrapper").velocity('slideUp', {duration: 300, queue: false, complete: function() {
                philoID = philoID.split('-').join('/');
                $location.url(URL.path(philoID)).replace();
                $scope.$apply()
            }});
    }
}]);


philoApp.animation('.toc-slide', function() {
    return {
        beforeAddClass : function(element, className, done) {
            if (className == 'ng-hide') {
                $(element).velocity('slideUp', {duration: 300, complete: done});
                $(element).velocity({opacity: 0}, {duration: 300, queue: false, complete: function() {
                    $('#toc-container').removeClass('display');
                }});
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
                $('#toc-content').css({
                    maxHeight: height + 'px'
                    });
                $('#toc-container').addClass('display');
                $(element).velocity('slideDown', {duration: 300, complete: done});
                $(element).velocity({opacity: 1}, {duration: 300, queue: false});
            }
            else {
                done();
            }
        }
    };
});