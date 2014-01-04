$(document).ready(function() {
    
    //jQueryUI theming
    $('#time_series_buttons').buttonset();
    
    var mydata = eval($("#absolute_time").data('value'));
    var interval = $("#absolute_time").data('interval');
    var height = $(window).height() - $('#footer').height() - $('#initial_report').height() - $('#header').height() - 200;
    $('#test_time_series').css('height', height);
    $('#absolute_time').click(function() {
        var mydata = eval($(this).data('value'));
        var interval = $("#absolute_time").data('interval');
        drawFromData(mydata, interval, $(this).attr('id'));
    });
    $('#relative_time').click(function() {
        var mydata = eval($(this).data('value'));
        var interval = $("#absolute_time").data('interval');
        drawFromData(mydata, interval, $(this).attr('id'));
    });
    
    
    // Testing
    var body_width = parseInt($('body').width());
    $('#test_time_series, #first_division, #middle_division, #top_division').width(body_width-90 + 'px');
    drawFromData(mydata, interval, 'absolute_time');
    
    
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

function drawFromData(data, interval, frequency_type) {
    var max_count = 0;
    var width = adjustWidth(data.length);
    var margin = 0;
    for (var i=1, l=data.length; i < l; i++) {
        var count = Math.round(data[i][1]);
        // Test if the chart has already been drawn
        if ($('.graph_bar').length < (data.length - 1)) {
            var year = data[i][0];
            if (i > 1) {
                margin += width + 1;
            }
            var graph_bar = "<span class='graph_bar' title='" + count + " occurrences' style='margin-left:" + margin + "px' data-count='" + Math.round(count, false) + "' data-year='" + year + "'></span>";
            $('#test_time_series').append(graph_bar);
            $('.graph_bar').eq(i -1).width(width + 'px');
            var year_margin = margin - 2;
            var year = '<span style="display:none;position:absolute;bottom:0;margin-bottom:-30px;margin-left:' + year_margin + 'px;" class="graph_years">' + year + '</span>';
            $('#test_time_series').append(year);
        } else {
            $('.graph_bar').eq(i -1).data('count', count);
            $('.graph_bar').eq(i -1).attr('title', Math.round(count, false) + ' occurrences');
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
        console.log(num)
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
    clickChart(interval);
    $('.graph_bar').tooltip({ position: { my: "left top+10", at: "left bottom", collision: "flipfit" } }, { track: true });
}

function clickChart(interval) {
    $('.graph_bar').click(function() {
        var year = String($(this).data('year'));
        if (interval == '10') {
            year = year.slice(0,3) + '0';
            var next = String(parseInt(year) + 9);
            year = year + '-' + next
        }
        else if (interval == '100') {
            year = year.slice(0,2) + '00';
            var next = String(parseInt(year) + 99);
            year = year + '-' + next
        }
        var href = window.location.href.replace(/time_series/, 'concordance');
        href = href.replace(/date=[^&]*/, 'date=' + year)
        window.location = href;
    });
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
