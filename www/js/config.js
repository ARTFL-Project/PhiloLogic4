"use strict";

philoApp.factory('searchFormConfig', ['$rootScope', 'searchConfigBuild', function($rootScope, searchConfigBuild) {
    return {
        metadataFields: searchConfigBuild.metadata(),
        collocWordNum: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        wordFiltering: [25, 50, 75, 100, 125, 150, 175, 200],
        timeSeriesIntervals: searchConfigBuild.timeSeriesIntervals()
    }
}]);

philoApp.value('formData', {
        report: philoConfig.search_reports[0],
        method: "proxy",
        results_per_page: "25"
});

philoApp.value('concordanceResults', {});

philoApp.value('kwicResults', {});

philoApp.value('timeSeriesResults', {})

philoApp.value('collocationResults', {})

philoApp.value('textObjectCitation', {citation: {}})