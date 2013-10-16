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
    $("#reset_form, #reset_form1, #freq_sidebar, #show_table_of_contents, #hide_search_form, #more_options, .more_context, .close_concordance").button();
    $('#hide_frequency').button();
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
    ////////////////////////////////////////////////////////////////////////////
    
    
    
    ////////////////////////////////////////////////////////////////////////////
    ///////// Frequency / Frequency per 10,000 switcher ////////////////////////
    ////////////////////////////////////////////////////////////////////////////
    if ($('#philologic_frequency_report').length) {
        frequency_switcher(db_url);
    }
    ////////////////////////////////////////////////////////////////////////////

    display_options_on_selected();
    
});


////////////////////////////////////////////////////////////////////////////////
//////////// FUNCTIONS /////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////


// Switch between absolute frequency and frequency per 10,000 words
function frequency_switch(db_url) {
    $('#frequency_report_switch').on("change", function(){
        var switchto = $('input[name=freq_switch]:checked').val();
        var width = $(window).width() / 3;
        $("#waiting").css("margin-left", width).show();
        $("#waiting").css("margin-top", 200).show();
        $.get(db_url + "/scripts/frequency_switcher.py" + switchto, function(data) {
            $("#results_container").hide().html(data).fadeIn('fast');
            $("#waiting").hide();
        });
    });
}

///////////////////////////////////////////////////
////// Functions shared by various reports ////////
///////////////////////////////////////////////////

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
    $('.philologic_concordance, .kwic_concordance, .page_text, .obj_text').mouseup(function(e) {
        $('.highlight_options').remove();
        var text = getSelectedText();
        if (text != '') {
            var options = $('<div class="highlight_options">');
            var my_table = '<table class="context_table" BORDER=1 RULES=ALL frame=void>';
            my_table += '<tr><td class="selected_word">"' + text.charAt(0).toUpperCase() + text.slice(1) + '"</td></tr>';
            var search_reports = ['concordance', 'collocation', 'relevance']
            my_table += '<tr><td>';
            if (text.split(' ').length == 1) {
                for (report in search_reports) {
                    report = search_reports[report];
                    var url = "?report=" + report + "&method=proxy&q=" + text;
                    if (report != 'relevance') {
                        var report_link = '<a href="' + url + '" target="_blank" class="selected_tag">Run a ' + report + ' search for this selection</a><br>';
                    } else {
                        var report_link = '<a href="' + url + '" target="_blank" class="selected_tag">Run a ranked relevance search for this selection</a><br>';
                    }
                    my_table += report_link;
                }
                var url = "?q=&report=concordance&method=proxy&head=" + text;
                var report_link = '<a href="' + url + '" target="_blank" class="selected_tag">Run a headword search for this selection</a><br>';
                my_table += report_link;
            } else {
                var url = "?report=relevance&method=proxy&q=" + text;
                var report_link = '<a href="' + url + '" target="_blank" class="selected_tag">Run a ranked relevance search for this selection</a><br>';
                my_table += report_link;
                url = "?q=&report=concordance&method=proxy&head=" + text;
                report_link = '<a href="' + url + '" target="_blank" class="selected_tag">Run a headword search for this selection</a><br>';
                my_table += report_link;
            }
            if (text.split(' ').length == 1) {
                var url = "?report=time_series&method=proxy&q=" + text;
                var report_link = '<a href="' + url + '" target="_blank" class="selected_tag">Run a time series search for this selection</a><br>';
                var definition = '<a href=" http://artflsrv02.uchicago.edu/cgi-bin/dicos/quickdict.pl?docyear=1700-1799&strippedhw=' + text + '" target="_blank" class="selected_tag">Get a definition of this word</a>';
                my_table += "</tr></td><tr><td class='definition'>";
                my_table += definition;
            }
            my_table += "</td></tr>";
            options.append(my_table);
            var top_coord = e.pageY + 10;
            var left_coord = e.pageX + 10;
            var parent_left_coord = $(this).offset().left + $(this).width();
            $("body").append(options);
            var width = options.width();
            options.offset({ top: top_coord, left: left_coord});
            var options_left_coord = left_coord + options.width();
            if (options_left_coord > parent_left_coord) {
                options.css('position', '').css('float', 'right').css('margin-right', '20px');
                options.css('left', parent_left_coord - width)
            } 
            options.fadeIn('fast');
        }
    });
}

function getSelectedText() {
    if (window.getSelection) {
        return window.getSelection().toString();
    } else if (document.selection) {
        return document.selection.createRange().text;
    }
    return '';
}


// For concordances and concordances from collocations
function closeConcordance() {
    $(".close_concordance").click(function() {
        console.log('hi')
        var $conc = $(this).parents('.philologic_occurrence ');
        $conc.animate({
            left: parseInt($conc.css('left'),10) == 0 ?
                -$conc.outerWidth() :
                0
        }, function() {
            $(this).animate({height: "hide"}, 200, "easeInQuad");
        });
    });
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
    $("#toggle_frequency").click(function() {
        toggle_frequency(q_string, db_url, pathname);
    });
    $("#frequency_field").change(function() {
        toggle_frequency(q_string, db_url, pathname);
    });
    $("#hide_frequency").click(function() {
        hide_frequency();
    });
}
function toggle_frequency(q_string, db_url, pathname) {
    var field =  $("#frequency_field").val();
    if (field != 'collocate') {
        var script_call = db_url + "/scripts/get_frequency.py?" + q_string + "&frequency_field=" + field;
    } else {
        var script_call = db_url + "/scripts/get_collocate.py?" + q_string
    }
    $(".loading").empty().hide();
    var spinner = '<img src="' + db_url + '/js/ajax-loader.gif" alt="Loading..."  height="25px" width="25px"/>';
    $("#results_container").animate({
        "margin-right": "410px"},
        150, function() {
                getCitationWidth();
            }
    );
    var width = $(".sidebar_display").width() / 2;
    $(".loading").append(spinner).css("margin-left", width).css("margin-top", "10px").show();
    $.getJSON(script_call, function(data) {
        var newlist = "";
        $(".loading").hide().empty();
        if (field == "collocate") {
            newlist += "<p class='freq_sidebar_status'>Collocates within 10 words left or right</p>";
        }
        $.each(data, function(index, item) {
            var url = '<a class="freq_sidebar_text" href="' + item[2] + '">' + item[0] + '</a>';
            newlist += '<li style="white-space:nowrap;">';
            newlist += '<span class="ui-icon ui-icon-bullet" style="display: inline-block;vertical-align:10px;"></span>';
            newlist += url + '<span style="float:right;display:inline-block;padding-right: 5px;">' + item[1] + '</span></li>';
        });
        $("#freq").hide().empty().html(newlist).fadeIn('fast');
    });
    $("#hide_frequency").show();
    $(".frequency_container").show();
    $("#hide_frequency").click(function() {
        hide_frequency();
    });
    sidebar_reports(q_string, db_url, pathname);
}
function hide_frequency() {
    $("#hide_frequency").hide();
    $("#freq").empty().hide();
    $('.frequency_container').hide();
    $(".loading").empty();
    $(".results_container").animate({
        "margin-right": "0px"},
        150, function() {
                getCitationWidth();
        }
    );
}