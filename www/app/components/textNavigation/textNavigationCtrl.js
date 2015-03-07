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
        $('#toc-wrapper').css('opacity', 1);
        $('#nav-buttons').addClass('col-md-offset-4'); // could cause the margin issue
        $('#toc-wrapper').addClass('show');
        $scope.adjustTocHeight();
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
        $('#toc-content').css({'max-height': toc_height + 'px'});
    }
    
    $scope.backToTop = function() {
        $("body").velocity('scroll', {duration: 800, easing: 'easeOutCirc', offset: 0});
    }
    
    $scope.goToTextObject = function(philoID) {
        textNavigationValues.tocOpen = $scope.tocOpen;
        philoID = philoID.split('-').join('/');
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