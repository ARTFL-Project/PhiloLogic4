(function() {
    "use strict";

    angular
        .module('philoApp')
        .value('descriptionValues', {
            start: '',
            end: '',
            resultsPerPage: 25,
            resultsLength: '',
        })
        .value('facetedBrowsing', {
            show: true
        })
        .value('sortedKwicCached', {
            results: null,
            queryObject: null
        });
})();
