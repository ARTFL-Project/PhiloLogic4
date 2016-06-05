(function() {
    "use strict"

    angular
        .module('philoApp')
        .filter('metadataFieldsFilter', metadataFieldsFilter)

    function metadataFieldsFilter($rootScope, philoConfig) {
        return function(metadataFields) {
            var filtered = [];
            for (var i = 0; i < metadataFields.length; i++) {
                var metadata = metadataFields[i].value;
                if ($rootScope.formData.report === "time_series") {
                    if (metadata !== philoConfig.time_series_year_field) {
                        filtered.push(metadataFields[i]);
                    }
                } else {
                    filtered.push(metadataFields[i]);
                }
            }
            return filtered;
        }
    }
})();
