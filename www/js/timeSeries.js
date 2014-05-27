$(document).ready(function() {
    
    var db_url = webConfig['db_url'];
    
    //jQueryUI theming
    $('#time_series_buttons').buttonset();
    
    if (sessionStorage[window.location.href] == null) {
        // Make relative frequency unclickable until full results are in
        $("label[for='relative_time']").css({'pointer-events': "none", "color": "#D8D8D8"});
        
        // Calculate width and height of chart
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
        var interval = $("#absolute_time").data('interval');
        drawFromData(sorted_abs, interval, 'absolute_time');
        var total = parseInt($('#progress_bar').data('total'));
        $('#progress_bar').progressbar({max: total});
        $('#progress_bar').progressbar({value: 5000});
        var percent = 5000 / total * 100;
        $('.progress-label').text(percent.toString().split('.')[0] + '%');
        $('#progress_bar').width($('#initial_report').width());
        $('#progressive_bar').show();
        var date_counts = eval($('#relative_time').data('datecount'));
        progressiveLoad(db_url, total, interval, 0, 5000, full_abs, date_counts);   
    } else {
        var time_series = JSON.parse(sessionStorage[window.location.href]);
        $('#philologic_response').html(time_series);
        frequencySwitcher();
    }
    
    $(window).resize(function() {
        waitForFinalEvent(function() {
            var diff = parseInt($('body').width()) - body_width;
            var chart_width = body_width - 90 + diff;
            $('#test_time_series, #first_division, #middle_division, #top_division').width(chart_width + 'px');
            $('.graph_bar').remove();
            var height = $(window).height() - $('#footer').height() - $('#initial_report').height() - $('#header').height() - 200;
            $('#test_time_series').css('height', height);
            $('#test_time_series').fadeOut('fast', function() {
                $(this).show();
                var frequency = $('input[name="freq_type"]:checked').attr('id');
                data = eval($('#' + frequency).data('value'));
                drawFromData(data, interval);
            });
        }, 500, $('#test_time_series').attr('id'));
    });
    
});


function frequencySwitcher() {
    $('#absolute_time, #relative_time').click(function() {
        var abs_data = eval($(this).data('value'));
        var interval = $(this).data('interval');
        drawFromData(abs_data, interval, $(this).attr('id'));
    });
}

function progressiveLoad(db_url, total_results, interval, interval_start, interval_end, abs_full_results, full_date_counts) {
    var q_string = window.location.search.substr(1);
    var script = db_url + "/scripts/time_series_fetcher.py?" + q_string
    if (interval_start === 0) {
        interval_start = 10000;
        interval_end = 30000;
    } else {
        interval_start += 20000;
        interval_end += 20000;
    }
    if (interval_start < total_results) {
        script_call = script + "&interval_start=" + interval_start + "&interval_end=" + interval_end;
        $.getJSON(script_call, function(data) {
            var abs_merge = merge_time_results(abs_full_results, data[0]);
            abs_sorted_list = abs_merge[0];
            abs_new_full_results = abs_merge[1];            
            $('.graph_years').remove();
            $('.graph_bar').remove();
            drawFromData(abs_sorted_list, interval, "absolute_time");
            
            // Update date_counts
            for (date in data[1]) {
                full_date_counts[date] = data[1][date]
            }
            
            progressiveLoad(db_url, total_results, interval, interval_start, interval_end, abs_new_full_results, full_date_counts);
            var total = $('#progress_bar').progressbar("option", "max");
            var percent = interval_end / total * 100;
            if (interval_end < total) {
                var progress_width = $('#progress_bar').width() * percent / 100;
                $('#progress_bar .ui-progressbar-value').animate({width: progress_width}, 'slow', 'easeOutQuart', {queue: false});
                $('.progress-label').text(percent.toString().split('.')[0] + '%');
            }
        });
    } else {
        // Store final sorted results
        abs_results = sortResults(abs_full_results)
        $('#absolute_time').data('value', JSON.stringify(abs_results));
        
        // Generate relative frequencies from absolute frequencies and make button clickable again
        $("label[for='relative_time']").animate({"color": "#555"}).css('pointer-events', "auto");
        relative_results = relativeCount(abs_results, full_date_counts);
        $('#relative_time').data('value', JSON.stringify(relative_results))
        
        // Create click event handler to switch between frequency types
        frequencySwitcher();
        
        var total = $('#progress_bar').progressbar("option", "max");
        $('#progress_bar').progressbar({value: total});
        $('.progress-label').text('Complete!');
        $("#progress_bar").delay(500).slideUp();
    }
}

