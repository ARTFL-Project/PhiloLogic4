$(document).ready(function() {
    
    var db_url = db_locals['db_url'];
    var q_string = window.location.search.substr(1);

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
    
});


function autocomplete_metadata(metadata, field, db_url) {
    $("#" + field).autocomplete({
        source: db_url + "/scripts/metadata_list.py?field=" + field,
        minLength: 2,
        timeout: 1000,
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