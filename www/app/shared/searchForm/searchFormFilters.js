philoApp.filter('metadataFieldsFilter', ['$rootScope', function($rootScope) {
    return function(metadataFields) {
        var filtered = [];
        for (var i=0; i < metadataFields.length; i++) {
            var metadata = metadataFields[i].value;
            if ($rootScope.formData.report === "time_series") {
                if (metadata !== "date") {
                    filtered.push(metadataFields[i]);
                }
            } else {
                filtered.push(metadataFields[i]);
            }
        }
        return filtered;
    }
}]);