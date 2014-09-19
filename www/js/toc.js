"use strict";

$(document).ready(function() {
    //var new_margin = parseInt($('#philologic_response').css("margin-top")) + 10;
    //$('#philologic_response').css("margin-top", new_margin + "px");
    var pathname = window.location.pathname.replace('dispatcher.py/', '');
    var my_path = pathname.replace(/\/\d+.*$/, '/');
    var doc_id = pathname.replace(my_path, '').replace(/(\d+)\/*.*/, '$1');
    var philo_id = doc_id + ' 0 0 0 0 0 0'
    var script = my_path + '/scripts/get_table_of_contents.py?philo_id=' + philo_id;
    $.get(script, function(data) {
        $("#toc-content").html(data);
        $("#toc_wrapper").fadeIn();
    });
    $('#show-header').click(function() {
        if ($('#show-header').text() == "Show Header") {
            $.get(my_path + '/scripts/get_header.py?philo_id=' + philo_id, function(data) {
                $('#tei-header').append(data).show();
                $('#show-header').html("Hide Header");                
            });
        } else {
            $('#tei-header').hide().empty();
            $('#show-header').html("Show Header");
        }
    });
});
