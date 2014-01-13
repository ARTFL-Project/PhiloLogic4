$(document).ready(function() {
    
    //jQueryUI theming
    $('#time_series_buttons').buttonset();
    
    var db_url = db_locals['db_url'];
    
    var interval = $("#absolute_time").data('interval');
    var height = $(window).height() - $('#footer').height() - $('#initial_report').height() - $('#header').height() - 200;
    $('#test_time_series').css('height', height);
    var body_width = parseInt($('body').width());
    $('#test_time_series, #first_division, #middle_division, #top_division').width(body_width-90 + 'px');
    
    // Default data display
    var full_results;
    var abs_data = eval($("#absolute_time").data('value'));
    var merge_abs = merge_time_results(full_results, abs_data);
    var sorted_abs = merge_abs[0]
    var full_abs = merge_abs[1]
    drawFromData(sorted_abs, interval, 'absolute_time');
    var total = parseInt($('#progress_bar').data('total'));
    $('#progress_bar').progressbar({max: total});
    $('#progress_bar').progressbar({value: 100});
    var percent = 100 / total * 100;
    $('.progress-label').text(percent.toString().split('.')[0] + '%');
    $('#progress_bar').width($('#initial_report').width());
    $('#progressive_bar').show();
    var rel_data = eval($(this).data('value'));
    var full_rel = merge_time_results(full_results, rel_data)[1];
    progressiveLoad(db_url, total, interval, 0, 100, full_abs, full_rel);
    
    
    $('#absolute_time').click(function() {
        var abs_data = JSON.parse($(this).data('value'));
        abs_data = merge_time_results(full_results, abs_data)[0];
        var interval = $("#absolute_time").data('interval');
        drawFromData(abs_data, interval, $(this).attr('id'));
    });
    $('#relative_time').click(function() {
        var mydata = JSON.parse($(this).data('value'));
        mydata = merge_time_results(full_results, mydata)[0];
        var interval = $("#absolute_time").data('interval');
        drawFromData(mydata, interval, $(this).attr('id'));
    });
    $('.graph_bar').click(function() {
        window.location = $(this).data('href');
    });
    
    $(window).resize(function() {
        waitForFinalEvent(function() {
            var diff = parseInt($('body').width()) - body_width;
            var chart_width = body_width - 90 + diff;
            $('#test_time_series, #first_division, #middle_division, #top_division').width(chart_width + 'px');
            $('.graph_bar, .graph_years').remove();
            var height = $(window).height() - $('#footer').height() - $('#initial_report').height() - $('#header').height() - 200;
            $('#test_time_series').css('height', height);
            $('#test_time_series').fadeOut('fast', function() {
                $(this).show();
                drawFromData(mydata, interval);
            });
        }, 500, $('#test_time_series').attr('id'));
    });
    
});

