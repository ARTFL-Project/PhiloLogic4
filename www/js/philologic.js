$(document).ready(function() {
    
    ////////////////////////////////////////////////////////////////////////////
    // Important variables /////////////////////////////////////////////////////
    ////////////////////////////////////////////////////////////////////////////
    var pathname = window.location.pathname.replace('dispatcher.py/', '');
    var db_url = db_locals['db_url'];
    var q_string = window.location.search.substr(1);
    ////////////////////////////////////////////////////////////////////////////
    
    ////////////////////////////////////////////////////////////////////////////
    //  jQueryUI theming ///////////////////////////////////////////////////////
    ////////////////////////////////////////////////////////////////////////////
    $( "#button, #button1" )
        .button()
        .click(function( event ) {
            hide_search_form();
            var width = $(window).width() / 3;
            $("#waiting").css("margin-left", width).css('margin-top', 100).show();
        });
    $("#reset_form, #reset_form1, #freq_sidebar, #show_table_of_contents, #hide_search_form, #more_options, .more_context").button();
    $('#button2').button();
    $('#hide_sidebar').button();
    $("#page_num, #field, #method, #year_interval, #time_series_buttons, #report_switch, #frequency_report_switch").buttonset();
    $("#word_num").spinner({
        spin: function(event, ui) {
                if ( ui.value > 20 ) {
                    $(this).spinner( "value", 1 );
                    return false;
                } else if ( ui.value < 1 ) {
                    $(this).spinner( "value", 20 );
                    return false;
                }
            }
    });
    $("#word_num").val(10);
    $('.ui-spinner').css('width', '45px')
    $(':text').addClass("ui-corner-all");
    $("#show_search_form").tooltip({ position: { my: "left+10 center", at: "right" } });
    $(".tooltip_link").tooltip({ position: { my: "left top+5", at: "left bottom", collision: "flipfit" } }, { track: true });
    $('#search_explain').accordion({
        collapsible: true,
        heightStyle: "content",
        active: false
    });
    $('#page_links').find('a').each(function(){$(this).button()});
    ////////////////////////////////////////////////////////////////////////////
    
    //display_options_on_selected();
    
    /// Make sure search form doesn't cover footer
    var form_offset = $('#form_body').offset().top + $('#form_body').height();
    searchFormOverlap(form_offset);
    $(window).resize(function() {
        searchFormOverlap(form_offset);
    });
    
    // Initialize progress bar for sidebar
    var total_results = parseInt($('#total_results').text());
    $('#progress_bar').progressbar({max: total_results});
    $('#progress_bar').progressbar({value: 100});
    var percent = 100 / total_results * 100;
    $('.progress-label').text(percent.toString().split('.')[0] + '%');
    
});


///////////////////////////////////////////////////
////// Functions shared by various reports ////////
///////////////////////////////////////////////////


function searchFormOverlap(form_offset) {
    var footer_offset = $('#footer').offset().top;
    if (form_offset > footer_offset) {
        $('#footer').css('top', form_offset + 20);
    } else {
        $('#footer').css('top', 'auto');
    }
}

// Show more context in concordance and concordance from collocation searches
function more_context() {
    $(".more_context").click(function() {
        var context_link = $(this).text();
        if (context_link == 'More') {
            $(this).parents().siblings('.philologic_context').children('.begin_concordance').show();
            $(this).parents().siblings('.philologic_context').children('.end_concordance').show();
            $(this).find('.ui-button-text').empty().fadeIn(100).append('Less');
        } 
        else {
            $(this).parents().siblings('.philologic_context').children('.begin_concordance').hide();
            $(this).parents().siblings('.philologic_context').children('.end_concordance').hide();
            $(this).find('.ui-button-text').empty().fadeIn(100).append('More');
        }
    });
}



