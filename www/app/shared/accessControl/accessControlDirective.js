(function() {
    "use strict";

    angular
        .module("philoApp")
        .directive('accessControl', accessControl);

    function accessControl() {
        return {
            templateUrl: 'app/shared/accessControl/accessControl.html'
        };
    }
})();
