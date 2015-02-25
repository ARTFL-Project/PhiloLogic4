philoApp.controller('searchForm', ['$scope', '$rootScope', '$http', '$location', 'radio', 'URL', function($scope, $rootScope, $http, $location, radio, URL) {
    $scope.formOpen = false;
    $scope.toggleForm = function() {
        if (!$("#search-elements").length) {
            $scope.formOpen = true;
        } else {
            $scope.formOpen = false;
        }
    }
    
    // Handle radio clicks to workaround clash between angular and bootstrap
    $scope.radioClick = radio.click;
    
    $scope.clearFormData = function() {
        $rootScope.formData = {
            report: $rootScope.philoConfig.search_reports[0],
            method: "proxy",
            results_per_page: "25"
        };
    }
    
    // Button click from fixed search bar
    $scope.backToFullSearch = function() {
        $("body").velocity('scroll', {duration: 800, easing: 'easeOutCirc', offset: 0, complete: function() {
            $scope.toggleForm();
            $scope.$apply();
        }});            
    }
    
    // Show or hide search bar
    if ($rootScope.report === "concordance" || $rootScope.report === "kwic" || $rootScope.report === "bibliography" || $rootScope.report === "collocation") {
        $scope.showSearchBar = true;
    } else {
        $scope.showSearchBar = false;
    }
    $rootScope.$watch('report', function(newReport) {
        if (newReport === "concordance" || newReport === "kwic" || newReport === "bibliography" || newReport === 'collocation') {
            $scope.showSearchBar = true;
        } else {
            $scope.showSearchBar = false;
        }
    });
    
    $scope.submit = function() {
        $('.ui-autocomplete').hide();
        if (typeof($rootScope.formData.q) === "undefined" || $rootScope.formData.q === '') {
            $rootScope.formData.report = "bibliography";
        } else if ($scope.formData.report === "bibliography" && typeof($rootScope.formData.q) !== "undefined") {
            $rootScope.formData.report = $("#report label.active input").attr('id');
        }
        delete $rootScope.formData.start;
        delete $rootScope.formData.end;
        $scope.formOpen = false;
        $location.url(URL.objectToString($rootScope.formData, true));
    }
}]);

philoApp.animation('.overlay-fadeOut', function() {
    return {
        enter: function(element, done) {
            $(element).velocity({
                opacity: 0.3
            }, {duration: 300, complete: done});
        },
        leave: function(element, done) {
            $(element).velocity({
                opacity: 0
            }, {duration: 300, complete: done});
        }
    };
});

philoApp.animation('.report-fade', function() {
    return {
        enter: function(element, done) {
            $(element).velocity({
                opacity: 1
            }, {duration: 200, complete: done});
        },
        leave: function(element, done) {
            $(element).velocity({
                opacity: 0
            }, {duration: 200, complete: done});
        }
    };
});