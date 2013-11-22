$(document).ready(function() {
    
    var db_url = db_locals['db_url'];
    var q_string = window.location.search.substr(1);
    
    
    for (i in db_locals['search_reports']) {
        var search_report = '#' + db_locals['search_reports'][i] + '_button';
        $(search_report).show();
    }
    
    $("#q").focus(function() {
        if ($("#philologic_response").is('*')) {
            show_more_options("report");
            hide_search_on_click();
        }
    });
    $('#more_options').click(function() {
        $('#search_elements').css('z-index', 150);
        $('.book_page').css('z-index', 90);
        if ($(this).text() == "Show search options") {
            show_more_options("all");
            $('#search_explain').slideDown();
            hide_search_on_click();
        } else {
            hide_search_form();
        }
    });
    $("#report").buttonset();
    $('#form_body').show();
    $("#search_elements").hide();
    $('#conc_question, #freq_question, #colloc_question, #time_question, #relev_question, #kwic_question').hide();
    $('#search_explain').hide();
    showHide($('input[name=report]:checked', '#search').val());
    $('#report').click(function() {
        var report = $('input[name=report]:checked', '#search').val();
        if ($("#search_elements:visible")) {
            showHide(report);
            if (report != "frequencies") {
                $("#search_elements").slideDown();
                $('#search_explain').slideDown();
            }
        } else {
            showHide(report);
            if (report != "frequencies") {
                $("#search_elements").fadeIn();
                $('#search_explain').fadeIn();
            }
        }
    });
      
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
        term = item.label.replace(/^[^<]*/g, '');
        return $("<li></li>")
            .data("item.autocomplete", item)
            .append("<a>" + term + "</a>")
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
    $("#reset_form, #reset_form1").click(function() {
        $("#method").find("input:radio").attr("checked", false).end();
        $("#method1").attr('checked', true);
        $("#method").buttonset('refresh');
        $("#page_num").find("input:radio").attr("checked", false).end();
        $("#pagenum2").attr('checked', true);
        $("#page_num").buttonset('refresh');
        $('#search')[0].reset();
        $("#search_elements").fadeIn();
        $("#reset_form1").css('color', '#555555 !important');
        $("#report").find("input:radio").attr("checked", false).end();
        $('#concordance').attr('checked', true);
        $('#concordance')[0].click();
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
    
    $('#syntax').offset({"left":  $('#q').offset().left});
    
    $('#syntax_title').mouseup(function() {
        if ($('#syntax_explain').not(':visible')) {
            $('#syntax_explain').fadeIn('fast');
        }
        $(document).mousedown(function() {
            $('#syntax_explain').fadeOut('fast');
        });
    });
    
//    Check if the search form has any input has been prefilled
    $('input:text').each(function(){
        if ($(this).val().length) {
            if ($(this).attr('id') != 'word_num') {
                $('#reset_form1').find('.ui-button-text').blink()
                return false;
            }
        }
    });
    $(window).load(function() {
        adjustReportWidth();
    });
    
});

//    Adjust width of report buttons
function adjustReportWidth() {
    var button_length = 0;
    var report_num = 0
    $("#report").find('label').first().css('border-left', '0px');
    $("#report").find('label').each(function() {
        if ($(this).is(':visible')) {
            button_length += $(this).width();
            report_num += 1;
            $(this).css({'border-bottom': '0px', 'border-top': '0px'});
        }
    });
    length_to_add = ($("#report").width() - button_length) / report_num;
    $('#report').find("label").each(function() {$(this).css("width", "+=" + (length_to_add));});
}

function autocomplete_metadata(metadata, field, db_url) {
    $("#" + field).autocomplete({
        source: db_url + "/scripts/metadata_list.py?field=" + field,
        minLength: 2,
        timeout: 1000,
        dataType: "json",
        focus: function( event, ui ) {
            q = ui.item.label.replace(/<\/?span[^>]*?>/g, '');
            q = q.replace(/ CUTHERE /, ' ');
            $("#" + field).val(q);
            return false;
        },
        select: function( event, ui ) {
            q = ui.item.label.replace(/<\/?span[^>]*?>/g, '');
            q = q.replace(/ CUTHERE /, ' ');
            $("#" + field).val(q);
            return false;
        }
    }).data("ui-autocomplete")._renderItem = function (ul, item) {
        term = item.label.replace(/.*(?=CUTHERE)CUTHERE /, '');
        return $("<li></li>")
            .data("item.autocomplete", item)
            .append("<a>" + term + "</a>")
            .appendTo(ul);
     };
}

// Display different search parameters based on the type of report used
function showHide(value) {
    $("#results_per_page, #collocation_num, #time_series_num, #year_interval,#frequency_num, #method, #metadata_fields").hide();
    $('#explain_relev, #explain_conc, #explain_time, #explain_colloc, #explain_kwic, #explain_freq').hide();
    $('#relev_question, #conc_question, #colloc_question, #time_question, #kwic_question, #freq_question').hide();
    $('#frequency_task, #bottom_search').hide()

    if (value == 'frequency') {
        $("#frequency_num, #method, #metadata_fields").show();
        $('#metadata_fields').find('tr').has('#date').show();
        $('#freq_question').show();
        $('#search_terms_container').slideDown('fast');
    }
    if (value == 'collocation') {
        $("#collocation_num, #method, #metadata_fields").show();
        $('#metadata_fields').find('tr').has('#date').show();
        $('#colloc_question').show();
        $('#search_terms_container').slideDown('fast');
    }
    if (value == 'kwic') {
        $("#results_per_page, #method, #metadata_fields").show();
        $('#metadata_fields').find('tr').has('#date').show();
        $('#kwic_question').show();
        $('#search_terms_container').slideDown('fast');
    }
    if (value == 'concordance') {
        $("#results_per_page, #method, #metadata_fields").show();
        $('#metadata_fields').find('tr').has('#date').show();
        $('#conc_question').show();
        $('#start_date, #end_date').val('');
        $('#search_terms_container').slideDown('fast');
    }
    if (value == 'relevance') {
        $("#results_per_page").show();
        $('#relev_question').show();
    }
    if (value == "time_series") {
        $("#time_series_num, #year_interval, #method, #metadata_fields").show();
        $('#metadata_fields').find('tr').has('#date').hide();
        $('#time_question').show();
        $('#date').val('');
        $('#search_terms_container').slideDown('fast');
    }
    if (value == "frequencies") {
        $('#search_terms_container').slideUp('fast');
        $('#search_elements').hide();
        $('#frequency_task').show();
        $('#bottom_search').show();   
    }
}

//  Function to show or hide search options
function show_more_options(display) {
    $("#more_options").button('option', 'label', 'Hide search options');
    if (display == "all") {
        var report = $('input[name=report]:checked', '#search').val();
        showHide(report);
        $("#search_elements").slideDown();
    }
    $('#form_body').css('z-index', 99);
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
    $('#search_explain').accordion({
        collapsible: true,
        heightStyle: "content",
        active: false
    });
    $("#search_elements").slideUp();
    $("#search_overlay").fadeOut('fast', function() {
        $(this).remove();
    });
    $("#more_options").button('option', 'label', 'Show search options');
    $('#search_explain').slideUp();
}
function hide_search_on_click() {
    $("#search_overlay, #header, #footer").click(function() {
        hide_search_form();
    }); 
}

(function($)
{
    $.fn.blink = function(options) {
        var defaults = { delay:1500 };
        var options = $.extend(defaults, options);

        return this.each(function() {
            var obj = $(this);
            var state = false;
            var colorchange = setInterval(function() {
                if(state)
                {
                    $(obj).animate({color: '#555555 !important'}, 1500);
                    state = false;
                }
                else
                {
                    $(obj).animate({color: 'rgb(255,0,0) !important'}, 1500);
                    state = true;
                }
            }, options.delay);
            $('#reset_form, #reset_form1').click(function() {
                $(obj).css('color', '#555555 !important');
                clearInterval(colorchange);
            });
        });
    }
}(jQuery))