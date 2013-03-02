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
    
    var fields = [];
    $('#metadata_fields input').each(function(){
        fields.push($(this).attr('name'));
    });
    
    var pathname = window.location.pathname.replace('dispatcher.py/', '');
    var db_path = window.location.hostname + pathname;
    var q_string = window.location.search.substr(1);
    
    $(".show_search_form").click(function() {
        var link = $(this).text()
        if ($("#search_elements").css('display') == 'none') {
            link = link.replace("Show", "Hide");
            $(this).tooltip({content: "Click to hide the search form"},{ position: { my: "left+10 center", at: "right" } });
        } else {
            link = link.replace("Hide", "Show");
            $(this).tooltip({content: "Click to show the search form"},{ position: { my: "left+10 center", at: "right" } });
        }
        $(this).text(link);
        $("#search_elements").slideToggle()
    });
    
    monkeyPatchAutocomplete();    
    
    $("#q").autocomplete({
        source: pathname + "scripts/term_list.py",
        minLength: 2,
        "dataType": "json"
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
    $(document).on("click", ".more_context", function() {
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
    showHide($('input[name=report]:checked', '#search').val());
    
    $('#report').change(function() {
        var report = $('input[name=report]:checked', '#search').val();
        var visible = new Boolean(1);
        if ($("#search_elements").css('display') == "none") {
            visible = Boolean(0);
        }
        showHide(report);
        if (visible) {
            $("#search_elements").fadeIn();
        } else {
            $("#search_elements").slideDown();
        }
    });
    
    
    //  Clear search form
    $("#reset").click(function() {
        $("#q").empty();
        $("#arg").empty();
        for (i in fields) {
            var field = $("#" + i);
            $(field).empty();
        }
        $("#method1").prop('checked', true).button("refresh");
        $("#report1").prop('checked', true).button("refresh");
        $("#pagenum1").prop('checked', true).button("refresh");
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
        $.get("http://" + db_path + "/reports/concordance_switcher.py" + switchto, function(data) {
            $("#results_container").hide().empty().html(data).fadeIn('fast');
            $("#waiting").hide();
        });
    });
    
    // This is to display the table of contents in the document viewer
    $("#show_table_of_contents").click(function() {
        if ($("#t_b_c_box").text() == "Show table of contents") {
            $("#t_b_c_box").html("Hide table of contents");
            $(".table_of_contents").css('float', 'left');
            var width = $(".table_of_contents").width() + 20;
            $(".page_display, .object_display").animate({
                "float": "right",
                "margin-left": width + "px"},
                50, function() {
                    $(".table_of_contents").fadeIn('fast');
            });
            
        } else {
            $("#t_b_c_box").html("Show table of contents");
            $(".page_display, .object_display").animate({
                "float": "",
                "margin-left": "0px"},
                50, function() {
                    $(".table_of_contents").hide();
            });
        }
    });
    
    //  jQueryUI theming
    $( "#button" )
            .button()
            .click(function( event ) {
                $("#search_elements").slideUp(function() {
                    var width = $(window).width() / 3;
                    $("#waiting").css("margin-left", width).show();
                });
            });
    $("#reset, #freq_sidebar, #show_table_of_contents").button();
    $("#page_num, #word_num, #field, #method, #year_interval, #time_series_buttons, #report_switch").buttonset()
    $(".show_search_form").tooltip({ position: { my: "left+10 center", at: "right" } });
    $(".tooltip_link").tooltip({ position: { my: "left top+5", at: "left bottom", collision: "flipfit" } }, { track: true });
    
    
});

function showHide(value) {
    if (value == 'frequency') {
        $("#search_elements").hide();
        $("#results_per_page, #collocation, #time_series, #year_interval").hide();
        $("#frequency, #method, #metadata_field").show();
    }
    if (value == 'collocation') {
        $("#search_elements").hide()
        $("#frequency").hide()
        $("#results_per_page").hide()
        $("#method, #time_series, #year_interval").hide()
        $("#collocation, #metadata_field").show()
    }
    if (value == 'concordance') {
        $("#search_elements").hide()
        $("#frequency").hide()
        $("#collocation, #time_series, #year_interval").hide()
        $("#results_per_page, #method, #metadata_field").show()
    }
    if (value == 'kwic') {
        $("#search_elements").hide()
        $("#frequency").hide()
        $("#collocation, #time_series, #year_interval").hide()
        $("#results_per_page, #method, #metadata_field").show()
    }
    if (value == 'relevance') {
        $("#search_elements").hide()
        $("#frequency").hide()
        $("#collocation").hide()
        $("#method, #time_series, #year_interval").hide()
        $("#results_per_page, #metadata_field").show()
    }
    if (value == "time_series") {
        $("#search_elements").hide();
        $("#results_per_page, #metadata_field, #method, #frequency, #collocation").hide();
        $("#time_series, #year_interval").show();
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
    var spinner = '<img src="http://' + db_url + '/js/spinner-round.gif" alt="Loading..." />';
    if ($("#toggle_frequency").hasClass('show_frequency')) {
        $(".results_container").animate({
            "margin-right": "330px"},
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
        $("#freq").show();
    }
}
function hide_frequency() {
    $(".hide_frequency").fadeOut();
    $("#freq").empty().hide();
    $(".loading").empty();
    $(".results_container").animate({
        "margin-right": "0px"},
        50);
}