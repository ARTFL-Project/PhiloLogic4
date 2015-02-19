"use strict";

philoApp.controller('landingPage', ['$scope', function($scope) {
    $scope.dictionary = $scope.philoConfig.dictionary;
}]);

philoApp.controller('landingDefault', ['$scope', '$http', function($scope, $http) {
    
    $scope.authorRanges = $scope.philoConfig.landing_page_browsing.author;
    $scope.titleRanges = $scope.philoConfig.landing_page_browsing.title;
    $scope.authorOffset = "";
    $scope.titleOffset = "";
    
    if (!$scope.titleRanges) {
        $scope.authorOffset = "col-sm-offset-3";
    }
    if (!$scope.authorRanges) {
        $scope.titleOffset = "col-sm-offset-3";
    }
    $scope.dateRanges = [];
    var start = $scope.philoConfig.landing_page_browsing.date.start;
    var end = $scope.philoConfig.landing_page_browsing.date.end;
    var interval = $scope.philoConfig.landing_page_browsing.date.interval;
    var row = [];
    var position = 0;
    for (var i=start; i < end; i += interval) {
        position++;
        row.push({start: i, end: i+interval});
        if (position === 4) {
            $scope.dateRanges.push(row);
            row = [];
            position = 0;
        }
    }
    if (row.length) {
        $scope.dateRanges.push(row);
    }
    if (!$scope.dateRanges.length) {
        $scope.dateRanges = false;
    }
    
    $scope.getContent = function(contentType, range) {
        $('#landing-page-content').find('div:visible')
                                  .velocity('transition.slideRightOut',
                                    {
                                        duration: 200,
                                        begin: function() { $("#footer").hide(); },
                                        complete:function() { $(this).css('opacity', 1); }
                                    });
        var contentId = contentType + '-' + range;
        var contentArea = $('#' + contentId);
        if (!contentArea.length) {
            var contentDiv = '<div id="' + contentId + '"></div>';
            var query = 'scripts/get_landing_page_content.py?landing_page_content_type=' + contentType + '&range=' + range;
            $http.get(query)
                .success(function(data, status, headers, config) {
                    $scope.renderContent(contentId, contentDiv, contentType, range, data)
                })
                .error(function(data, status, headers, config) {
                    console.log("Error", status, headers)
                });
        } else {
            var contentArea = $('#' + contentId);
            var contentElements = contentArea.find('ul');
            contentArea.show();
            $('#landing-page-content').show();
            contentElements.velocity('transition.slideLeftIn', {
                duration: 400,
                stagger: 20,
                complete:function() {
                    $("#footer").velocity('fadeIn');}
            });
        }  
    }
    
    $scope.renderContent = function(contentId, contentDiv, contentType, range, data) {
        $('#landing-page-content').append(contentDiv);
        var contentArea = $('#' + contentId);
        var available_links = [];
        var html = '';
        var title;
        for (var i=0; i < data.length; i++) {
            if (contentType == "author" || contentType == "title") {
                var prefix = data[i][contentType].slice(0,1).toLowerCase();
            } else {
                prefix = data[i].year;
            }
            if (i == 0) {
                html += '<ul class="row" style="margin-bottom: 20px;">';
                html += '<h4 id="' + prefix + '">' + prefix.toUpperCase() + '</h4>';
                title = prefix;
                available_links.push(title);
            }
            if (prefix != title) {
                html += '</ul><ul class="row" style="margin-bottom: 20px;"><h4 id="' + prefix + '">' + prefix.toUpperCase() + '</h4>';
                title = prefix;
                available_links.push(title);
            }
            if (contentType == "author") {
                var content = '<li class="col-xs-12 col-sm-6">';
                content += data[i].cite + "</li>";
            } else if (contentType == "title" || contentType == "year") {
                var content = '<li class="col-xs-12">'
                content += data[i].cite + "</li>";
            }
            html += content;
        }
        html += '</ul>';
        contentArea.html(html).promise().done(function() {
            var contentElements = contentArea.find('ul');
            contentArea.show();
            $('#landing-page-content').show();
            contentElements.velocity('transition.slideLeftIn', {
                duration: 400,
                stagger: 20,
                complete:function() {
                    $("#footer").velocity('fadeIn');}
            });
        });   
    }
}]);
    
philoApp.controller('landingDico', ['$scope', '$http', function($scope, $http) {
    var allVolumesQuery = "scripts/get_bibliography.py?object_level=doc&format=json"
    $http.get(allVolumesQuery)
        .success(function(data, status, headers, config) {
            for (var i=0; i < data.length; i++) {
                $scope.volumeData.push(data[i]);
            }
        })
        .error(function(data, status, headers, config) {
            console.log("Error", status, headers)
        });
    
    var dicoLetterRange = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M",
                            "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"];
    $scope.dicoLetterRows = [];
    var row = [];
    var position = 0;
    for (var i=0; i < dicoLetterRange.length; i++) {
        position++;
        row.push(dicoLetterRange[i]);
        if (position === 4) {
            $scope.dicoLetterRows.push(row);
            row = [];
            position = 0;
        }
    }
    if (row.length) {
        $scope.dicoLetterRows.push(row);
    }
    
    $scope.goToBibliographyReport = function(letter) {
        var query = "dispatcher.py?report=bibliography&format=json&head=^" + letter + '.*';
        $http.get(query)
            .success(function(data, status, headers, config) {
                $scope.headData = data;
            })
            .error(function(data, status, headers, config) {
                console.log("Error", status, headers)
            });
    }
}]);