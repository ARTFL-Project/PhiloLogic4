"use strict";

$(document).ready(function() {
    
    
    if (webConfig.dictionary == false) { // default
        //Handle click on button
        $('#landingGroup button').on('touchstart click', function() {
            var selected = $(this).attr('id');
            $('#landingGroup button').removeClass('active');
            $(this).addClass('active');
            if (selected == "authorGroup") {
                $("#landing-page-authors").show();
                $("#landing-page-titles").hide()
                $("#landing-page-years").hide();
            } else if (selected == "titleGroup") {
                $("#landing-page-titles").show();
                $("#landing-page-authors").hide();
                $("#landing-page-years").hide();
            } else if (selected == "yearGroup") {
                $("#landing-page-years").show();
                $("#landing-page-authors").hide();
                $("#landing-page-titles").hide();
            }
        });
        
        //Ajax calls to pull content data
        $('#author-range-selectors td, #title-range-selectors td, #year-range-selectors td').click(function() {
            var range = $(this).data('range');
            var type = $(this).parents('table').data('type');
            var script = $('#landingGroup').data('script') + type + "&range=" + range;
            var contentId = type + '-' + range;
            var contentDiv = '<div id="' + contentId + '"></div>';
            var available_links = [];
            var visibleDiv = $('#landing-page-content').find('div:visible').velocity('transition.slideRightOut', {duration: 200});
            if ($('#' + contentId).length == 0) {
                $('#landing-page-content').append(contentDiv);
                var contentArea = $('#' + contentId);
                $.getJSON(script, function(data) {
                    var html = '';
                    var title;
                    for (var i=0; i < data.length; i++) {
                        if (type == "author" || type == "title") {
                            var prefix = data[i][type].slice(0,1).toLowerCase();
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
                        if (type == "author") {
                            var content = '<li class="col-xs-12 col-sm-6">';
                            content += data[i].cite + "</li>";
                        } else if (type == "title" || type == "year") {
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
                        contentElements.velocity('transition.slideLeftIn', {duration: 400, stagger: 20, complete: function() {
                            contentArea.velocity({opacity: 1})}}); // in case opacity doesn't get set
                    });
                });
            } else {
                var contentArea = $('#' + contentId);
                var contentElements = contentArea.find('ul');
                contentArea.show();
                $('#landing-page-content').show();
                contentElements.velocity('transition.slideLeftIn', {duration: 400, stagger: 20, complete: function() {
                            contentArea.velocity({opacity: 1})}}); // in case opacity doesn't get set
            }
        });
    } else {
        var script = $('#dico-landing-volume').data('script');
        var list = $(this).find('ul');
        $.getJSON(script, function(data) {
            for (var i=0; i < data.length; i++) {
                console.log(data[i].philo_id)
                var li = '<li class="list-group-item"><a href="dispatcher.py/' + data[i].philo_id[0] + '">' + data[i].title + '</a></li>';
                list.append(li);
            }
        });
        $('#dico-landing-alpha td').on('click touchstart', function() {
            var script = $('#dico-landing-alpha').data('script') + '^' + $(this).text() + '.*';
            window.location = script;
        });
    }
    
});