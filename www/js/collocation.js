$(document).ready(function() {
    if (sessionStorage[window.location.href] == null) {
        collocation_cloud();
        var db_url = db_locals['db_url'];
        var colloc_hits = parseInt($('#colloc_hits').html());
        $('#progress_bar').css('width', $('#collocation_table').width() - 5);
        $('#progress_bar').progressbar({max: colloc_hits});
        $('#progress_bar').progressbar({value: 100});
        var percent = 100 / colloc_hits * 100;
        $('.progress-label').text(percent.toString().split('.')[0] + '%');
        update_colloc(db_url, all_colloc, left_colloc, right_colloc, hit_len, 0, 100);
    } else {
        var collocation = JSON.parse(sessionStorage[window.location.href]);
        $('#philologic_collocation').html(collocation);
        $("span[id^='all_'], span[id^='left_'], span[id^='right_']").css('opacity', '');
    }
});

// Set of functions for updating collocation tables
function update_table(sorted_lists) {
    for (column in sorted_lists) {
        var pos = 0;
        var sorted_list = sorted_lists[column];
        for (i in sorted_list) {
            pos += 1;
            var link = "<a href=" + sorted_list[i][1]['url'] + ">" + sorted_list[i][0] + "</a>";
            var count_id = column + '_count_' + sorted_list[i][1]['count'];
            data = link + '<span id="' + count_id + '"> (' + sorted_list[i][1]['count'] + ')</span>';
            $('#' + column + '_num' + pos).html(data);
        }
        $('[id^=' + column+ '_]').hide(function() {$(this).fadeIn(800)});
    }
}

function update_colloc(db_url, all_colloc, left_colloc, right_colloc, results_len, colloc_start, colloc_end) {
    var q_string = window.location.search.substr(1);
    var script = db_url + "/scripts/collocation_fetcher.py?" + q_string
    if (colloc_start == 0) {
        colloc_start = 100;
        colloc_end = 1100;
    } else {
        colloc_start += 1000;
        colloc_end += 1000;
    }
    var script_call = script + '&interval_start=' + colloc_start + '&interval_end=' + colloc_end
    if (colloc_start <= results_len) {
        $.getJSON(script_call, function(data) {
            all_list = merge_results(all_colloc, data[0]);
            var all_sorted = all_list[0];
                all_new_colloc = all_list[1];
            left_list = merge_results(left_colloc, data[1]);
            var left_sorted = left_list[0];
                left_new_colloc = left_list[1];
            right_list = merge_results(right_colloc, data[2]);
            var right_sorted = right_list[0];
                right_new_colloc = right_list[1];
            sorted_lists = {'all': all_sorted, 'left': left_sorted, 'right': right_sorted};
            update_table(sorted_lists);
            update_colloc(db_url, all_new_colloc, left_colloc, right_colloc, results_len, colloc_start, colloc_end);
            collocation_cloud();
            var total = $('#progress_bar').progressbar("option", "max");
            var percent = colloc_end / total * 100;
            if (colloc_end < total) {
                $('#progress_bar').progressbar({value: colloc_end});
                $('.progress-label').text(percent.toString().split('.')[0] + '%');
            }
        });
    }
    else {
        var total = $('#progress_bar').progressbar("option", "max");
        $('#progress_bar').progressbar({value: total});
        $('.progress-label').text('Complete!');
        $("#progress_bar").delay(500).fadeOut('slow');
        if (typeof(localStorage) == 'undefined' ) {
            alert('Your browser does not support HTML5 localStorage. Try upgrading.');
        } else {
            try {
                sessionStorage[window.location.href] = JSON.stringify($('#philologic_collocation').html());
            } catch(e) {
                if (e == QUOTA_EXCEEDED_ERR) {
                    sessionStorage.clear();
                    sessionStorage[window.location.href] = JSON.stringify($('#philologic_collocation').html());
                }
            }
        }
    }
}

// Functions to draw collocation cloud
function collocation_cloud() {
    $.fn.tagcloud.defaults = {
        size: {start: 1.1, end: 3.4, unit: 'em'},
        color: {start: '#F9D69A', end: '#800000'}
      };
    $('#collocate_counts').fadeOut('fast').empty();
    var colloc_counts = {};
    var unordered_list = $('#collocation_table tr');
    unordered_list.each(function() {
    // need this to skip the first row
        if ($(this).find("td:first").length > 0) {
            var word = $(this).find("td:first").find('a').html();
            var href = $(this).find("td:first").find('a').attr('href');
            var count = $(this).find("td:first").find('[id^=all_count]').html();
            count = count.replace('(', '').replace(')', '').replace(' ', '');
            colloc_counts[word] = [];
            colloc_counts[word]['href'] = href;
            colloc_counts[word]['count'] = count;
        }
    });
    function keys(obj) {
        var keys = [];
        for (var key in obj) {
            if(obj.hasOwnProperty(key)) {
                keys.push(key);
            }
        }
        return keys;
    }
    var sorted_list = keys(colloc_counts).sort();
    for (word in sorted_list) {
        word = sorted_list[word];
        var searchlink = '<a href="' + colloc_counts[word]['href'] + '" class="cloud_term" rel="' + colloc_counts[word]['count'] + '"> ';
        var full_link = searchlink + word + ' </a>';
        $("#collocate_counts").append(full_link);
    }
    $("#collocate_counts a").tagcloud();
    $("#collocate_counts").fadeIn('fast');
}