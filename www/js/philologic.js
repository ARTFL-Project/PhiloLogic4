function monkeyPatchAutocomplete() {
    //taken from http://stackoverflow.com/questions/2435964/jqueryui-how-can-i-custom-format-the-autocomplete-plug-in-results    
    $.ui.autocomplete.prototype._renderItem = function( ul, item) {
        // This regex took some fiddling but should match beginning of string and
        // any match preceded by a string: this is useful for sql matches.
        var re = new RegExp('((^' + this.term + ')|( ' + this.term + '))', "gi") ; 
        var t = item.label.replace(re,"<span style='font-weight:bold;color:Red;'>" + 
                "$&" + 
                "</span>");
        return $( "<li></li>" )
            .data( "item.autocomplete", item )
            .append( "<a>" + t + "</a>" )
            .appendTo( ul );
    };
}

var pathname = window.location.pathname.replace('dispatcher.py/', '');

function autocomplete_metadata(metadata, field) {
    $("#" + field).autocomplete({
        source: pathname + "scripts/metadata_list.py?field=" + field,
        minLength: 2,
        dataType: "json"
    });
}


$(document).ready(function(){
    
    var pathname = window.location.pathname.replace('dispatcher.py/', '');
    var db_path = window.location.hostname + pathname;
    var q_string = window.location.search.substr(1);
    
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
            hide_search_on_click();
        } else {
            hide_search_form();
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
    
    //  This is for displaying the full bibliography on mouse hover
    //  in kwic reports
    var config = {    
        over: showBiblio, 
        timeout: 100,  
        out: hideBiblio   
    };
    $(".kwic_biblio").hoverIntent(config)

    //  This will show more context in concordance searches
    $(".more_context").click(function(e) {
        var context_link = $(this).text();
        if (context_link == 'More') {
            $(this).siblings('.philologic_context').children('.begin_concordance').show()
            $(this).siblings('.philologic_context').children('.end_concordance').show()
            $(this).empty().fadeIn(100).append('Less')
        } 
        else {
            $(this).siblings('.philologic_context').children('.begin_concordance').hide()
            $(this).siblings('.philologic_context').children('.end_concordance').hide()
            $(this).empty().fadeIn(100).append('More')
        }
        e.preventDefault();
    });
    
    //  This will prefill the search form with the current query
    var val_list = q_string.split('&');
    for (var i = 0; i < val_list.length; i++) {
        var key_value = val_list[i].split('=');
        var my_value = decodeURIComponent((key_value[1]+'').replace(/\+/g, '%20'));
        if (my_value) {
            if (key_value[0] == 'pagenum' || key_value[0] == 'report' || key_value[0] == 'field' || key_value[0] == 'word_num' || key_value[0] == 'method' || key_value[0] == 'year_interval') {
                $('input[name=' + key_value[0] + '][value=' + my_value + ']').attr("checked", true)
            }
            else if (my_value == 'relative') {
                $('#' + key_value[0]).attr('checked', true);
            }
            else {
                $('#' + key_value[0]).val(my_value);
            }
        }
    }
    
    $("#report").buttonset();
    
    $('.form_body').show();
    //showHide($('input[name=report]:checked', '#search').val());
    $("#search_elements").hide();
    
    $('#report').click(function() {
        var report = $('input[name=report]:checked', '#search').val();
        if ($("#search_elements:visible")) {
            showHide(report);
            $("#search_elements").slideDown();
        } else {
            showHide(report);
            $("#search_elements").fadeIn();
        }
    });
    
    
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
    
    //    This will display the sidebar for various frequency reports
    $("#toggle_frequency").click(function() {
        toggle_frequency(q_string, db_path, pathname);
    });
    $("#frequency_field").change(function() {
        toggle_frequency(q_string, db_path, pathname);
    });
    $(".hide_frequency").click(function() {
        hide_frequency();
    });
    
    
    //  This is to switch views between concordance and KWIC
    $("#report_switch").change(function() {
        var switchto = $('input[name=report_switch]:checked').val();
        var width = $(window).width() / 3;
        $("#waiting").css("margin-left", width).show();
        $("#waiting").css("margin-top", 200).show();
        $.get("http://" + db_path + "/reports/concordance_switcher.py" + switchto, function(data) {
            $("#results_container").hide().empty().html(data).fadeIn('fast');
            $("#waiting").hide();
        });
    });
    
    
    // Change page in docs
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
    
    //  jQueryUI theming
    $( "#button, #button1" )
            .button()
            .click(function( event ) {
                $("#search_elements").slideUp(function() {
                    $("#report").hide();
                    var width = $(window).width() / 3;
                    $("#waiting").css("margin-left", width).show();
                });
            });
    $("#reset_form, #freq_sidebar, #show_table_of_contents, #overlay_toggler, #hide_search_form, .more_options").button();
    $("#page_num, #word_num, #field, #method, #year_interval, #time_series_buttons, #report_switch").buttonset()
    $(".show_search_form").tooltip({ position: { my: "left+10 center", at: "right" } });
    $(".tooltip_link").tooltip({ position: { my: "left top+5", at: "left bottom", collision: "flipfit" } }, { track: true });
    
    
});

function showHide(value) {
    if (value == 'frequency') {
        $("#results_per_page, #collocation, #time_series, #year_interval").hide();
        $("#frequency, #method, #metadata_field").show();
        $('.explain_relev, .explain_conc, .explain_time, .explain_colloc').hide();
        $('.explain_freq').fadeIn('slow');
    }
    if (value == 'collocation') {
        $("#results_per_page, #frequency, #method, #time_series, #year_interval").hide();
        $("#collocation, #metadata_field").show();
        $('.explain_relev, .explain_freq, .explain_time, .explain_conc').hide();
        $('.explain_colloc').fadeIn('slow');
    }
    if (value == 'concordance') {
        $("#frequency, #collocation, #time_series, #year_interval").hide();
        $("#results_per_page, #method, #metadata_field").show();
        $('.explain_relev, .explain_freq, .explain_time, .explain_colloc').hide();
        $('.explain_conc').fadeIn('slow');
    }
    if (value == 'relevance') {
        $("#collocation, #frequency, #method, #time_series, #year_interval").hide();
        $("#results_per_page, #metadata_field").show();
        $('.explain_conc, .explain_freq, .explain_time, .explain_colloc').hide();
        $('.explain_relev').fadeIn('slow');
    }
    if (value == "time_series") {
        $("#results_per_page, #metadata_field, #method, #frequency, #collocation").hide();
        $("#time_series, #year_interval").show();
        $('.explain_relev, .explain_freq, .explain_conc, .explain_colloc').hide();
        $('.explain_time').fadeIn('slow');
    }
}

// These functions are for the kwic bibliography which is shortened by default
function showBiblio() {
    $(this).children("#full_biblio").css('position', 'absolute').css('text-decoration', 'underline')
    $(this).children("#full_biblio").css('background', 'LightGray')
    $(this).children("#full_biblio").css('box-shadow', '5px 5px 5px #888888')
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

//  Function to show ore search options
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
    $("#search_elements").slideUp();
    $("#search_overlay").fadeOut('fast', function() {
        $(this).remove();
    });
    $(".more_options").button('option', 'label', 'Show search options');
    $('.explain_conc, .explain_relev, .explain_freq, .explain_time, .explain_colloc').fadeOut();
}
function hide_search_on_click() {
    $("#search_overlay, #header, #footer").click(function() {
        hide_search_form();
    }); 
}