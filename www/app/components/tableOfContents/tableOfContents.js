"use strict"

philoApp.controller('tableOfContents', ['$rootScope', '$http', '$location', '$routeParams', 'URL', "request", function($rootScope, $http, $location, $routeParams, URL, request) {
    
    this.textObjectURL = $routeParams;
    var tempValue = this.textObjectURL.pathInfo.split('/');
    tempValue.pop();
    this.philoID = tempValue.join(' ');
    var formData = {report: "table_of_contents", philo_id: this.philoID};
    var self = this;
    request.report(formData).then(function(promise) {
        self.tocObject = promise.data;
    });
    
    this.teiHeader = false;
    this.showHeader = function() {
        if (typeof(this.teiHeader) === "string") {
            this.teiHeader = false;
        } else {
            var UrlString = {script: "get_header.py", philo_id: this.philoID};
            request.script(UrlString).then(function(promise) {
                self.teiHeader = promise.data;
            });
        }
    }

}]);