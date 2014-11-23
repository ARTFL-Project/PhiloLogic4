"use strict";

$(document).ready(function() {
    
    var db_url = webConfig['db_url'];
    var date_list = generateDateList();
    
    if (sessionStorage[window.location.href] == null) {
        
        // Calculate width and height of chart
        var height = $(window).height() - $('#footer').height() - $('#initial_report').height() - $('#header').height() - 190;
        $('#test_time_series').css('height', height);
        var body_width = parseInt($('body').width());
        $('#test_time_series, #first_division, #middle_division, #top_division').width(body_width-90 + 'px');        
        
        // Default data display
        var full_results;
        var abs_data = eval($("#absolute_time").data('value'));
        var merge_abs = merge_time_results(full_results, abs_data, date_list);
        var sorted_abs = merge_abs[0]
        var full_abs = merge_abs[1]
        var interval = $("#absolute_time").data('interval');
        drawFromData(sorted_abs, interval, 'absolute_time');
        // Fetch total results to make sure we always have the right number
        var total_hits_script = $('#search_arguments').data('script');
        $.getJSON(total_hits_script, function(data) {
            var total = data;
            $("#time-series-length").html(total);
            var percent = 3000 / total * 100;
            $('.progress').show();
            updateProgressBar(percent);
            var date_counts = eval($('#relative_time').data('datecount'));
            var script = $('#time_series_report').data('script');
            console.log(date_list)
            progressiveLoad(db_url, total, interval, 0, 3000, full_abs, date_counts, date_list, script);
        });
    } else {
        var time_series = JSON.parse(sessionStorage[window.location.href]);
        var date_counts = time_series['date_counts'];
        var abs_results = time_series['abs_results'];
        var total = $("#time-series-length").html(total);
        var script = $('#time_series_report').data('script');
        $('#relative_counts').data('value', relativeCount(abs_results, date_counts))
        progressiveLoad(db_url, total, interval, 0, 3000, abs_results, date_counts, date_list, script);
    }
    
    $(window).resize(function() {
        waitForFinalEvent(function() {
            var diff = parseInt($('body').width()) - body_width;
            var chart_width = body_width - 90 + diff;
            $('#test_time_series, #first_division, #middle_division, #top_division').width(chart_width + 'px');
            $('.graph_bar').remove();
            var height = $(window).height() - $('#footer').height() - $('#initial_report').height() - $('#header').height() - 190;
            $('#test_time_series').css('height', height);
            $('#test_time_series').fadeOut('fast', function() {
                $(this).show();
                var frequency = $('#time_series_buttons label.active').attr('id');
                var data = eval($('#' + frequency).data('value'));
                drawFromData(data, interval);
            });
        }, 500, $('#test_time_series').attr('id'));
    });
});

function generateDateList() {
    // Generate range of all dates
    var year_interval = parseInt($('#search_arguments').data('interval'));
    var start_date = normalizeDate($('#search_arguments').data('start'), year_interval);
    var end_date = parseInt($('#search_arguments').data('end'));
    var date_list = []
    for (var i = start_date; i <= end_date; i += year_interval) {
        date_list.push(i);
    }
    return date_list;
}

function progressiveLoad(db_url, total_results, interval, interval_start, interval_end, abs_full_results, full_date_counts, date_list, script) {
    var q_string = window.location.search.substr(1);
    var initial_end = interval_end;
    if (interval_start === 0) {
        interval_start = 3000;
        interval_end = 13000;
    } else {
        interval_start += 10000;
        interval_end += 10000;
    }
    if (initial_end < total_results) {
        var script_call = script + "&interval_start=" + interval_start + "&interval_end=" + interval_end;
        $.getJSON(script_call, function(data) {
            var abs_merge = merge_time_results(abs_full_results, data.results['absolute_count'], date_list);
            var abs_sorted_list = abs_merge[0];
            var abs_new_full_results = abs_merge[1];            
            drawFromData(abs_sorted_list, interval, "absolute_time");
            
            // Update date_counts
            for (var date in data.results['date_count']) {
                full_date_counts[date] = data.results['date_count'][date]
            }
            
            progressiveLoad(db_url, total_results, interval, interval_start, interval_end, abs_new_full_results, full_date_counts, date_list, script);
            if (interval_end < total_results) {
                var percent = interval_end / total_results * 100;
                updateProgressBar(percent)
            }
        });
    } else {
        // Store final sorted results
        var abs_results = sortResults(abs_full_results)
        $('#absolute_time').data('value', JSON.stringify(abs_results));
        
        // Generate relative frequencies from absolute frequencies and make button clickable again
        $("#relative_time").removeAttr("disabled");
        var relative_results = relativeCount(abs_results, full_date_counts);
        $('#relative_time').data('value', JSON.stringify(relative_results))
        
        // Create click event handler to switch between frequency types
        frequencySwitcher();
        
        updateProgressBar(100)
        var progress_height = $(".progress").height();
        $(".progress").delay(500).velocity("slideUp");
        $('.graph_bar').tooltip({html: true});
        //if (!(window.location.href in sessionStorage)) {
        //    saveTimeSeries(abs_full_results, full_date_counts)
        //}
    }
}