/// Contextual menu when selecting a word in the text /////
function display_options_on_selected() {
    // TODO reword this in a sane way
    
    
    //$('.philologic_context, #kwic_concordance, #obj_text').mouseup(function(e) {
    //    $('.highlight_options').remove();
    //    var text = getSelectedText();
    //    if (text != '') {
    //        var options = $('<div class="highlight_options">');
    //        var my_table = '<table class="context_table" BORDER=1 RULES=ALL frame=void>';
    //        my_table += '<tr><td class="selected_word">"' + text.charAt(0).toUpperCase() + text.slice(1) + '"</td></tr>';
    //        var search_reports = ['concordance', 'collocation', 'relevance']
    //        my_table += '<tr><td>';
    //        if (text.split(' ').length == 1) {
    //            for (report in search_reports) {
    //                report = search_reports[report];
    //                var url = "?report=" + report + "&method=proxy&q=" + text;
    //                if (report != 'relevance') {
    //                    var report_link = '<a href="' + url + '" target="_blank" class="selected_tag">Run a ' + report + ' search for this selection</a><br>';
    //                } else {
    //                    var report_link = '<a href="' + url + '" target="_blank" class="selected_tag">Run a ranked relevance search for this selection</a><br>';
    //                }
    //                my_table += report_link;
    //            }
    //            var url = "?q=&report=concordance&method=proxy&head=" + text;
    //            var report_link = '<a href="' + url + '" target="_blank" class="selected_tag">Run a headword search for this selection</a><br>';
    //            my_table += report_link;
    //        } else {
    //            var url = "?report=relevance&method=proxy&q=" + text;
    //            var report_link = '<a href="' + url + '" target="_blank" class="selected_tag">Run a ranked relevance search for this selection</a><br>';
    //            my_table += report_link;
    //            url = "?q=&report=concordance&method=proxy&head=" + text;
    //            report_link = '<a href="' + url + '" target="_blank" class="selected_tag">Run a headword search for this selection</a><br>';
    //            my_table += report_link;
    //        }
    //        if (text.split(' ').length == 1) {
    //            var url = "?report=time_series&method=proxy&q=" + text;
    //            var report_link = '<a href="' + url + '" target="_blank" class="selected_tag">Run a time series search for this selection</a><br>';
    //            var definition = '<a href=" http://artflsrv02.uchicago.edu/cgi-bin/dicos/quickdict.pl?docyear=1700-1799&strippedhw=' + text + '" target="_blank" class="selected_tag">Get a definition of this word</a>';
    //            my_table += "</tr></td><tr><td class='definition'>";
    //            my_table += definition;
    //        }
    //        my_table += "</td></tr>";
    //        options.append(my_table);
    //        var top_coord = e.pageY + 10;
    //        var left_coord = e.pageX + 10;
    //        var parent_left_coord = $(this).offset().left + $(this).width();
    //        $("body").append(options);
    //        var width = options.width();
    //        options.offset({ top: top_coord, left: left_coord});
    //        var options_left_coord = left_coord + options.width();
    //        if (options_left_coord > parent_left_coord) {
    //            options.css('position', '').css('float', 'right').css('margin-right', '20px');
    //            options.css('left', parent_left_coord - width)
    //        } 
    //        options.fadeIn('fast');
    //    }
    //});
}

function getSelectedText() {
    if (window.getSelection) {
        return window.getSelection().toString();
    } else if (document.selection) {
        return document.selection.createRange().text;
    }
    return '';
}

function getCitationWidth() {
    var citation_width = $('.citation').width() - $('.more_context_and_close').width() - $('.hit_n').width() - 30;
    $('.cite').width(citation_width);
}


// Delay function calls in repeated actions
var waitForFinalEvent = (function () {
  var timers = {};
  return function (callback, ms, uniqueId) {
    if (!uniqueId) {
      uniqueId = "Don't call this twice without a uniqueId";
    }
    if (timers[uniqueId]) {
      clearTimeout (timers[uniqueId]);
    }
    timers[uniqueId] = setTimeout(callback, ms);
  };
})();

//    These functions are for the sidebar frequencies
function sidebar_reports(q_string, db_url, pathname) {
    $("#frequency_by").button().click(function(e) {
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
function merge_results(full_results, new_data) {
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