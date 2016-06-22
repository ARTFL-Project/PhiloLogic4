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
        .value('sortedKwicCache', {
            results: null,
            queryObject: null
        });
})();
