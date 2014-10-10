"use strict";

$(document).ready(function() {
    
    var pathname = window.location.pathname.replace('dispatcher.py/', '');
    var db_url = webConfig['db_url'];
    var q_string = window.location.search.substr(1);
    
    // Load slimScroll plugin
    $.getScript(webConfig['db_url'] + '/js/plugins/jquery.slimscroll.min.js');
    
    $('.sidebar-option').click(function() {
        var header = $(this).parent().prevAll('.dropdown-header').eq(0).text();
        var facet = $(this).data('value');
        var alias = $(this).data('display');
        var script = $(this).data('script');
        $('#menu-header').html(header);
        var header_value = webConfig.metadata_aliases[alias] || alias;
        $('#selected-sidebar-option').html(header_value);
        showSidebar();
        sidebarReports(q_string, db_url, facet, script);
    });
    $('#hide-sidebar-button').click(function() {
        hideSidebar();
    });
    
});


function sidebarReports(q_string, db_url, value, script_call) {
    // store the selected field to check whether to kill the ajax calls in populate_sidebar
    $('#selected-sidebar-option').data('selected', value);
    
    // Get total results
    var total_results = parseInt($('#total_results').text());
    
    $('#frequency_table').empty().show();
    $('.progress').hide();
    if (typeof sessionStorage[script_call] == "undefined") {
        // Initialize progress bar for sidebar
        var percent = 100 / total_results * 100;
        $(".progress").show();
        updateProgressBar(percent);
        $('#selected-sidebar-option').data('interrupt', false)
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
        $("#frequency_container").show();
        $('#frequency_table').slimScroll({height: container_height});
    }
}
function showSidebar() {
    if ($('#sidebar').css('display') == 'none') {
        $('#results_container').removeClass('col-xs-12').addClass('col-xs-8');
        $('#sidebar').show();
        $('#hide-sidebar-button').show();
    }
}
function hideSidebar() {
    $('#results_container').removeClass('col-xs-8').addClass('col-xs-12');
    $('#hide-sidebar-button').hide();
    $('#sidebar').hide()
    //$("#hide_sidebar").hide().data('interrupt', true);
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
    for (var key in full_results) {
        sorted_list.push([key, full_results[key]]);
    }
    sorted_list.sort(function(a,b) {return b[1].count - a[1].count});
    
    return [sorted_list, full_results]
}

function mergeCollocResults(full_results, new_data) {
    if (typeof full_results === 'undefined') {
        full_results = new_data;
    } else {
        for (var key in new_data) {
            if (key in full_results) {
                full_results[key] += new_data[key];
            }
            else {
                full_results[key] = new_data[key];
            }
        }
    }
    var sorted_list = [];
    for (var k in full_results) {
        sorted_list.push([k, full_results[k]]);
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
        var script_call_interval = script_call + "&interval_start=" + interval_start + "&interval_end=" + interval_end;
        if (interval_start === 0) {
            interval_start = 1000;
        }
        $.getJSON(script_call_interval, function(data) {
            if ($('#selected-sidebar-option').data('interrupt') != true && $('#selected-sidebar-option').data('selected') == field) {
                if (field != "collocation_report") {
                    var merge = mergeResults(full_results, data);
                } else {
                    var merge = mergeCollocResults(full_results, data);
                }
                var sorted_list = merge[0];
                var new_full_results = merge[1];
                update_sidebar(sorted_list, field);
                populate_sidebar(script_call, field, total_results, interval_start, interval_end, new_full_results);
                if (interval_end < total_results) {
                    var percent = interval_end / total_results * 100;
                    updateProgressBar(percent);
                }
            } else {
                // This won't affect the full collocation report which can't be interrupted
                // when on the page
                $('#selected-sidebar-option').data('interrupt', false);
            }
        });
    } else {
        updateProgressBar(100)
        $(".progress").delay(500).velocity('slideUp', {complete: function() {$('.progress-bar').width(0).text("0%");}});
        $('#frequency_table').slimScroll({height: $('#results_container').height() - 14});
        if (typeof(localStorage) == 'undefined' ) {
            alert('Your browser does not support HTML5 localStorage. Try upgrading.');
        } else {
            try {
                sessionStorage[script_call] = JSON.stringify($('#frequency_table').html());
            } catch(e) {
                sessionStorage.clear();
                sessionStorage[script_call] = JSON.stringify($('#frequency_table').html());
            }
        }
    }
}

function update_sidebar(sorted_list, field) {
    var newlist = "";
    if (field == "collocation_report") {
        newlist += "<p id='freq_sidebar_status'>Collocates within 5 words left or right</p>";
        var q_string = window.location.search.substr(1);
    }
    var limit = false;
    if (sorted_list.length > 1000) {
        sorted_list = sorted_list.slice(0,1000);
        limit = 1000;
    }
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
            full_link = '<span style="vertical-align: 10px"><span class="dot"></span>N/A</span>'; // Set to N/A for display only
        } else {
            full_link = '<a id="freq_sidebar_text" href="' + link + '"><span class="dot"></span>' + result + '</a>';
        }
        newlist += '<li>';
        newlist += full_link + '<span style="float:right;display:inline-block;padding-right: 5px;">' + count + '</span></li>';
    }
    if (limit) {
        newlist += '<p>For performance reasons, this list is limited to 1000 results</p>';
    }
    $("#frequency_table").replaceHtml(newlist);
    $("#hide_sidebar").css('display', 'inline-block');
    $("#frequency_container").show();
}
