$(document).ready(function() {
    
    //jQueryUI theming
    $('#frequency_by, #hide_sidebar').button();
    
    // Initialize progress bar for sidebar
    var total_results = parseInt($('#total_results').text());
    $('#progress_bar').progressbar({max: total_results});
    $('#progress_bar').progressbar({value: 100});
    var percent = 100 / total_results * 100;
    $('.progress-label').text(percent.toString().split('.')[0] + '%');
});


function sidebar_reports(q_string, db_url, pathname) {
    $("#frequency_by").click(function(e) {
        e.stopPropagation();
        if ($('#frequency_field').css('display') == 'none') {
            $('#frequency_field').css('width', $("#frequency_by").width());
            $('#frequency_field').slideDown('fast', 'swing');
        } else {
            $('#frequency_field').slideUp('fast', 'swing');
        }
    });
    $(document).click(function() {
        $('#frequency_field').slideUp('fast', 'swing');
    });
    $('.sidebar_option').click(function(evt) {
        $('#frequency_field').slideUp('fast', 'swing');
        value = $(this).data('value');
        
        // store the selected field to check whether to kill the ajax calls in populate_sidebar
        $('#frequency_by').data('selected', value);
        
        $('#displayed_sidebar_value').html(value);
        show_sidebar(q_string, db_url, pathname,value);
        var total_results = parseInt($('#total_results').text());
        $('#frequency_table').empty();
        if (value != 'collocate') {
            var script_call = db_url + "/scripts/get_frequency.py?" + q_string + "&frequency_field=" + value;
        } else {
            var script_call = db_url + "/scripts/collocation_fetcher.py?" + q_string + "&full_report=False";
        }
        $('#progress_bar').hide();
        if (typeof sessionStorage[script_call] == "undefined") {
            $('.progress-label').text('0%');
            $('#progress_bar').progressbar({value: 0});
            $("#progress_bar").show();
            var full_results;
            populate_sidebar(script_call, value, total_results, 0, full_results);
        } else {
            var table = JSON.parse(sessionStorage[script_call]);
            $('#frequency_table').html(table); 
            $('#frequency_container').show();
            $("#hide_sidebar").css('display', 'inline-block');
        }
    });
    $("#hide_sidebar").click(function() {
        hide_frequency();
    });
}
function show_sidebar() {
    $("#results_container").animate({
        "margin-right": "410px"},
        150, function() {
                getCitationWidth();
                $('#frequency_container').height($('#results_container').height() -14 + 'px');
            }
    );
}
function hide_frequency() {
    $("#hide_sidebar").hide().data('interrupt', true);;
    $("#frequency_table").empty().hide();
    $('#frequency_container').hide();
    $(".results_container").animate({
        "margin-right": "0px"},
        150, function() {
                getCitationWidth();
        }
    );
}
function populate_sidebar(script_call, field, total_results, interval_start, interval_end, full_results) {
    if (interval_start === 0) {
        interval_end = 50;
    } else if (interval_end === 50) {
        interval_end = 2050;
    } else {
        interval_start += 2000;
        interval_end += 2000;
    }
    if (interval_start < total_results) {
        script_call_interval = script_call + "&interval_start=" + interval_start + "&interval_end=" + interval_end;
        if (interval_start === 0) {
            interval_start = 100;
        }
        $.getJSON(script_call_interval, function(data) {
            if ($('#hide_sidebar').data('interrupt') != true && $('#frequency_by').data('selected') == field) {
                var merge = merge_results(full_results, data);
                sorted_list = merge[0];
                new_full_results = merge[1];
                update_sidebar(sorted_list, field);
                populate_sidebar(script_call, field, total_results, interval_start, interval_end, new_full_results);
                var total = $('#progress_bar').progressbar("option", "max");
                var percent = interval_end / total * 100;
                if (interval_end < total) {
                    $('#progress_bar').progressbar({value: interval_end});
                    $('.progress-label').text(percent.toString().split('.')[0] + '%');
                }
            } else {
                // This won't affect the full collocation report which can't be interrupted
                // when on the page
                $('#hide_sidebar').data('interrupt', false);
            }
        });
    } else {
        var total = $('#progress_bar').progressbar("option", "max");
        $('#progress_bar').progressbar({value: total});
        $('.progress-label').text('Complete!');
        $("#progress_bar").delay(500).slideUp();
        if (typeof(localStorage) == 'undefined' ) {
            alert('Your browser does not support HTML5 localStorage. Try upgrading.');
        } else {
            try {
                sessionStorage[script_call] = JSON.stringify($('#frequency_table').html());
            } catch(e) {
                if (e == QUOTA_EXCEEDED_ERR) {
                    sessionStorage.clear();
                    sessionStorage[script_call] = JSON.stringify($('#frequency_table').html());
                }
            }
        }
    }
}

function update_sidebar(sorted_list, field) {
    var newlist = "";
    if (field == "collocate") {
        newlist += "<p id='freq_sidebar_status'>Collocates within 5 words left or right</p>";
    }
    for (item in sorted_list.slice(0,300)) {
        var url = '<a id="freq_sidebar_text" href="' + sorted_list[item][1]['url'] + '">' + sorted_list[item][0] + '</a>';
        newlist += '<li style="white-space:nowrap;">';
        newlist += '<span class="ui-icon ui-icon-bullet" style="display: inline-block;vertical-align:8px;"></span>';
        newlist += url + '<span style="float:right;display:inline-block;padding-right: 5px;">' + sorted_list[item][1]['count'] + '</span></li>';
    }
    $("#frequency_table").hide().empty().html(newlist).fadeIn('fast');
    $("#hide_sidebar").css('display', 'inline-block');
    $("#frequency_container").show();
    $("#hide_sidebar").click(function() {
        hide_frequency();
    });
}