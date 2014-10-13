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
        $('#author-range-selectors a, #title-range-selectors a, #year-range-selectors a').click(function() {
            var range = $(this).data('range');
            var type = $(this).parent().parent().data('type');
            var script = $('#landingGroup').data('script') + type + "&range=" + range;
            var contentId = type + '-' + range;
            var contentDiv = '<div id="' + contentId + '"></div>';
            var available_links = [];
            if ($('#' + contentId).length == 0) {
                $('#' + type + "-range-display").append(contentDiv);
                var contentArea = $('#' + contentId);
                $.getJSON(script, function(data) {
                    $('div[id$="-range-display"] div').hide();
                    var html = '';
                    var title;
                    for (var i=0; i < data.length; i++) {
                        if (type == "author" || type == "title") {
                            var prefix = data[i][type].slice(0,1).toLowerCase();
                        } else {
                            prefix = data[i].year;
                        }
                        if (i == 0) {
                            html += '<h4 id="' + prefix + '" style="border-bottom: 1px solid #eee">' + prefix.toUpperCase() + '</h4>';
                            html += '<ul style="margin-bottom: 20px;">';
                            title = prefix;
                            available_links.push(title);
                        }
                        if (prefix != title) {
                            html += '</ul><h4 id="' + prefix + '" style="border-bottom: 1px solid #eee">' + prefix.toUpperCase() + '</h4><ul style="margin-bottom: 20px;">';
                            title = prefix;
                            available_links.push(title);
                        }
                        var content = '<li style="padding-top: 10px;padding-bottom: 10px;border-bottom: 1px solid #eee">'
                        if (type == "author") {
                            content += data[i].cite + "</li>";
                        } else if (type == "title" || type == "year") {
                            content += data[i].cite + "</li>";
                        }
                        html += content;
                    }
                    html += '</ul>';
                    contentArea.html(html).promise().done(function() {
                        contentArea.show();
                        $('#landing-page-content').show();
                    });
                });
            } else {
                var contentArea = $('#' + contentId);
                $('div[id$="-range-display"] div').hide();
                contentArea.show();
                $('#landing-page-content').show();
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