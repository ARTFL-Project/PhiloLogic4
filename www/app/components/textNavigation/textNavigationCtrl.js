"use strict";

philoApp.controller('textNavigationCtrl', ['$scope', '$rootScope', '$location', '$routeParams', '$timeout', 'accessControl', 'URL', 'textNavigationValues',
                                           function($scope, $rootScope, $location, $routeParams, $timeout, accessControl, URL, textNavigationValues) {
    
    var vm = this;
    var access = accessControl.cookieCheck()
    vm.authorized = $rootScope.access.navigation;
    vm.textObject = {};
    vm.loading = true;
    vm.navBar = textNavigationValues.navBar; // Don't draw navBar until text has been fetched
    vm.tocElements = textNavigationValues.tocElements;
    vm.tocOpen = false;
    vm.tocDone = false // Only fetch TOC once navBar has been drawn
    
    vm.philoId = $routeParams.pathInfo.replace('/', ' ');
    
    if (vm.tocOpen) {
        $timeout(function() {
            $('.current-obj').velocity("scroll", {duration: 0, container: $("#toc-content"), offset: -50});
        });
    }
    
    vm.toggleTableOfContents = function() {
        if (vm.tocOpen) {
            closeTableOfContents();
        } else {
            openTableOfContents();
        }
    }    
    var openTableOfContents = function() {
        $('#toc-wrapper').addClass('display');
        vm.tocOpen = true;
        $timeout(function() {
            $('.current-obj').velocity("scroll", {duration: 500, container: $("#toc-content"), offset: -50});
        }, 300);
    }
    var closeTableOfContents = function() {
        $('#toc-wrapper').removeClass('display');
        vm.tocOpen = false;
        $timeout(function() {
            if ($(document).height() == $(window).height()) {
                $('#toc-container').css('position', 'static');
            }
        });
    }
    
    vm.backToTop = function() {
        $("body").velocity('scroll', {duration: 800, easing: 'easeOutCirc', offset: 0});
    }
    
    vm.goToTextObject = function(philoID) {
        philoID = philoID.split('-').join('/');
        if (vm.tocOpen) {
            $("#toc-wrapper").velocity('transition.slideUpOut', {duration: 200, queue: false, complete: function() {
                $location.url(URL.path(philoID)).replace();
                $scope.$apply();
            }});
        } else {
            $location.url(URL.path(philoID)).replace();
        }
        
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
                var height = $(window).height() - $('#book-page').offset().top - 80;
                $('#toc-content').css('max-height', height + 'px');
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