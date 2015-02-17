"use strict";

philoApp.controller('collocationCtrl', ['$scope', '$rootScope', '$http', '$location', 'radio', 'URL',
                                            function($scope, $rootScope, $http, $location, radio, URL) {
    $rootScope.formData = $location.search();
    if ($rootScope.formData.q === "" && $rootScope.report !== "bibliography") {
        $rootScope.formData.report = "bibliography";
        $location.url(URL.objectToString($rootScope.formData, true));
    }
    
    radio.setReport('collocation');
    
    $scope.collocationParams = {
        q: $rootScope.formData.q,
        wordNum: $rootScope.formData.word_num,
        collocFilterChoice: $rootScope.formData.colloc_filter_choice,
        collocFilterFrequency: $rootScope.formData.filter_frequency,
        collocFilterList: $rootScope.formData.filter_list
    }
    
    $scope.done = false;
    $scope.filterList = false;
    $scope.percent = 0;
    $scope.sortedLists = {};
    $scope.resultsLength = false; // set to false for now
    
    $scope.toggleFilterList = function() {
        if ($('#filter-list').css('display') === "block") {
            $('#filter-list').velocity('fadeOut');
        } else {
            $('#filter-list').velocity('fadeIn');
        }
    }

}]);