google.load("visualization", "1", {packages:["corechart"]});

$(document).ready(function() {
    var mydata = eval($("#relative_time").data('value'));
    var interval = $("#relative_time").data('interval');
    //google.setOnLoadCallback(drawChart(mydata, interval, "Rate per 10000 words"));
    $('#absolute_time').click(function() {
        var mydata = eval($(this).data('value'));
        var interval = $("#absolute_time").data('interval')
        //$("#chart").fadeOut('fast').empty().show();
        //google.setOnLoadCallback(drawChart(mydata,interval, "Count"));
        //$("#chart").hide().fadeIn('fast');
        drawFromData(mydata, interval, $(this).attr('id'));
    });
    $('#relative_time').click(function() {
        //$("#chart").fadeOut('fast').empty().show();
        //google.setOnLoadCallback(drawChart(mydata,interval, "Rate per 10000 words"));
        //$("#chart").hide().fadeIn('fast');
        drawFromData(mydata, interval, $(this).attr('id'));
    });
    
    
    // Testing
    var body_width = parseInt($('body').width());
    $('#test_time_series, #first_division, #middle_division, #top_division').width(body_width-90 + 'px');
    drawFromData(mydata, interval, 'relative_time');
    
    
    var hide_chart = false;
    $(window).resize(function() {
        if (hide_chart === false) {
            $('#test_time_series').fadeOut('fast');
            hide_chart = true;
        }
        waitForFinalEvent(function() {
            var diff = parseInt($('body').width()) - body_width;
            var chart_width = body_width - 90 + diff;
            $('#test_time_series, #first_division, #middle_division, #top_division').width(chart_width + 'px');
            $('.graph_bar, .graph_years').remove();
            $('#test_time_series').show();
            drawFromData(mydata, interval);
            hide_chart = false;
        }, 100, $('#test_time_series').attr('id'));
    });
    
});

function drawChart(mydata, interval, count_type) {
    var data = google.visualization.arrayToDataTable(mydata);
    var chart = new google.visualization.ColumnChart(document.getElementById('chart'));
    var options = {
      hAxis: {title: 'Date', titleTextStyle: {color: 'black'}},
      vAxis: {title: count_type, titleTextStyle: {color: 'black'}}
    }
    
    function selectHandler() {
        var selectedItem = chart.getSelection()[0];
        if (selectedItem) {
            var value = mydata[selectedItem.row+1][0];
            if (interval == '10') {
                value = value.slice(0,3) + '0';
                var next = String(parseInt(value) + 9);
                value = value + '-' + next
            }
            else if (interval == '100') {
                value = value.slice(0,2) + '00';
                var next = String(parseInt(value) + 99);
                value = value + '-' + next
            }
            var href = window.location.href.replace(/time_series/, 'concordance');
            href = href.replace(/date=[^&]*/, 'date=' + value)
            window.location = href;
        }
    }
    
    google.visualization.events.addListener(chart, 'select', selectHandler); 
    chart.draw(data, options);
}

function drawFromData(data, interval, frequency_type) {
    var max_count = 0;
    var width = adjustWidth(data.length);
    var margin = 0;
    for (var i=1, l=data.length; i < l; i++) {
        var count = data[i][1];
        if ($('.graph_bar').length < (data.length - 1)) {
            var year = data[i][0];
            if (i > 1) {
                margin += width + 1;
            }
            var graph_bar = "<span class='graph_bar' title='" + count + " occurrences' style='margin-left:" + margin + "px' data-count='" + formatNumber(count, false) + "' data-year='" + year + "'></span>";
            $('#test_time_series').append(graph_bar);
            $('.graph_bar').eq(i -1).width(width + 'px');
            var year_margin = margin - 3;
            var year = '<span style="position:absolute;bottom:0;margin-bottom:-30px;margin-left:' + year_margin + 'px;" class="graph_years">' + year + '</span>';
            $('#test_time_series').append(year);
        } else {
            $('.graph_bar').eq(i -1).data('count', count);
            $('.graph_bar').eq(i -1).attr('title', formatNumber(count, false) + ' occurrences');
        }
        if (count > max_count) {
            max_count = count;
        }
    }
    
    if (frequency_type == "relative_time") {
        $('#side_text').html('Occurrences per 1,000,000 words');
        var top_number = formatNumber(max_count, false);
        var middle_number = formatNumber(max_count / 3 * 2, false);
        var bottom_number = formatNumber(max_count / 3, false);
    } else {
        $('#side_text').html('Total occurrences');
        var top_number = formatNumber(max_count, true);
        var middle_number = formatNumber(max_count / 3 * 2, true);
        var bottom_number = formatNumber(max_count / 3, true);
    }
    $('#top_number').html(top_number + ' occurrences');
    $('#middle_number').html(middle_number + ' occurrences');
    $('#first_number').html(bottom_number + ' occurrences');
    
    
    multiplier = 590 / max_count; 
    
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

function formatNumber(num, truncate) {
    if (truncate) {
        num = String(num).replace(/(\d+).*/, '$1');
    } else {
        num = String(num).replace(/(\d+\..{0,3}).*/, '$1');
    }
    return num;  
}
