"use strict";

philoApp.controller('textObjectNavigation', ['$scope', '$rootScope', '$http', '$location', '$routeParams', 'URL',
                                            function($scope, $rootScope, $http, $location, $routeParams, URL) {
    $scope.textObjectURL = $routeParams;
    $scope.philoID = $scope.textObjectURL.pathInfo.split('/').join(' ');
    if ("byte" in $scope.textObjectURL) {
        $scope.byteOffset = $scope.textObjectURL.byte;
    } else {
        $scope.byteOffset = ''
    }
    var request = {
        method: "GET",
        url: $rootScope.philoConfig.db_url + '/' + URL.query({
            report: "navigation",
            philo_id: $scope.philoID,
            byte: $scope.byteOffset})
    }
    $http(request)
        .success(function(data, status, headers, config) {
            $scope.textObject = data;
            getTableOfContents();
        })
        .error(function(data, status, headers, config) {
            console.log("Error", status, headers)
        });
        
    var getTableOfContents = function() {
        var request = {
        method: "GET",
        url: $rootScope.philoConfig.db_url + '/' + URL.query({philo_id: $scope.philoID, script: 'get_table_of_contents.py'})
        }
        $http(request)
            .success(function(data, status, headers, config) {
                $scope.tocObject = data;
                $("#show-toc").removeAttr("disabled");
                adjustTocHeight(100);
            })
            .error(function(data, status, headers, config) {
                console.log("Error", status, headers)
            });
    }
    
    // Previous and next button follow scroll
    $('#nav-buttons, #toc-container').affix({
        offset: {
        top: function() {
            return (this.top = $('#nav-buttons').offset().top)
            }
        }
    });
    
    $('#nav-buttons').on('affix.bs.affix', function() {
        $(this).addClass('fixed');
        $("#toc-container").addClass('fixed');
        adjustTocHeight();
        $('#back-to-top').velocity("stop").velocity('fadeIn', {duration: 200});
    });
    $('#nav-buttons').on('affix-top.bs.affix', function() {
        $(this).removeClass('fixed');
        $("#toc-container").removeClass('fixed').css('position', 'static');
        adjustTocHeight();
        $('#back-to-top').velocity("stop").velocity('fadeOut', {duration: 200});
    });
    
    $('#back-to-top').click(function() {
        $("body").velocity('scroll', {duration: 800, easing: 'easeOutCirc', offset: 0});
    })
    
    var adjustTocHeight = function (num) {
        // Make sure the TOC is no higher than viewport
        if ($(document).height() == $(window).height()) {
            var toc_height = $(window).height() - $('#nav-buttons').position().top - $('#nav-buttons').height() - $('#toc-titlebar').height() - 59;
        } else {
            var toc_height = $(window).height() - $('#nav-buttons').position().top - $('#toc-titlebar').height() - 59;
        }
        if (typeof num !="undefined") {
            toc_height = toc_height - num;
        }
        $('#toc-content').velocity("stop").velocity({'max-height': toc_height + 'px'});
    }
    
    $scope.tocOpen = false;
    $scope.openTableOfContents = function() {
        if ($scope.tocOpen) {
            $scope.closeTableOfContents();
        } else {
            if ($(document).height() == $(window).height()) {
                $('#toc-container').css('position', 'static');
            }
            $('#toc-wrapper').css('opacity', 1);
            $('#nav-buttons').addClass('col-md-offset-4');
            $('#toc-wrapper').addClass('show');
            $scope.tocOpen = true;
            setTimeout(function() {
                adjustTocHeight();
                // TODO: find why this doesn't work
                var scrollToID = $('#' + $scope.tocObject.philo_id.join('-'));
                scrollToID.velocity("scroll", {duration: 500, container: $("#toc-content") });
                scrollToID.addClass('current-obj');
            }, 300);
        }
    }
    $scope.closeTableOfContents = function() {
        $scope.tocOpen = false;
        setTimeout(function() {
            if ($(document).height() == $(window).height()) {
                $('#toc-container').css('position', 'static');
            }
        });
        $('#nav-buttons').removeClass('col-md-offset-4');
    }
    
    
    $scope.$on('$viewContentLoaded', function() {
        scrollToHighlight();
    });
    var scrollToHighlight = function() {
        var word_offset = $('.highlight').eq(0).offset().top;
        if (word_offset == 0) {
            var note = $('.highlight').parents('.note-content');
            note.show(); // The highlight is in a hidden note
            word_offset = $('.highlight').offset().top;
            $('.highlight').parents('.note-content').hide();
        }
        if ($('.highlight').eq(0).parents('.note-content').length) {
            $("body").velocity('scroll', {duration: 800, easing: 'easeOutCirc', offset: word_offset - 60, complete: function() {
                $('.highlight').parents('.note-content').prev('.note').trigger('focus');}}
            );
        } else {
            $("body").velocity('scroll', {duration: 800, easing: 'easeOutCirc', offset: word_offset - 40});
        }
    }
}]);