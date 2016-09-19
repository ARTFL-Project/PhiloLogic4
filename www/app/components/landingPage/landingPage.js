(function() {
    "use strict";

    angular
        .module("philoApp")
        .controller('LandingPageController', LandingPageController)
        .animation('.repeated-item', function() {
            return {
                enter: function(element, done) {
                    element.velocity('transition.slideLeftIn', {
                        duration: 400
                    })
                },
                leave: function(element, done) {
                    element.velocity('transition.slideRightOut', {
                        duration: 400
                    })
                }
            }
        });


    function LandingPageController($rootScope, $location, accessControl) {
        var vm = this;
        if ($rootScope.authorized === true) {
            vm.authorized = true;
        } else {
            $rootScope.accessRequest.then(function(response) {
                $rootScope.authorized = response.data.access;
                vm.authorized = $rootScope.authorized;
            });
        }

        vm.landingPageBrowsing = $rootScope.philoConfig.landing_page_browsing;

        $rootScope.report = "landing_page";

        vm.getContent = function(browseType, range) {
            vm.query = {
                browseType: browseType,
                query: range
            };
        }

        vm.goToBibliography = function(url) {
            $location.url(url);
        }

        vm.goToToc = function(docId) {
            $location.url('navigate/' + docId + '/table-of-contents');
        }
    }
})();
