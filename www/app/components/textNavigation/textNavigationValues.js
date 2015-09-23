(function() {
    "use strict";
    angular
        .module('philoApp')
        .value('textNavigationValues', {
            citation: {},
            tocElements: false,
            tocOpen: false,
            navBar: false,
            prev: "",
            next: "",
        });
})();
