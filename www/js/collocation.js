"use strict";

philoApp.controller('collocationCtrl', ['$scope', '$rootScope', '$http', '$location', 'radio', 'progressiveLoad', 'URL', 'collocation',
                                            function($scope, $rootScope, $http, $location, radio, progressiveLoad, URL, collocation) {
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
    
    if (sessionStorage[$location.url()] == null || $rootScope.philoConfig.debug === false) {
        $('#philologic_collocation').velocity('fadeIn', {duration: 200});
        $scope.resultsLength = false; // set to false for now
        $(".progress").show();
        var collocObject;
        collocation.updateCollocation($scope, collocObject, false, 0, 1000);
    } else {
        var savedObject = JSON.parse(sessionStorage[$location.url()]);
        $scope.sortedLists = savedObject.results;
        $scope.resultsLength = savedObject.resultsLength;
        $scope.filterList = savedObject.filterList;
        collocation.collocationCloud($scope.sortedLists.all);
        collocation.activateLinks();
        $scope.percent = 100;
        $scope.done = true;
        $('#philologic_collocation').velocity('fadeIn', {duration: 200});
    }
    
    $scope.toggleFilterList = function() {
        if ($('#filter-list').css('display') === "block") {
            $('#filter-list').velocity('fadeOut');
        } else {
            $('#filter-list').velocity('fadeIn');
        }
    }

}]);