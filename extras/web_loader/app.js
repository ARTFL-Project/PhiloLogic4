(function() {
    "use strict";

    angular
        .module("philoLoader", ["ngRoute", "ngTouch"])
        .controller("PhiloLoaderController", PhiloLoaderController);

    function PhiloLoaderController($http, $log) {
        var vm = this;

        vm.formData = {
            fileSource: "server"
        };

        vm.submit = function() {
            $log.debug(vm.formData)
            var urlString = objectToString(vm.formData);
            $http.get("/philoload/web_loader.py?" + urlString).then(function(response) {
                $log.debug(response.data);
            });
        }
    }

    function objectToString(localParams) {
        var str = [];
        for (var p in localParams) {
            var k = p,
                v = localParams[k];
            if (angular.isObject(v)) {
                for (var i = 0; i < v.length; i++) {
                    str.push(angular.isObject(v[i]) ? this.query(v[i], k) : (k) + "=" + encodeURIComponent(v[i]));
                }
            } else {
                str.push(angular.isObject(v) ? this.query(v, k) : (k) + "=" + encodeURIComponent(v));
            }
        }
        return str.join("&")
    }
})();