function normalizeDate(year, interval) {
    year = year.toString();
    if (interval == 10) {
        year = year.slice(0,-1) + '0';
    } else if (interval == '100') {
        year = year.slice(0,-2) + '00';
    } else if (interval == '50') {
        var decade = parseInt(year.slice(-2));
        if (decade < 50) {
            year = year.slice(0,-2) + '00';
        } else {
            year = year.slice(0,-2) + '50';
        }
    }
    return parseInt(year)
}

function frequencySwitcher() {
    $('#absolute_time, #relative_time').click(function() {
        var abs_data = eval($(this).data('value'));
        var interval = $(this).data('interval');
        drawFromData(abs_data, interval, $(this).attr('id'));
    });
}

function saveTimeSeries(full_abs_results, full_date_counts) {
    if (typeof(localStorage) == 'undefined' ) {
        alert('Your browser does not support HTML5 localStorage. Try upgrading.');
    } else {
        try {
            sessionStorage[window.location.href] = JSON.stringify({"abs_results": full_abs_results, "date_counts": full_date_counts});
        } catch(e) {
            if (e == QUOTA_EXCEEDED_ERR) {
                sessionStorage.clear();
                sessionStorage[window.location.href] = JSON.stringify({"abs_results": full_abs_results, "date_counts": full_date_counts});
            }
        }
    }
}

function relativeCount(absolute_counts, date_counts) {
    var relative_counts = []
    for (var i=0; i < absolute_counts.length; i++) {
        var relative_count = absolute_counts[i][1] / date_counts[absolute_counts[i][0]] * 1000000;
        relative_counts.push([absolute_counts[i][0], relative_count]);
    }
    return relative_counts
}

function addMissingDates(full_results, date_list) {
    for (var i = 0; i < date_list.length; i++) {
        if (!(date_list[i] in full_results)) {
            full_results[date_list[i]] = 0;
        }
    }
    return full_results
}

// Taken from common.js. Differs in that it sorts by date and not count
function merge_time_results(full_results, new_data, date_list) {
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
    full_results = addMissingDates(full_results, date_list);
    var sorted_list = sortResults(full_results);
    return [sorted_list, full_results]
}

function sortResults(full_results) {
    var sorted_list = [];
    for (var key in full_results) {
        sorted_list.push([key, full_results[key]]);
    }
    sorted_list.sort(function(a,b) {return a[0] - b[0]});
    return sorted_list
}

function yearToTimeSpan(year, interval) {
    var end_date = parseInt($('#search_arguments').data('end'));
    year = String(year);
    if (interval == '10') {
        year = year.slice(0,-1) + '0';
        var next = parseInt(year) + 9;
        if (next > end_date) {
            next = String(end_date)
        } else {
            next = String(next);   
        }
        year = year + '-' + next;
    }
    else if (interval == '100') {
        year = year.slice(0,-2) + '00';
        var next = parseInt(year) + 99;
        if (next > end_date) {
            next = String(end_date)
        } else {
            next = String(next);   
        }
        year = year + '-' + next
    } else if (interval == '50') {
        var decade = parseInt(year.slice(-2));
        if (decade < 50) {
            var next = parseInt(year.slice(0,-2) + '49');
            if (next > end_date) {
                next = String(end_date)
            } else {
                next = String(next);   
            }
            year = year.slice(0,-2) + '00' + '-' + next;
        } else {
            var next = year.slice(0,-2) + '99';
            if (next > end_date) {
                next = String(end_date)
            } else {
                next = String(next);   
            }
            year = year.slice(0,-2) + '50' + '-' + next;
        }
    }
    return year
}

