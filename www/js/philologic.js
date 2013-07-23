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
    $("#reset_form, #freq_sidebar, #show_table_of_contents, #overlay_toggler, #hide_search_form, .more_options").button();
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
    $(".show_search_form").tooltip({ position: { my: "left+10 center", at: "right" } });
    $(".tooltip_link").tooltip({ position: { my: "left top+5", at: "left bottom", collision: "flipfit" } }, { track: true });
    $('.search_explain').accordion({
        collapsible: true,
        heightStyle: "content",
        active: false
    });
    ////////////////////////////////////////////////////////////////////////////
    
    
    ////////////////////////////////////////////////////////////////////////////
    // Search form related events //////////////////////////////////////////////
    ////////////////////////////////////////////////////////////////////////////
    for (i in db_locals['search_reports']) {
        search_report = '#' + db_locals['search_reports'][i] + '_button';
        $(search_report).show();
    }
    $("#q").focus(function() {
        if ($(".philologic_response").is('*')) {
            show_more_options("report");
            hide_search_on_click();
        }
    });
    $('.more_options').click(function() {
        $('.search_elements').css('z-index', 150);
        $('.book_page').css('z-index', 90);
        if ($(".more_options").text() == "Show search options") {
            show_more_options("all");
            $('.search_explain').slideDown();
            hide_search_on_click();
        } else {
            hide_search_form();
        }
    });
    $("#report").buttonset();
    $('.form_body').show();
    $("#search_elements").hide();
    $('.conc_question, .freq_question, .colloc_question, .time_question, .relev_question, .kwic_question').hide();
    $('.search_explain').hide();
    showHide($('input[name=report]:checked', '#search').val());
    $('#report').click(function() {
        var report = $('input[name=report]:checked', '#search').val();
        if ($("#search_elements:visible")) {
            showHide(report);
            $("#search_elements").slideDown();
            $('.search_explain').slideDown();
        } else {
            showHide(report);
            $("#search_elements").fadeIn();
            $('.search_explain').fadeIn();
        }
    });
    
    //monkeyPatchAutocomplete();    
    $("#q").autocomplete({
        source: db_url + "/scripts/term_list.py",
        minLength: 2,
        "dataType": "json",
        focus: function( event, ui ) {
            q = ui.item.label.replace(/<\/?span[^>]*?>/g, '');
            $("#q").val(q);
            return false;
        },
        select: function( event, ui ) {
            q = ui.item.label.replace(/<\/?span[^>]*?>/g, '');
            $("#q").val(q);
            return false;
        }
    }).data("ui-autocomplete")._renderItem = function (ul, item) {
         return $("<li></li>")
             .data("item.autocomplete", item)
             .append("<a>" + item.label + "</a>")
             .appendTo(ul);
     };
    var fields = [];
    $('#metadata_fields input').each(function(){
        fields.push($(this).attr('name'));
    });
    for (i in fields) {
        var  metadata = $("#" + fields[i]).val();
        var field = fields[i];
        autocomplete_metadata(metadata, field, db_url)
    }
    
    //  This will prefill the search form with the current query
    var val_list = q_string.split('&');
    for (var i = 0; i < val_list.length; i++) {
        var key_value = val_list[i].split('=');
        var value = decodeURIComponent((key_value[1]+'').replace(/\+/g, '%20'));
        var key = key_value[0]
        if (value) {
            if (key == 'report') {
                $('input[name=' + key + '][value=' + value + ']').attr("checked", true);
                $("#report").buttonset("refresh");
            }
            else if (key == 'pagenum' || key == 'method' || key == 'year_interval') {
                $('input[name=' + key + '][value=' + value + ']').attr("checked", true);
                $('input[name=' + key + '][value=' + value + ']').button('refresh');
            }
            else if (key == 'field') {
                $('select[name=' + key + ']').val(value);
            }
            else {
                $('#' + key).val(value);
            }
        }
    }
    
    //  Clear search form
    $("#reset_form").click(function() {
        $("#method").find("input:radio").attr("checked", false).end();
        $("#method1").attr('checked', true);
        $("#method").buttonset('refresh');
        $("#report").find("input:radio").attr("checked", false).end();
        $("#report1").attr('checked', true);
        $("#report").buttonset('refresh');
        $("#page_num").find("input:radio").attr("checked", false).end();
        $("#pagenum1").attr('checked', true);
        $("#page_num").buttonset('refresh');
        $('#search')[0].reset();
        showHide('concordance');
        $("#search_elements").fadeIn();
    });
    
    //  This is to select the right option when clicking on the input box  
    $("#arg_proxy").focus(function() {
        $("#arg_phrase").val('');
        $("#method1").attr('checked', true).button("refresh");
    });
    $("#arg_phrase").focus(function() {
        $("#arg_proxy").val('');
        $("#method2").attr('checked', true).button("refresh");
    });
    ////////////////////////////////////////////////////////////////////////////

    
    ////////////////////////////////////////////////////////////////////////////
    ///////// Frequency / Frequency per 10,000 switcher ////////////////////////
    ////////////////////////////////////////////////////////////////////////////
    if ($('.philologic_frequency_report').length) {
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

function autocomplete_metadata(metadata, field, db_url) {
    $("#" + field).autocomplete({
        source: db_url + "/scripts/metadata_list.py?field=" + field,
        minLength: 2,
        dataType: "json",
        focus: function( event, ui ) {
            q = ui.item.label.replace(/<\/?span[^>]*?>/g, '');
            $("#" + field).val(q);
            return false;
        },
        select: function( event, ui ) {
            q = ui.item.label.replace(/<\/?span[^>]*?>/g, '');
            $("#" + field).val(q);
            return false;
        }
    }).data("ui-autocomplete")._renderItem = function (ul, item) {
         return $("<li></li>")
             .data("item.autocomplete", item)
             .append("<a>" + item.label + "</a>")
             .appendTo(ul);
     };
}

// Display different search parameters based on the type of report used
function showHide(value) {
    $("#results_per_page, #collocation_num, #time_series_num, #year_interval,#frequency_num, #method, #metadata_fields").hide();
    $('.explain_relev, .explain_conc, .explain_time, .explain_colloc, .explain_kwic, explain_freq').hide();
    $('.relev_question, .conc_question, .colloc_question, .time_question, .kwic_question, explain_freq').hide();    

    if (value == 'frequency') {
        $("#frequency_num, #method, #metadata_fields").show();
        $('.freq_question').fadeIn();
    }
    if (value == 'collocation') {
        $("#collocation_num, #method, #metadata_fields").show();
        $('.colloc_question').fadeIn();
    }
    if (value == 'kwic') {
        $("#results_per_page, #method, #metadata_fields").show();
        $('.kwic_question').fadeIn();
    }
    if (value == 'concordance') {
        $("#results_per_page, #method, #metadata_fields").show();
        $('.conc_question').fadeIn();
    }
    if (value == 'relevance') {
        $("#results_per_page").show();
        $('.relev_question').fadeIn();
    }
    if (value == "time_series") {
        $("#time_series_num, #year_interval").show();
        $('.time_question').fadeIn();
    }
}

//  Function to show or hide search options
function show_more_options(display) {
    $(".more_options").button('option', 'label', 'Hide search options');    
    $("#report").slideDown('fast');
    if (display == "all") {
        var report = $('input[name=report]:checked', '#search').val();
        showHide(report);
        $("#search_elements").slideDown();
    }
    $('.form_body').css('z-index', 99);
    $("body").append("<div id='search_overlay' style='display:none;'></div>");
    var header_height = $('#header').height();
    var footer_height = $('#footer').height();
    var overlay_height = $(document).height() - header_height - footer_height;
    $("#search_overlay")
    .height(overlay_height)
    .css({
       'opacity' : 0.2,
       'position': 'absolute',
       'top': 0,
       'left': 0,
       'background-color': 'lightGrey',
       'width': '100%',
       'margin-top': header_height,
       'z-index': 90
     });
    $("#search_overlay").fadeIn('fast');
}
function hide_search_form() {
    $("#report").slideUp();
    $('.search_explain').accordion({
        collapsible: true,
        heightStyle: "content",
        active: false
    });
    $("#search_elements").slideUp();
    $("#search_overlay").fadeOut('fast', function() {
        $(this).remove();
    });
    $(".more_options").button('option', 'label', 'Show search options');
    $('.search_explain').slideUp();
}
function hide_search_on_click() {
    $("#search_overlay, #header, #footer").click(function() {
        hide_search_form();
    }); 
}


///////////////////////////////////////////////////
////// Functions shared by various reports ////////
///////////////////////////////////////////////////

// Show more context in concordance and concordance from collocation searches
function more_context() {
    $(".more_context").click(function(e) {
        var context_link = $(this).text();
        if (context_link == 'More') {
            $(this).siblings('.philologic_context').children('.begin_concordance').show();
            $(this).siblings('.philologic_context').children('.end_concordance').show();
            $(this).empty().fadeIn(100).append('Less');
        } 
        else {
            $(this).siblings('.philologic_context').children('.begin_concordance').hide();
            $(this).siblings('.philologic_context').children('.end_concordance').hide();
            $(this).empty().fadeIn(100).append('More');
        }
        e.preventDefault();
    });
}

//    These functions are for the sidebar frequencies
function sidebar_reports(q_string, db_url, pathname) {
    $("#toggle_frequency").click(function() {
        toggle_frequency(q_string, db_url, pathname);
    });
    $("#frequency_field").change(function() {
        toggle_frequency(q_string, db_url, pathname);
    });
    $(".hide_frequency").click(function() {
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
    $(".results_container").animate({
        "margin-right": "420px"},
        150);
    var width = $(".sidebar_display").width() / 2;
    $(".loading").append(spinner).css("margin-left", width).css("margin-top", "10px").show();
    $.getJSON(script_call, function(data) {
        var newlist = "";
        $(".loading").hide().empty();
        if (field == "collocate") {
            newlist += "<p class='freq_sidebar_status'>Collocates within 10 words left or right</p>";
        }
        $.each(data, function(index, item) {
            if (item[0].length > 30) {
                var url = '<a href="' + item[2] + '">' + item[0].slice(0,32) + '[...]</a>'
            } else {
                var url = '<a href="' + item[2] + '">' + item[0] + '</a>'
            } 
            newlist += '<p><li>' + url + '<span style="float:right;">' + item[1] + '</span></li></p>';
        });
        $("#freq").hide().empty().html(newlist).fadeIn('fast');
    });
    $(".hide_frequency").show();
    $(".frequency_container").show();
    // Workaround padding weirdness in Firefox and Internet Explorer
    if (/Firefox[\/\s](\d+\.\d+)/.test(navigator.userAgent) || /MSIE (\d+\.\d+);/.test(navigator.userAgent)) {
        $(".frequency_table").css('padding-left', '20px');
    }
    $(".hide_frequency").click(function() {
        hide_frequency();
    });
    sidebar_reports(q_string, db_url, pathname);
}
function hide_frequency() {
    $(".hide_frequency").hide();
    $("#freq").empty().hide();
    $('.frequency_container').hide();
    $(".loading").empty();
    $(".results_container").animate({
        "margin-right": "0px"},
        150);
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
            } else {
                var url = "?report=relevance&method=proxy&q=" + text;
                var report_link = '<a href="' + url + '" target="_blank" class="selected_tag">Run a ranked relevance search for this selection</a><br>';
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