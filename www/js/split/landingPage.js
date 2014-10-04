"use strict";

$(document).ready(function() {
    
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
        var target = $(this).data('target');
        console.log(target)
        var contentArea = $("#" + target);
        var available_links = [];
        if (contentArea.is(':empty')) {
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
                        content += '<a href="' + data[i].link + '">' + data[i].author + ' (' + data[i].count + ")</a></li>";
                    } else if (type == "title" || type == "year") {
                        content += '<a href="' + data[i].link + '"><i>' + data[i].title + '</i></a> (' + data[i].author + ")</li>";
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
            $('div[id$="-range-display"] div').hide();
            contentArea.show();
            $('#landing-page-content').show();
        }
    });
    
});