$(document).ready(function() {
    
    //jQueryUI theming
    $('#frequency_by, #hide_sidebar').button();
    
    // Load slimScroll plugin
    $.getScript(webConfig['db_url'] + '/js/plugins/jquery.slimscroll.min.js');
    
    $("#hide_sidebar").click(function(e) {
        e.stopPropagation();
        hide_frequency();
    });
    
});


function sidebar_reports(q_string, db_url, pathname) {
    $("#frequency_by").click(function(e) {
        e.stopPropagation();
        if ($('#hide_sidebar').css('display') == 'none') {
            $('#frequency_field').css('right', '0');
        } else {
            $('#frequency_field').css('right', '39px');
        }
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
        var value = $(this).data('value');
        
        // store the selected field to check whether to kill the ajax calls in populate_sidebar
        $('#frequency_by').data('selected', value);
        
        // Get total results
        var total_results = parseInt($('#total_results').text());
        
        // Show which option was chosen
        var display_value = $(this).data('display');
        if (typeof webConfig.metadata_aliases[display_value] != 'undefined') {
            display_value = webConfig.metadata_aliases[display_value];
        }
        $('#displayed_sidebar_value').html(display_value);
        
        show_sidebar(q_string, db_url, pathname,value);
        $('#frequency_table').empty();
        if (value != 'collocation_report') {
            var script_call = db_url + "/scripts/get_frequency.py?" + q_string + "&frequency_field=" + value;
        } else {
            var script_call = db_url + "/scripts/collocation_fetcher.py?" + q_string + "&full_report=False";
        }
        $('#progress_bar').hide();
        if (typeof sessionStorage[script_call] == "undefined") {
            // Initialize progress bar for sidebar
            $('#progress_bar').progressbar({max: total_results});
            $('#progress_bar').progressbar({value: 100});
            var percent = 100 / total_results * 100;
            $('.progress-label').text(percent.toString().split('.')[0] + '%');
            $('.progress-label').text('0%');
            $('#progress_bar').progressbar({value: 0.1});
            $("#progress_bar").show();
            $('#hide_sidebar').data('interrupt', false)
            var full_results;
            populate_sidebar(script_call, value, total_results, 0, full_results);
        } else {
            var table = JSON.parse(sessionStorage[script_call]);
            $('#frequency_table').html(table).show(); 
            $("#hide_sidebar").css('display', 'inline-block');
            var container_height = $('#results_container').height() - 14;
            var freq_height = $('#frequency_container').height();
            if (freq_height > container_height) {
                container_height = freq_height;
            }
            $('#frequency_table').slimScroll({height: container_height});
        }
    });
}
function show_sidebar() {
    if ($('#frequency_container').css('display') == 'none') {
        $("#results_container, .cite").velocity({
            "width": "-=410"},
            150, function() {
                    $('#frequency_container').height($('#results_container').height() -14 + 'px');
                    $('#frequency_container').show();
                    $('#sidebar_display').css('opacity', 1);
                }
        );
    }
}
function hide_frequency() {
    if ($('#frequency_container').css('display') != 'none') {
        $("#hide_sidebar").hide().data('interrupt', true);;
        $("#frequency_table").empty().hide();
        $('#frequency_container').hide();
        $('#sidebar_display').css('opacity', 0);
        $("#results_container, .cite").velocity({
            "width": "+=410"},
            150);    
        }
}

function mergeResults(full_results, new_data) {
    if (typeof full_results === 'undefined') {
        full_results = new_data;
    } else {
        for (key in new_data) {
            if (key in full_results) {
                full_results[key]['count'] += new_data[key]['count'];
            }
            else {
                full_results[key] = new_data[key];
            }
        }
    }
    var sorted_list = [];
    for (key in full_results) {
        sorted_list.push([key, full_results[key]]);
    }
    sorted_list.sort(function(a,b) {return b[1].count - a[1].count});
    
    return [sorted_list, full_results]
}

function mergeCollocResults(full_results, new_data) {
    if (typeof full_results === 'undefined') {
        full_results = new_data;
    } else {
        for (key in new_data) {
            if (key in full_results) {
                full_results[key] += new_data[key];
            }
            else {
                full_results[key] = new_data[key];
            }
        }
    }
    var sorted_list = [];
    for (key in full_results) {
        sorted_list.push([key, full_results[key]]);
    }
    sorted_list.sort(function(a,b) {return b[1] - a[1]});
    
    return [sorted_list, full_results]
}

function populate_sidebar(script_call, field, total_results, interval_start, interval_end, full_results) {
    if (interval_start === 0) {
        interval_end = 1000;
    } else if (interval_end === 1000) {
        interval_end = 21000;
    } else {
        interval_start += 20000;
        interval_end += 20000;
    }
    if (interval_start < total_results) {
        script_call_interval = script_call + "&interval_start=" + interval_start + "&interval_end=" + interval_end;
        if (interval_start === 0) {
            interval_start = 1000;
        }
        $.getJSON(script_call_interval, function(data) {
            if ($('#hide_sidebar').data('interrupt') != true && $('#frequency_by').data('selected') == field) {
                if (field != "collocation_report") {
                    var merge = mergeResults(full_results, data);
                } else {
                    var merge = mergeCollocResults(full_results, data);
                }
                sorted_list = merge[0];
                new_full_results = merge[1];
                update_sidebar(sorted_list, field);
                populate_sidebar(script_call, field, total_results, interval_start, interval_end, new_full_results);
                var total = $('#progress_bar').progressbar("option", "max");
                var percent = interval_end / total * 100;
                if (interval_end < total) {
                    var progress_width = $('#progress_bar').width() * percent / 100;
                    $('#progress_bar .ui-progressbar-value').animate({width: progress_width}, 'fast', 'easeOutQuint', {queue: false});
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
        $('#frequency_table').slimScroll({height: $('#results_container').height() - 14});
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
    if (field == "collocation_report") {
        newlist += "<p id='freq_sidebar_status'>Collocates within 5 words left or right</p>";
        q_string = window.location.search.substr(1);
    }
    sorted_list = sorted_list.slice(0,300);
    for (var item=0; item < sorted_list.length; item++) {
        var result = sorted_list[item][0];
        if (field == 'collocation_report') {
            var count = sorted_list[item][1];
            var link = "?" + colloc_linker(result, q_string, "all", count);
        } else {
            var link = sorted_list[item][1]['url'];
            var count = sorted_list[item][1]['count'];
        }
        // The following if clause is a workaround for a bug with NULL queries
        // TODO: remove once the bug is fixed in the library.
        var full_link;
        if (result == "NULL") {
            full_link = '<span style="vertical-align: 10px">' + result + '</span>';
        } else {
            full_link = '<a id="freq_sidebar_text" href="' + link + '">' + result + '</a>';
        }
        newlist += '<li>';
        newlist += '<span class="ui-icon ui-icon-bullet" style="display: inline-block;vertical-align:8px;"></span>';
        newlist += full_link + '<span style="float:right;display:inline-block;padding-right: 5px;">' + count + '</span></li>';
    }
    $("#frequency_table").hide().empty().html(newlist).velocity('fadeIn', {duration: 200});
    $("#hide_sidebar").css('display', 'inline-block');
    $("#frequency_container").show();
}
