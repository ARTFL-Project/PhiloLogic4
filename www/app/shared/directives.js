philoApp.directive('loading', function() {
    return {
        restrict: 'A',
        scope: {
            loading: '='
        },
        link: function(scope, element) {
            element.prepend('<div class="spinner"><div class="bounce1"></div><div class="bounce2"></div><div class="bounce3"></div></div>');
            scope.$watch('loading', function(value) {
                if (value) {
                   element.find('.spinner').velocity('fadeIn', {duration: 200}); 
                } else {
                    element.find('.spinner').velocity('fadeOut', {duration: 200});
                }
            })
        }
    }
});

philoApp.directive('progressBar', function() {
    return {
        restrict: 'E',
        template: '<div class="progress"><div class="progress-bar" role="progressbar" aria-valuenow="20" aria-valuemin="0" aria-valuemax="100" style="width: 0%;"></div></div>',
        replace: true,
        link: function(scope, element, attrs) {
            attrs.$observe('progress', function(percent) {
                element.show(); // Make sure it's always visible
                var progressElement = element.find('.progress-bar');
                progressElement.velocity({'width': percent.toString() + '%'}, {
                    queue: false,
                    complete: function() {
                        progressElement.text(percent.toString() + '%');
                        if (percent == 100) {
                            progressElement.parent().delay(500).velocity('slideUp');
                        }
                    }
                }); 
            });     
        }
    }
});

philoApp.directive('selectWord', ['$location', 'request', '$rootScope', function($location, request, $rootScope) {
    return {
        restrict: 'A',
        replace: true,
        link: function(scope, element, attrs) {
            if (scope.philoConfig.words_facets.length > 0) {
                element.mouseup(function() {
                    var text = window.getSelection().toString();
                    if (text.length > 0) {
                        var context = element.find('div:visible').text();
                        var position = parseInt(attrs.position) - 1;
                        var query = $location.search();
                        request.script(query, {
                            script: 'lookup_word.py',
                            selected: text,
                            position: position
                        }).then(function(response) {
                            if (!$.isEmptyObject(response.data)) {
                                $rootScope.wordProperties = response.data;
                                $('#wordProperty').modal('show');
                            }
                        });
                    }
                });
            }
            element.on('$destroy', function() {
                element.off();
            });
        }
    }
}]);

philoApp.directive('tooltip', function() {
    return {
        restrict: 'A',
        link: function(scope, element, attrs) {
            element.mouseenter(function() {
                var text = attrs.tooltipTitle;
                if (!text.length && scope.formData.report === 'time_series') {
                    var startDate = element.find('.graph-years').text();
                    var endDate = parseInt(startDate) + parseInt(scope.formData.year_interval) - 1;
                    text = '0 occurrences for ' + startDate.toString() + '-' + endDate.toString();
                }
                var barWidth = element.width();
                var distanceFromEdge = $(document).width() - element.offset().left - element.width() - 180; // Give extra for padding;
                if (distanceFromEdge > 0) {
                    var tooltipContainer = $('<div class="tooltip right" style="width: 150px; margin-left: ' + barWidth + 'px;"><div class="tooltip-arrow"></div><div class="tooltip-inner">' + text + '</div></div>');
                } else {
                    var tooltipContainer = $('<div class="tooltip left" style="width: 150px; margin-left: -150px;"><div class="tooltip-arrow"></div><div class="tooltip-inner">' + text + '</div></div>');
                }
                element.append(tooltipContainer);
                element.find('.tooltip').velocity({'opacity': .9}, {duration: 200});              
            });
            element.mouseleave(function() {
                element.find('.tooltip').remove();
            });
            element.on('$destroy', function() {
                element.off();
            });
        }
    }
});