(function() {
    "use strict";

    angular
        .module('philoApp')
        .controller('TextNavigationController', TextNavigationController)
        .animation('.toc-slide', function() {
            return {
                beforeAddClass: function(element, className, done) {
                    if (className == 'ng-hide') {
                        angular.element(element).velocity('slideUp', {
                            duration: 300,
                            complete: done
                        });
                        angular.element(element).velocity({
                            opacity: 0
                        }, {
                            duration: 300,
                            queue: false,
                            complete: function() {
                                angular.element('#toc-container').removeClass('display');
                            }
                        });
                    } else {
                        done();
                    }
                },
                removeClass: function(element, className, done) {
                    if (className == 'ng-hide') {
                        var height = angular.element(window).height() - angular.element('#book-page').offset().top - 80;
                        angular.element('#toc-content').css('max-height', height + 'px');
                        angular.element('#toc-container').addClass('display');
                        angular.element(element).velocity('slideDown', {
                            duration: 300,
                            complete: done
                        });
                        angular.element(element).velocity({
                            opacity: 1
                        }, {
                            duration: 300,
                            queue: false
                        });
                    } else {
                        done();
                    }
                }
            };
        });

    function TextNavigationController($scope, $rootScope, $location, $routeParams, $timeout, accessControl, URL, textNavigationValues) {
        var vm = this;
        if ($rootScope.authorized === true) {
            vm.authorized = true;
        } else {
            $rootScope.accessRequest.then(function(response) {
                $rootScope.authorized = response.data.access;
                vm.authorized = $rootScope.authorized;
            });
        }
        vm.textObject = {};
        vm.loading = true;
        vm.navBar = textNavigationValues.navBar; // Don't draw navBar until text has been fetched
        vm.tocOpen = false;
        vm.tocDone = false // Only fetch TOC once navBar has been drawn
        vm.textRendered = false;

        vm.philoId = $routeParams.pathInfo.replace('/', ' ');

        if (vm.tocOpen) {
            $timeout(function() {
                angular.element('.current-obj').velocity("scroll", {
                    duration: 0,
                    container: angular.element("#toc-content"),
                    offset: -50
                });
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
            angular.element('#toc-wrapper').addClass('display');
            vm.tocOpen = true;
            $timeout(function() {
                angular.element('.current-obj').velocity("scroll", {
                    duration: 500,
                    container: angular.element("#toc-content"),
                    offset: -50
                });
            }, 300);
        }
        var closeTableOfContents = function() {
            angular.element('#toc-wrapper').removeClass('display');
            vm.tocOpen = false;
            $timeout(function() {
                if (angular.element(document).height() == angular.element(window).height()) {
                    angular.element('#toc-container').css('position', 'static');
                }
            });
        }

        vm.backToTop = function() {
            angular.element("body").velocity('scroll', {
                duration: 800,
                easing: 'easeOutCirc',
                offset: 0
            });
        }

        vm.goToTextObject = function(philoID) {
            philoID = philoID.split('-').join('/');
            if (vm.tocOpen) {
                angular.element("#toc-wrapper").velocity('transition.slideUpOut', {
                    duration: 200,
                    queue: false,
                    complete: function() {
                        $location.url(URL.path(philoID)).replace(); // deleting current page history and replace with new page
                        $scope.$apply();
                    }
                });
            } else {
                $location.url(URL.path(philoID)).replace(); // deleting current page history and replace with new page
            }

        }
    }
})();
