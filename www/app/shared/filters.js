(function() {
    "use strict";

    angular
        .module("philoApp")
        .filter("isEmpty", isEmpty)
        .filter("unsafe", unSafe);


    function isEmpty() {
        return function(obj) {
            if (angular.element.isEmptyObject(obj)) {
                return false;
            } else {
                return true;
            }
        };
    }

    function unSafe($sce) {
        return $sce.trustAsHtml;
    }
})();