function clickOnChart(interval) {
    $('.graph_bar').click(function() {
        var year = String($(this).data('year'));
        year = yearToTimeSpan(year, interval);
        var href = window.location.href.replace(/time_series/, 'concordance');
        href = href.replace(/date=[^&]*/, 'date=' + year)
        window.location = href;
    });
}

function drawFromData(data, interval, frequency_type) {
    var max_count = 0;
    var width = adjustWidth(data.length);
    var margin = 0;  
    for (var i=0; i < data.length; i++) {
        var count = Math.round(data[i][1]);
        var year = data[i][0];
        var year_to_display = yearToTimeSpan(year, interval);
        // Test if the chart has already been drawn
        if ($('.graph_bar').length < (data.length)) {
            if (i > 0) {
                margin += width + 1;
            }
            var graph_bar = "<span class='graph_bar' data-toggle='tooltip' title='" + count + " occurrences in years '" + year_to_display + "' style='margin-left:" + margin + "px' data-count='" + Math.round(count, false) + "' data-year='" + year + "'></span>";
            $('#test_time_series').append(graph_bar);
            $('.graph_bar').eq(i).width(width + 'px');
            $('.graph_bar').eq(i).data('href', data[i][1]['url']);
            var year = '<span class="graph_years">' + year + '</span>';
            $('.graph_bar').eq(i).append(year);
            var year_width = (width - 25) / 2;
            $('.graph_bar').eq(i).find('.graph_years').css('margin-left', year_width + 'px');
        } else {
            $('.graph_bar').eq(i).data('count', count);
            if (frequency_type == "absolute_time") {
                $('.graph_bar').eq(i).attr('title', Math.round(count, false) + ' occurrences<br>between ' + year_to_display);
            } else {
                $('.graph_bar').eq(i).attr('title', Math.round(count, false) + ' occurrences per 1,000,000 words<br>between ' + year_to_display);
            }  
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
        var num = parseInt($('.graph_years').length / 10);
        $('.graph_years').each(function() {
            count += 1;
            if (count == num) {
                $(this).show();
                count = 0;
            }
        })
    }
    
    var chart_height = $('#test_time_series').height();
    var multiplier = (chart_height - 10) / max_count; 
    var max_height = 0;
    
    var delay_anim = 0
    $('.graph_bar').each(function() {
        var count = $(this).data('count');
        var height = count * multiplier;
        delay_anim += 10;
        if (height > max_height) {
            max_height = height;
        }
        $(this).eq(0).velocity({'height': height + 'px'}, {delay: delay_anim, duration: 200, easing: "easeOutQuad"});
    });
    
    var top_line = (chart_height - 10) / chart_height * 100;
    $("#top_division").css('bottom', top_line + '%');
    
    // Draw three lines along the X axis to help visualize frequencies
    if (frequency_type == "relative_time") {
        $('#side_text').html('Occurrences per 1,000,000 words'); // TODO: move to translation file
        var top_number = Math.round(max_count);
        var middle_number = Math.round(max_count / 3 * 2);
        var bottom_number = Math.round(max_count / 3);
        $('#top_number').html(top_number + ' occurrences per 1,000,000 words');
        $('#middle_number').html(middle_number + ' occurrences per 1,000,000 words');
        $('#first_number').html(bottom_number + ' occurrences per 1,000,000 words');
    } else {
        $('#side_text').html('Total occurrences'); // TODO: move to translation file
        var top_number = Math.round(max_count);
        var middle_number = Math.round(max_count / 3 * 2);
        var bottom_number = Math.round(max_count / 3);
        $('#top_number').html(top_number + ' occurrences');
        $('#middle_number').html(middle_number + ' occurrences');
        $('#first_number').html(bottom_number + ' occurrences');
    }
    clickOnChart(interval);
}

function adjustWidth(elem_num) {
    var container_width = parseInt($('#test_time_series').width());
    var separation_margin = 1 * elem_num;
    var bar_width = (container_width - separation_margin) / elem_num;
    return bar_width;
}