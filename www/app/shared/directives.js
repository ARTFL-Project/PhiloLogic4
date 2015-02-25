philoApp.directive('loading', function() {
    return {
        restrict: 'E',
        template: '<div class="spinner"><div class="bounce1"></div><div class="bounce2"></div><div class="bounce3"></div></div>'
    }
});

philoApp.directive('progressBar', function() {
    return {
        restrict: 'E',
        template: '<div class="progress"><div class="progress-bar" role="progressbar" aria-valuenow="20" aria-valuemin="0" aria-valuemax="100" style="width: 0%;"></div></div>',
        link: function(scope, element, attrs) {
            attrs.$observe('progress', function(percent){
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

philoApp.directive('affix', ['$rootScope', '$timeout', function($rootScope, $timeout) {
    return {
        link: function($scope, $element, $attrs) {

            function applyAffix() {
                $timeout(function() {                   
                    $element.affix({ offset: { top: $attrs.affix } });
                });
            }

            $rootScope.$on('$locationChangeStart', function() {
                $element.removeData('bs.affix').removeClass('affix affix-top affix-bottom');
                applyAffix();
            });

            applyAffix();

        }
    };
}]);