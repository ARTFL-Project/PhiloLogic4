(function() {
    "use strict";

    angular
        .module('philoApp')
        .value('descriptionValues', {
            start: '',
            end: '',
            resultsPerPage: 25,
            resultsLength: '',
            sortedKwic: {
                results: null,
                queryObject: null            }
        });
})();