function saveTimeSeries() {
    if (typeof(localStorage) == 'undefined' ) {
        alert('Your browser does not support HTML5 localStorage. Try upgrading.');
    } else {
        try {
            sessionStorage[window.location.href] = JSON.stringify($('#philologic_response').html());
        } catch(e) {
            if (e == QUOTA_EXCEEDED_ERR) {
                sessionStorage.clear();
                sessionStorage[window.location.href] = JSON.stringify($('#philologic_response').html());
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

// Taken from common.js. Differs in that it sorts by date and not count
function merge_time_results(full_results, new_data) {
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
    var sorted_list = sortResults(full_results);
    return [sorted_list, full_results]
}

function sortResults(full_results) {
    var sorted_list = [];
    for (key in full_results) {
        sorted_list.push([key, full_results[key]]);
    }
    sorted_list.sort(function(a,b) {return a[0] - b[0]});
    return sorted_list
}

function clickOnChart(interval) {
    $('.graph_bar').click(function() {
        var year = String($(this).data('year'));
        if (interval == '10') {
            year = year.slice(0,-1) + '0';
            var next = String(parseInt(year) + 9);
            year = year + '-' + next
        }
        else if (interval == '100') {
            year = year.slice(0,-2) + '00';
            var next = String(parseInt(year) + 99);
            year = year + '-' + next
        } else if (interval == '50') {
            var decade = parseInt(year.slice(-2));
            if (decade < 50) {
                year = year.slice(0,-2) + '00' + '-' + year.slice(0,-2) + '49';
            } else {
                year = year.slice(0,-2) + '50' + '-' + year.slice(0,-2) + '99';
            }
        }
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
        // Test if the chart has already been drawn
        if ($('.graph_bar').length < (data.length)) {
            var year = data[i][0];
            if (i > 0) {
                margin += width + 1;
            }
            var graph_bar = "<span class='graph_bar' title='" + count + " occurrences' style='margin-left:" + margin + "px' data-count='" + Math.round(count, false) + "' data-year='" + year + "'></span>";
            $('#test_time_series').append(graph_bar);
            $('.graph_bar').eq(i).width(width + 'px');
            $('.graph_bar').eq(i).data('href', data[i][1]['url']);
            var year = '<span class="graph_years">' + year + '</span>';
            $('.graph_bar').eq(i).append(year);
            var year_width = (width - 30) / 2;
            $('.graph_bar').eq(i).find('.graph_years').css('margin-left', year_width + 'px');
        } else {
            $('.graph_bar').eq(i).data('count', count);
            if (frequency_type == "absolute_time") {
                $('.graph_bar').eq(i).attr('title', Math.round(count, false) + ' occurrences');
            } else {
                $('.graph_bar').eq(i).attr('title', Math.round(count, false) + ' occurrences per 1,000,000 words')
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
    
    multiplier = ($('#test_time_series').height() - 10) / max_count; 
    
    $('.graph_bar').each(function() {
        var count = $(this).data('count');
        var height = count * multiplier;
        $(this).attr('data-height', height)
        $(this).eq(0).css('height', height + 'px');
    });
    $('.graph_bar').tooltip({ position: { my: "left top+10", at: "left bottom", collision: "flipfit" } }, { track: true });
    clickOnChart(interval);
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