function progressiveLoad(db_url, total_results, interval, interval_start, interval_end, abs_full_results, rel_full_results) {
    var q_string = window.location.search.substr(1);
    var script = db_url + "/scripts/time_series_fetcher.py?" + q_string
    if (interval_start === 0) {
        interval_start = 100;
        interval_end = 600;
    } else {
        interval_start += 500;
        interval_end += 500;
    }
    if (interval_start < total_results) {
        script_call = script + "&interval_start=" + interval_start + "&interval_end=" + interval_end;
        $.getJSON(script_call, function(data) {
            var abs_merge = merge_time_results(abs_full_results, data[0]);
            abs_sorted_list = abs_merge[0];
            abs_new_full_results = abs_merge[1];
            $('#absolute_time').data('value', JSON.stringify(abs_new_full_results));
            
            var rel_merge = merge_time_results(rel_full_results, data[1]);
            rel_sorted_list = rel_merge[0];
            rel_new_full_results = rel_merge[1];
            $('#relative_time').data('value', JSON.stringify(rel_new_full_results));
            
            var selected_view = $('input[name=freq_type]:checked').attr('id');
            $('.graph_years').remove();
            $('.graph_bar').remove();
            if (selected_view == 'absolute_time') {
                drawFromData(abs_sorted_list, interval, selected_view);
            } else {
                drawFromData(rel_sorted_list, interval, selected_view);
            }
            
            
            progressiveLoad(db_url, total_results, interval, interval_start, interval_end, abs_new_full_results, rel_new_full_results);
            var total = $('#progress_bar').progressbar("option", "max");
            var percent = interval_end / total * 100;
            if (interval_end < total) {
                $('#progress_bar').progressbar({value: interval_end});
                $('.progress-label').text(percent.toString().split('.')[0] + '%');
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
                sessionStorage[script] = JSON.stringify($('#philologic_response').html());
            } catch(e) {
                if (e == QUOTA_EXCEEDED_ERR) {
                    sessionStorage.clear();
                    sessionStorage[script_call] = JSON.stringify($('#philologic_response').html());
                }
            }
        }
    }
}

// Taken from common.js. Differs in that it sorts by date and not count
function merge_time_results(full_results, new_data) {
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
    sorted_list.sort(function(a,b) {return a[0] - b[0]});
    
    return [sorted_list, full_results]
}

function drawFromData(data, interval, frequency_type) {
    var max_count = 0;
    var width = adjustWidth(data.length);
    var margin = 0;
    
    for (var i=0; i < data.length; i++) {
        var count = Math.round(data[i][1]['count']);
        // Test if the chart has already been drawn
        if ($('.graph_bar').length < (data.length)) {
            var year = data[i][0];
            console.log(i, year)
            if (i > 0) {
                margin += width + 1;
            }
            var graph_bar = "<span class='graph_bar' title='" + count + " occurrences' style='margin-left:" + margin + "px' data-count='" + Math.round(count, false) + "' data-year='" + year + "'></span>";
            $('#test_time_series').append(graph_bar);
            $('.graph_bar').eq(i).width(width + 'px');
            $('.graph_bar').eq(i).data('href', data[i][1]['url'])
            var year_margin = margin - 2;
            var year = '<span style="display:none;position:absolute;bottom:0;margin-bottom:-30px;margin-left:' + year_margin + 'px;" class="graph_years">' + year + '</span>';
            $('#test_time_series').append(year);
        } else {
            $('.graph_bar').eq(i).data('count', count);
            $('.graph_bar').eq(i).attr('title', Math.round(count, false) + ' occurrences');
        }
        if (count > max_count) {
            max_count = count;
        }
    }
    
    // Make sure the years don't overlap
    if (width > 12) {
        $('.graph_years').show();
        if (width < 18) {
            $('.graph_years').css('font-size', '70%');
        }
    } else {
        var count = 0;
        $('.graph_years').eq(0).show();
        //$('.graph_years').eq($('.graph_years').length - 1).show();
        var num = truncate($('.graph_years').length / 10);
        $('.graph_years').each(function() {
            count += 1;
            if (count == num) {
                $(this).show();
                count = 0;
            }
        })
    }
    
    // Draw three lines along the X axis to help visualize frequencies
    if (frequency_type == "relative_time") {
        $('#side_text').html('Occurrences per 1,000,000 words');
        var top_number = Math.round(max_count);
        var middle_number = Math.round(max_count / 3 * 2);
        var bottom_number = Math.round(max_count / 3);
        $('#top_number').html(top_number + ' occurrences on average');
        $('#middle_number').html(middle_number + ' occurrences on average');
        $('#first_number').html(bottom_number + ' occurrences on average');
    } else {
        $('#side_text').html('Total occurrences');
        var top_number = Math.round(max_count);
        var middle_number = Math.round(max_count / 3 * 2);
        var bottom_number = Math.round(max_count / 3);
        $('#top_number').html(top_number + ' occurrences');
        $('#middle_number').html(middle_number + ' occurrences');
        $('#first_number').html(bottom_number + ' occurrences');
    }
    
    
    multiplier = ($('#test_time_series').height() - 10) / max_count; 
    
    $('.graph_bar').each(function() {
        var count = $(this).data('count');
        var height = count * multiplier;
        $(this).attr('data-height', height)
        $(this).eq(0).animate({height: height + 'px'});
    });
    $('.graph_bar').tooltip({ position: { my: "left top+10", at: "left bottom", collision: "flipfit" } }, { track: true });
    clickOnChart();
}

function adjustWidth(elem_num) {
    var container_width = parseInt($('#test_time_series').width());
    var separation_margin = 1 * elem_num;
    var bar_width = (container_width - separation_margin) / elem_num;
    return bar_width;
}

function truncate(num) {
    new_num = String(num).replace(/(\d+).*/, '$1');
    return parseInt(new_num);  
}

function clickOnChart() {
    $('#graph_bar').click(function() {
        window.location = $(this).data('href');
    });
}
