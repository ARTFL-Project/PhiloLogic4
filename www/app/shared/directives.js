(function () {
    "use strict";

    angular
        .module("philoApp")
        .directive('loading', loading)
        .directive('progressBar', progressBar)
        .directive('selectWord', selectWord)
        .directive('tooltip', tooltip)
        .directive('animateOnLoad', animateOnLoad);

    function loading() {
        return {
            restrict: 'A',
            scope: {
                loading: '='
            },
            link: function (scope, element) {
                element.prepend(['<div class="spinner-wrapper"><div class="showbox"><div class="loader">',
                       '<svg class="circular" viewBox="25 25 50 50">',
                       '<circle class="path" cx="50" cy="50" r="20" fill="none" stroke-width="2" stroke-miterlimit="10"/>',
                       '</svg></div></div></div>'].join(''));
                scope.$watch('loading', function (value) {
                    if (value) {
                        element.find('.spinner-wrapper').velocity('fadeIn', { duration: 200 });
                    } else {
                        element.find('.spinner-wrapper').velocity('fadeOut', { duration: 200 });
                    }
                })
            }
        };
    }

    function progressBar() {
        return {
            restrict: 'E',
            template: '<div class="progress"><div class="progress-bar" role="progressbar" aria-valuenow="20" aria-valuemin="0" aria-valuemax="100" style="width: 0%;"></div></div>',
            replace: true,
            link: function (scope, element, attrs) {
                attrs.$observe('progress', function (percent) {
                    element.show(); // Make sure it's always visible
                    var progressElement = element.find('.progress-bar');
                    progressElement.velocity({ 'width': percent.toString() + '%' }, {
                        queue: false,
                        complete: function () {
                            progressElement.text(percent.toString() + '%');
                            if (percent == 100) {
                                progressElement.parent().delay(500).velocity('slideUp');
                            }
                        }
                    });
                });
            }
        };
    }

    function selectWord($location, request, $rootScope, $window) {
        return {
            restrict: 'A',
            replace: true,
            link: function (scope, element, attrs) {
                var modalPopUp = function (reponse) {
                    if (!$.isEmptyObject(response.data)) {
                        $rootScope.wordProperties = response.data;
                        angular.element('#wordProperty').modal('show');
                    }
                }
                if (scope.philoConfig.words_facets.length > 0) {
                    element.mouseup(function () {
                        var text = $window.getSelection().toString();
                        if (text.length > 0) {
                            var context = element.find('div:visible').text();
                            var resultsPromise = '';
                            var query = $location.search();
                            if ($rootScope.report === 'concordance') {
                                var position = parseInt(attrs.position) - 1;
                                resultsPromise = request.script(query, {
                                    script: 'lookup_word.py',
                                    selected: text,
                                    position: position
                                });
                            } else if ($rootScope.report === "textNavigation") {
                                var philoID = attrs.philoId;
                                resultsPromise = request.script(query, {
                                    script: 'lookup_word.py',
                                    selected: text,
                                    philo_id: philoID,
                                    report: "navigation"
                                });
                            }
                            resultsPromise.then(function (response) {
                                if (!$.isEmptyObject(response.data)) {
                                    $rootScope.wordProperties = response.data;
                                    angular.element('#wordProperty').modal('show');
                                }
                            });
                        }
                    });
                }
                element.on('$destroy', function () {
                    element.off();
                    $rootScope.wordProperties = undefined;
                });
            }
        };
    }

    function tooltip() {
        return {
            restrict: 'A',
            link: function (scope, element, attrs) {
                element.mouseenter(function () {
                    var text = attrs.tooltipTitle;
                    if (!text.length && scope.formData.report === 'time_series') {
                        var startDate = element.find('.graph-years').text();
                        var endDate = parseInt(startDate) + parseInt(scope.formData.year_interval) - 1;
                        text = '0 occurrences for ' + startDate.toString() + '-' + endDate.toString();
                    }
                    var barWidth = element.width();
                    var distanceFromEdge = angular.element(document).width() - element.offset().left - element.width() - 180; // Give extra for padding;
                    if (distanceFromEdge > 0) {
                        var tooltipContainer = angular.element('<div class="tooltip right" style="width: 150px; margin-left: ' + barWidth + 'px;"><div class="tooltip-arrow"></div><div class="tooltip-inner">' + text + '</div></div>');
                    } else {
                        var tooltipContainer = angular.element('<div class="tooltip left" style="width: 150px; margin-left: -150px;"><div class="tooltip-arrow"></div><div class="tooltip-inner">' + text + '</div></div>');
                    }
                    element.append(tooltipContainer);
                    element.find('.tooltip').velocity({ 'opacity': .9 }, { duration: 200 });
                });
                element.mouseleave(function () {
                    element.find('.tooltip').remove();
                });
                element.on('$destroy', function () {
                    element.off();
                });
            }
        };
    }
    
    // Force animate on load
    function animateOnLoad($animateCss) {
        return {
            'link': function (scope, element) {
                $animateCss(element, {
                    'event': 'enter',
                    structural: true
                }).start();
            }
        };
    }

})();
