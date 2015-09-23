(function() {
    "use strict";

    angular
        .module("philoApp")
        .controller('ExportResultsController', ExportResultsController);

    function ExportResultsController($window) {
        var vm = this;
        vm.export = function() {
            var exportLink = $window.location.href + "&format=json";
            $window.open(exportLink);
        }
    }
})();
