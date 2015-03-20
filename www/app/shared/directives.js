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