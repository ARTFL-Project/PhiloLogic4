$(document).ready(function() {
    
    ////////////////////////////////////////////////////////////////////////////
    // Important variables /////////////////////////////////////////////////////
    ////////////////////////////////////////////////////////////////////////////
    var pathname = window.location.pathname.replace('dispatcher.py/', '');
    var db_path = window.location.hostname + pathname;
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
            $("#waiting").css("margin-left", width).show();
        });
    $("#reset_form, #freq_sidebar, #show_table_of_contents, #overlay_toggler, #hide_search_form, .more_options").button();
    $("#page_num, #field, #method, #year_interval, #time_series_buttons, #report_switch, #frequency_report_switch").buttonset();
    $("#word_num").spinner({
        spin: function( event, ui ) {
            if ( ui.value > 10 ) {
                $( this ).spinner( "value", 1 );
                return false;
            } else if ( ui.value < 1 ) {
                $( this ).spinner( "value", 10 );
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
    $('.conc_question, .freq_question, .colloc_question, .time_question, .relev_question').hide();
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
    
    monkeyPatchAutocomplete();    
    $("#q").autocomplete({
        source: pathname + "scripts/term_list.py",
        minLength: 2,
        "dataType": "json"
    });
    var fields = [];
    $('#metadata_fields input').each(function(){
        fields.push($(this).attr('name'));
    });
    for (i in fields) {
        var  metadata = $("#" + fields[i]).val();
        var field = fields[i];
        autocomplete_metadata(metadata, field)
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
            else if (key == 'pagenum' || key == 'field' || key == 'method' || key == 'year_interval') {
                $('input[name=' + key + '][value=' + value + ']').attr("checked", true);
            }
            else if (value == 'relative') {
                $('#' + key).attr('checked', true);
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
    ///////// Concordance / KWIC switcher //////////////////////////////////////
    ////////////////////////////////////////////////////////////////////////////
    $("#report_switch").on("change", function() {
        $('.highlight_options').remove();
        var switchto = $('input[name=report_switch]:checked').val();
        var width = $(window).width() / 3;
        $("#waiting").css("margin-left", width).show();
        $("#waiting").css("margin-top", 200).show();
        $.get("http://" + db_path + "/reports/concordance_switcher.py" + switchto, function(data) {
            $("#results_container").hide().empty().html(data).fadeIn('fast');
            $("#waiting").hide();
            // This should only be loaded for KWIC results
            var config = {    
                over: showBiblio, 
                timeout: 100,  
                out: hideBiblio   
            };
            $(".kwic_biblio").hoverIntent(config)
            display_options_on_selected();
        });
    });
    ////////////////////////////////////////////////////////////////////////////
    
    
    ////////////////////////////////////////////////////////////////////////////
    ///////// Frequency / Frequency per 10,000 switcher ////////////////////////
    ////////////////////////////////////////////////////////////////////////////
    $('#frequency_report_switch').on("change", function(){
        var switchto = $('input[name=freq_switch]:checked').val();
        var width = $(window).width() / 3;
        $("#waiting").css("margin-left", width).show();
        $("#waiting").css("margin-top", 200).show();
        $.get("http://" + db_path + "/scripts/frequency_switcher.py" + switchto, function(data) {
            $("#results_container").hide().html(data).fadeIn('fast');
            $("#waiting").hide();
        });
    });
    ////////////////////////////////////////////////////////////////////////////

    
    ////////////////////////////////////////////////////////////////////////////
    //  This will show more context in concordance searches ////////////////////
    ////////////////////////////////////////////////////////////////////////////
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
    ////////////////////////////////////////////////////////////////////////////
    
    
    ////////////////////////////////////////////////////////////////////////////
    // This will display the sidebar for various frequency reports /////////////
    ////////////////////////////////////////////////////////////////////////////
    $("#toggle_frequency").click(function() {
        toggle_frequency(q_string, db_path, pathname);
    });
    $("#frequency_field").change(function() {
        toggle_frequency(q_string, db_path, pathname);
    });
    $(".hide_frequency").click(function() {
        hide_frequency();
    });
    ////////////////////////////////////////////////////////////////////////////
    
    
    ////////////////////////////////////////////////////////////////////////////
    // Page and reader code ////////////////////////////////////////////////////
    ////////////////////////////////////////////////////////////////////////////
    // Change pages
    $(".prev_page, .next_page").on('click', function() {
        var my_path = db_path.replace(/(\/\d+)+$/, '/');
        var doc_id = db_path.replace(my_path, '').replace(/(\d+)\/*.*/, '$1');
        var page = $("#current_page").text();
        var go_to_page = $(this).attr('id');
        var myscript = "http://" + my_path + "scripts/go_to_page.py?philo_id=" + doc_id + "&go_to_page=" + go_to_page + "&doc_page=" + page;
        $.getJSON(myscript, function(data) {
            $("#current_page").fadeOut('fast', function() {
                $(this).html(data[2]).fadeIn('fast');
            });
            $("#page_text").fadeOut('fast', function () {
                $(this).html(data[3]).fadeIn('fast');
                $(".prev_page").attr("id", data[0]);
                $('.next_page').attr('id', data[1]);
                $()
            }); 
        });
        
    });
    $(".fake_prev_page, .fake_next_page").on('click', function() {
        var direction = $(this).attr('class');
        var page_count = $(".obj_text").children('div').size();
        var visible = $(".obj_text").children("div:visible")
        if (direction == "fake_prev_page") {
            $(".obj_text").children().filter("div:visible").hide().prev().fadeIn('fast');
        } else {
            $(".obj_text").children().filter("div:visible").hide().next().fadeIn('fast');
        }
    });
    
    // This is to display the table of contents in the document viewer
    $("#show_table_of_contents").click(function() {
        if ($("#t_b_c_box").text() == "Show table of contents") {
            $("#t_b_c_box").html("Hide table of contents");
            $(".table_of_contents").css('float', 'left');
            var width = $(".table_of_contents").width() + 20;
            $(".page_display").animate({
                "float": "right",
                "margin-left": width + "px"},
                50, function() {
                    $(".table_of_contents").fadeIn('fast');
            });         
        } else {
            $("#t_b_c_box").html("Show table of contents");
            $(".page_display").animate({
                "float": "",
                "margin-left": "0px"},
                50, function() {
                    $(".table_of_contents").hide();
            });
        }
    });
    
    // Toggle reading mode
    $("#overlay_toggler").click(function() {
        if ($("#overlay").is('*')) {
            $(".book_page").css('box-shadow', '0px 0px 15px #888888');
            $("#overlay").fadeOut('fast', function() {
                $(this).remove();
                $("#read").html('Start reading mode').fadeIn('fast');
            });
        } else {
            var docHeight = $(document).height();
            $("body").append("<div id='overlay' style='display:none;'></div>");
            $(".book_page").css('position', 'relative').css('box-shadow', '0px 0px 15px #FFFFFF');
            $("#read").html('Exit reading mode').fadeIn('fast');
            $("#overlay_toggler").css('z-index', 100).css('position', 'relative');
            $('.initial_form').css('z-index', 98);
            $('.book_page').css('z-index', 100);
            $("#overlay")
               .height(docHeight)
               .css({
                  'opacity' : 0.7,
                  'position': 'absolute',
                  'top': 0,
                  'left': 0,
                  'background-color': 'black',
                  'width': '100%',
                  'z-index': 99
                });
            $("#overlay").fadeIn('fast');
        }
    });
    ////////////////////////////////////////////////////////////////////////////
    
    
    ////////////////////////////////////////////////////////////////////////////
    // Contextual menu when selecting a word ///////////////////////////////////
    ////////////////////////////////////////////////////////////////////////////
    display_options_on_selected();
    ////////////////////////////////////////////////////////////////////////////
    
});


////////////////////////////////////////////////////////////////////////////////
//////////// FUNCTIONS /////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////



function display_options_on_selected() {
    $('.philologic_concordance, .kwic_concordance').mouseup(function(e) {
        $('.highlight_options').remove();
        var text = getSelectedText();
        if (text != '') {
            var options = $('<div class="highlight_options">');
            var my_table = '<table class="context_table" BORDER=1 RULES=ALL frame=void>';
            my_table += '<tr><td class="selected_word">"' + text.charAt(0).toUpperCase() + text.slice(1) + '"</td></tr>';
            var search_reports = ['concordance', "relevance", 'collocation']
            my_table += '<tr><td>';
            for (report in search_reports) {
                report = search_reports[report];
                var url = "?report=" + report + "&method=proxy&q=" + text;
                if (report != 'relevance') {
                    var report_link = '<a href="' + url + '" class="selected_tag">Run a ' + report + ' search for this selection</a><br>'
                } else {
                    var report_link = '<a href="' + url + '" class="selected_tag">Run a ranked relevance search for this selection</a><br>'
                }
                my_table += report_link;
            }
            if (text.split(' ').length == 1) {
                var url = "?report=time_series&method=proxy&q=" + text;
                var report_link = '<a href="' + url + '" class="selected_tag">Run a time series search for this selection</a><br>'
                var definition = '<a href="http://dvlf.uchicago.edu/mot/' + text + '" class="selected_tag">Get a definition of this word</a>'
                my_table += report_link;
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


// Patch jQueryUI autocomplete to get higlighting
function monkeyPatchAutocomplete() {
    $.ui.autocomplete.prototype._renderItem = function( ul, item) {
        // This regex took some fiddling but should match beginning of string and
        // any match preceded by a string: this is useful for sql matches.
        var re = new RegExp('((^' + this.term + ')|( ' + this.term + '))', "gi") ; 
        var t = item.label.replace(re,"<span class='highlight'>" + 
                "$&" + 
                "</span>");
        return $( "<li></li>" )
            .data( "item.autocomplete", item )
            .append( "<a>" + t + "</a>" )
            .appendTo( ul );
    };
}
function autocomplete_metadata(metadata, field) {
    var pathname = window.location.pathname.replace('dispatcher.py/', '');
    $("#" + field).autocomplete({
        source: pathname + "scripts/metadata_list.py?field=" + field,
        minLength: 2,
        dataType: "json"
    });
}

// Display different search parameters based on the type of report used
function showHide(value) {
    if (value == 'frequency') {
        $("#results_per_page, #collocation, #time_series, #year_interval").hide();
        $("#frequency, #method, #metadata_field").show();
        $('.explain_relev, .explain_conc, .explain_time, .explain_colloc').hide();
        $('.relev_question, .conc_question, .colloc_question, .time_question').hide();
        $('.freq_question').fadeIn();
    }
    if (value == 'collocation') {
        $("#results_per_page, #frequency, #method, #time_series, #year_interval").hide();
        $("#collocation, #metadata_field").show();
        $('.explain_relev, .explain_freq, .explain_time, .explain_conc').hide();
        $('.relev_question, .freq_question, .conc_question, .time_question').hide();
        $('.colloc_question').fadeIn();
    }
    if (value == 'concordance') {
        $("#frequency, #collocation, #time_series, #year_interval").hide();
        $("#results_per_page, #method, #metadata_field").show();
        $('.explain_relev, .explain_freq, .explain_time, .explain_colloc').hide();
        $('.relev_question, .freq_question, .colloc_question, .time_question').hide();
        $('.conc_question').fadeIn();
    }
    if (value == 'relevance') {
        $("#collocation, #frequency, #method, #time_series, #year_interval").hide();
        $("#results_per_page, #metadata_field").show();
        $('.explain_conc, .explain_freq, .explain_time, .explain_colloc').hide();
        $('.conc_question, .freq_question, .colloc_question, .time_question').hide();
        $('.relev_question').fadeIn();
    }
    if (value == "time_series") {
        $("#results_per_page, #metadata_field, #method, #frequency, #collocation").hide();
        $("#time_series, #year_interval").show();
        $('.explain_relev, .explain_freq, .explain_conc, .explain_colloc').hide();
        $('.relev_question, .freq_question, .colloc_question, .conc_question').hide();
        $('.time_question').fadeIn();
    }
}

// These functions are for the kwic bibliography which is shortened by default
function showBiblio() {
    $(this).children("#full_biblio").css('position', 'absolute').css('text-decoration', 'underline')
    $(this).children("#full_biblio").css('background', 'LightGray')
    $(this).children("#full_biblio").css('box-shadow', '5px 5px 15px #C0C0C0')
    $(this).children("#full_biblio").css('display', 'inline')
}

function hideBiblio() {
    $(this).children("#full_biblio").fadeOut(200)
}

//    These functions are for the sidebar frequencies
function toggle_frequency(q_string, db_url, pathname) {
    var field =  $("#frequency_field").val();
    if (field != 'collocate') {
        var script_call = "http://" + db_url + "scripts/get_frequency.py?" + q_string + "&frequency_field=" + field;
    } else {
        var script_call = "http://" + db_url + "scripts/get_collocate.py?" + q_string
    }
    $(".loading").empty().hide();
    var spinner = '<img src="http://' + db_url + '/js/ajax-loader.gif" alt="Loading..."  height="25px" width="25px"/>';
    $(".results_container").animate({
        "margin-right": "420px"},
        50);
    var width = $(".sidebar_display").width() / 2;
    $(".loading").append(spinner).css("margin-left", width).css("margin-top", "10px").show();
    $.getJSON(script_call, function(data) {
        var newlist = "";
        $(".loading").hide().empty();
        if (field == "collocate") {
            newlist += "<p class='freq_sidebar_status'>Collocates within 5 words left or right</p>";
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
}
function hide_frequency() {
    $(".hide_frequency").fadeOut();
    $("#freq").empty().hide();
    $('.frequency_container').hide();
    $(".loading").empty();
    $(".results_container").animate({
        "margin-right": "0px"},
        50);
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
       'opacity' : 0.0,
       'position': 'absolute',
       'top': 0,
       'left': 0,
       'background-color': '#E0E0E0',
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

// Set of functions for updating collocation tables
function colloc_linker(word, q_string, direction, num) {
    q_string = q_string.replace('collocation', 'concordance_from_collocation');
    q_string += '&collocate=' + encodeURIComponent(word);
    q_string += '&direction=' + direction;
    q_string += '&collocate_num=' + num;
    link = '<a href="?' + q_string + '">' + word + '</a>'
    return link
}

function update_table(full_results, new_hash, q_string, column) {
    $('[id^=' + column+ '_]').hide();
    for (key in new_hash) {
        if (key in full_results) {
            full_results[key] += new_hash[key];
        }
        else {
            full_results[key] = new_hash[key];
        }
    }
    var sorted_list = [];
    for (key in full_results) {
        sorted_list.push([key, full_results[key]]);
    }
    sorted_list.sort(function(a,b) {return b[1] - a[1]});
    var pos = 0;
    for (i in sorted_list) {
        pos += 1;
        var link = colloc_linker(sorted_list[i][0], q_string, column, sorted_list[i][1]);
        var count_id = column + '_count_' + sorted_list[i][1];
        data = link + '<span id="' + count_id + '"> (' + sorted_list[i][1] + ')</span>';
        $('#' + column + '_num' + pos).html(data);
    }
    $('[id^=' + column+ '_]').fadeIn(800);
    return full_results;
}

function update_colloc(all_colloc, left_colloc, right_colloc, results_len, colloc_start, colloc_end) {
    var pathname = window.location.pathname.replace('dispatcher.py/', '');
    var db_path = window.location.hostname + pathname;
    var q_string = window.location.search.substr(1);
    var script = "http://" + db_path + "scripts/collocation_fetcher.py?" + q_string
    if (colloc_start == 0) {
        colloc_start = 100;
        colloc_end = 1100;
    } else {
        colloc_start += 1000;
        colloc_end += 1000;
    }
    var script_call = script + '&colloc_start=' + colloc_start + '&colloc_end=' + colloc_end
    if (colloc_start <= results_len) {
        $.when($.getJSON(script_call).done(function(data) {
            all_new_colloc = update_table(all_colloc, data[0], q_string, "all");
            left_new_collc = update_table(left_colloc, data[1], q_string, "left");
            right_new_colloc = update_table(right_colloc, data[2], q_string, "right");
            update_colloc(all_new_colloc, left_colloc, right_colloc, results_len, colloc_start, colloc_end);
            collocation_cloud();
        }));
    }
    else {
        $("#working").hide();
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
    unordered_list = unordered_list.sort(function() {
                                            return Math.round( Math.random() ) - 0.5;
                                        });
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
    for (word in colloc_counts) {
        var searchlink = '<a href="' + colloc_counts[word]['href'] + '" class="cloud_term" rel="' + colloc_counts[word]['count'] + '"> ';
        var full_link = searchlink + word + ' </a>';
        $("#collocate_counts").append(full_link);
    }
    $("#collocate_counts a").tagcloud();
    //$(".cloud_term :hover").css('text-decoration', 'none');
    //$(".cloud_term :hover").css('color', 'black');
    $("#collocate_counts").fadeIn('fast');
}