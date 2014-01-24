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
        var q_string = window.location.search.substr(1);
        clickOnColloc(db_url, q_string);
    }
});

// Set of functions for updating collocation tables
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
function update_table(sorted_lists, q_string, db_url) {
    for (column in sorted_lists) {
        var pos = 0;
        var sorted_list = sorted_lists[column];
        for (i in sorted_list.slice(0, 50)) {
            pos += 1;
            var word = '<span id="' + column + '_word_' + pos + '" data-word="' + sorted_list[i][0] + '" data-direction=' + column + '" data-count="' + sorted_list[i][1] + '">' + sorted_list[i][0] + '</span>';
            var count_id = column + '_count_' + sorted_list[i][1];
            data = word + '<span id="' + count_id + '">&nbsp(' + sorted_list[i][1] + ')</span>';
            $('#' + column + '_num' + pos).html(data);
        }
        $('[id^=' + column+ '_]').hide(function() {$(this).fadeIn(800)});
    }
}

function update_colloc(db_url, all_colloc, left_colloc, right_colloc, results_len, colloc_start, colloc_end) {
    var q_string = window.location.search.substr(1);
    var script = db_url + "/scripts/collocation_fetcher.py?" + q_string
    if (colloc_start == 0) {
        colloc_start = 3000;
        colloc_end = 18000;
    } else {
        colloc_start += 15000;
        colloc_end += 15000;
    }
    var script_call = script + '&interval_start=' + colloc_start + '&interval_end=' + colloc_end
    if (colloc_start <= results_len) {
        $.getJSON(script_call, function(data) {
            all_list = mergeCollocResults(all_colloc, data[0]);
            var all_sorted = all_list[0];
                all_new_colloc = all_list[1];
            left_list = mergeCollocResults(left_colloc, data[1]);
            var left_sorted = left_list[0];
                left_new_colloc = left_list[1];
            right_list = mergeCollocResults(right_colloc, data[2]);
            var right_sorted = right_list[0];
                right_new_colloc = right_list[1];
            sorted_lists = {'all': all_sorted, 'left': left_sorted, 'right': right_sorted};
            update_table(sorted_lists, q_string, db_url);
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
        
        // Active links on collocations
        $('span[id^=all_word], span[id^=left_word], span[id^=right_word]').addClass('colloc_link');
        clickOnColloc(db_url, q_string);
        
        // Make sure all animations and CSS transformations are complete
        setTimeout(saveCollocations, 3000);
    }
}

function saveCollocations(args) {
    if (typeof(localStorage) == 'undefined' ) {
        alert('Your browser does not support HTML5 localStorage. Try upgrading.');
    } else {
        try {
            sessionStorage[window.location.href] = JSON.stringify($('#philologic_collocation').html());
        } catch(e) {
            sessionStorage.clear();
            console.log("sessionStorage was full, clearing it for space...");
            sessionStorage[window.location.href] = JSON.stringify($('#philologic_collocation').html());
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
            var word = $(this).find("td:first").find('[id^=all_word]').html();
            var count = $(this).find("td:first").find('[id^=all_count]').html();
            count = count.replace('(', '').replace(')', '').replace(' ', '');
            colloc_counts[word] = [];
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
        var searchlink = '<a class="cloud_term" rel="' + colloc_counts[word]['count'] + '" data-word="' + word + '" data-direction="' + colloc_counts[word]['count'] + '" data-count="' + colloc_counts[word]['count'] + '">';
        var full_link = searchlink + word + ' </a>';
        $("#collocate_counts").append(full_link);
    }
    $("#collocate_counts a").tagcloud();
    $("#collocate_counts").fadeIn('fast');
}

function clickOnColloc(db_url, q_string) {
    $('.colloc_link, .cloud_term').click(function() {
        var word = $(this).data('word');
        var direction = $(this).data('direction');
        var count = $(this).data('count');
        q_string = q_string.replace(/report=[^&]+/, 'report=concordance_from_collocation');
        q_string += '&collocate=' + encodeURIComponent(word);
        q_string += '&direction=' + direction;
        q_string += '&collocate_num=' + count;
        var url = db_url + '/dispatcher.py/?' + q_string;
        window.location = url;
    });
}