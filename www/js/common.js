$(document).ready(function() {
    
    ////////////////////////////////////////////////////////////////////////////
    // Important variables /////////////////////////////////////////////////////
    ////////////////////////////////////////////////////////////////////////////
    var pathname = window.location.pathname.replace('dispatcher.py/', '');
    var db_url = webConfig['db_url'];
    var q_string = window.location.search.substr(1);
    ////////////////////////////////////////////////////////////////////////////
    
    //////////////////////////////////    
    //// Search Form related code ////
    //////////////////////////////////
    
    // Check if on a mobile device
    if (global_report == "landing_page" && isMobile()) {
        if (sessionStorage[window.location.href] == null) {
            var mobile_choice = '<div id="mobile_choice"><div style="margin-bottom:1em">Do you want to use the mobile version of PhiloLogic4?</div></div>';
            $('body').append(mobile_choice);
            $("#mobile_choice").dialog({
                position: { my: "center", at: "top+300", of: window },
                title: "PhiloLogic4 alert",
                resizable: false,
                height:170,
                width: 430,
                modal: true,
                buttons: {
                  "Use mobile version": function() {
                    sessionStorage[window.location.href] = "mobile";
                    $('body').fadeOut(function() {
                        window.location = 'mobile/philologic.html';
                    });
                  },
                  "Use desktop version": function() {
                    sessionStorage[window.location.href] = "desktop";
                    $(this).dialog("close");
                  }
                }
            });
        } else if (sessionStorage[window.location.href] == 'mobile') {
            $('body').fadeOut(function() {
                window.location = 'mobile/philologic.html';
            });
        }
    }
    
    ////// jQueryUI theming //////
    $("#button, #button1, #reset_form, #reset_form1, #hide_search_form, #more_options, .more_context").button();
    $('#button2, #search_explain').button();
    $("#page_num, #field, #method, #year_interval").buttonset();
    $("#word_num").spinner({
        spin: function(event, ui) {
                if ( ui.value > 10 ) {
                    $(this).spinner( "value", 1 );
                    return false;
                } else if ( ui.value < 1 ) {
                    $(this).spinner( "value", 10 );
                    return false;
                }
            }
    });
    $("#word_num").val(5);
    $("#show_search_form").tooltip({ position: { my: "left+10 center", at: "right" } });
    $(".tooltip_link").tooltip({ position: { my: "left top+5", at: "left bottom", collision: "flipfit" } }, { track: true });
    
    $('.ui-spinner').css('width', '45px')
    $(':text').addClass("ui-corner-all");
    
    ////////////////////////////////////////
    
    
    // Display report tabs according to web_config.cfg
    for (i in webConfig['search_reports']) {
        var search_report = '#' + webConfig['search_reports'][i] + '_button';
        $(search_report).show();
    }
    
    
    $('#more_options').click(function() {
        $('#search_elements').css('z-index', 150);
        $('.book_page').css('z-index', 90);
        if ($(this).text() == "Show search options") {
            showMoreOptions("all");
        } else {
            hideSearchForm();
        }
    });
    $("#report").buttonset();
    $('#form_body').show();
    var form_height = $(window).height() - $('#header').height() - $('#footer').height() - $('#initial_form').height();
    if (global_report == "landing_page") {
        $('#more_options').hide();
        showHide('concordance');
        $(window).load(function() {
            $('#search_elements').css('opacity', 0)
                .slideDown(200)
                .animate(
                  { opacity: 1 },
                  { queue: false, duration: 200 }
                );
            setTimeout(searchFormOverlap, 200);
        });
    } else {
        $('#initial_form').css({'max-height': '94px', 'opacity': 100});
        showHide($('input[name=report]:checked', '#search').val());
    }
    $('#report').find('label').click(function() {
        var report = $(this).attr('for');
        if ($("#search_elements").css('display') != 'none') {
            showHide(report);
            if (report != "frequencies") {
                $("#search_elements").css('opacity', 0)
                    .slideDown(200)
                    .animate(
                      { opacity: 1 },
                      { queue: false, duration: 200 }
                    );
            }
            showMoreOptions();
        } else {
            showHide(report);
            if (report != "frequencies") {
                $("#search_elements").fadeIn();
            }
            showMoreOptions();
        }
    });
    
    
    // Set-up autocomplete for words and metadata
    autoCompleteWord(db_url);
    for (i in webConfig["metadata"]) {
        var  metadata = $("#" + webConfig["metadata"][i]).val();
        var field = webConfig["metadata"][i];
        autoCompleteMetadata(metadata, field, db_url)
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
        $("#pagenum1").attr('checked', true);
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
    
    /// Make sure search form doesn't cover footer
    $(window).resize(function() {
        searchFormOverlap();
    });
    
    adjustReportWidth();
    adjustBottomBorder();
    
    metadataRemove();
    
    // Display help menu on click
    $('#search_explain').click(function(e) {
        e.preventDefault();
        $('div[id^="explain"]').hide();
        var report = $("#report").find('input:checked').attr('id');
        $("#explain_" + report).show();
        var title = $("#explain_" + report).data('title');
        $('#search_explain_content').show().dialog({
            position: { my: "center", at: "top+300", of: window },
            //title: title,
            draggable: false,
            resizable: false,
            height:"auto",
            width: 400,
            modal: true,
        });
    });
    
    // Add spinner to indicate that a query is running in the background
    $('#button, #button1').click(function( event ) {
        var width = $(window).width() / 2 - 100;
        hideSearchForm();
        $("#waiting").css("margin-left", width).css('margin-top', 100).show();
    });
});

// Remove metadata criteria on click
function metadataRemove() {
    $('.remove_metadata').click(function() {
        var href = window.location.href;
        var metadata = $(this).data("metadata");
        var match = href.match("&" + metadata + "=[^&]+");
        href = href.replace(match, "&" + metadata + "=");
        window.location = href;
    });
    if (global_report == "time_series") {
        $('#remove_metadata_date_start, #remove_metadata_date_end').click(function() {
            var href = window.location.href;
            if ($(this).attr('id') == "remove_metadata_date_start") {
                href = href.replace(/(&start_date=)[^&]+/, '$1');
            } else {
                href = href.replace(/(&end_date=)[^&]+/, '$1');
            }
            window.location = href;
        });
    }
}

function isMobile() {
  var index = navigator.appVersion.indexOf("Mobile");
  return (index > -1);
}

function searchFormOverlap() {
    var form_offset = $('#form_body').offset().top + $('#form_body').height();
    var footer_offset = $('#footer').offset().top;
    if (form_offset > footer_offset) {
        $('#footer').css('top', form_offset + 20);
    } else {
        $('#footer').css('top', 'auto');
    }
}

//    Adjust width of report buttons
function adjustReportWidth() {
    var button_length = 0;
    var report_num = 0
    $("#report").find('label').first().css('border-left', '0px');
    $("#report").find('label').each(function() {
        if ($(this).is(':visible')) {
            button_length += $(this).width();
            report_num += 1;
            $(this).css({'border-top': '0px'});
        }
    });
    length_to_add = ($("#report").width() - button_length) / report_num;
    $('#report').find("label").each(function() {$(this).css("width", "+=" + (length_to_add));});
}
function adjustBottomBorder() {
    $('#report').find('label').each(function() {
        if ($(this).hasClass('ui-state-active')) {
            $(this).css('border-bottom-width', '0px');
        } else {
            $(this).css('border-bottom', '1px solid #D3D3D3');
        }
    });
}

function autoCompleteWord(db_url) {
    $("#q").autocomplete({
        source: db_url + "/scripts/term_list.py",
        minLength: 2,
        "dataType": "json",
        focus: function( event, ui ) {
            q = ui.item.label.replace(/<\/?span[^>]*?>/g, '');
            //$("#" + field).val(q); This is too sensitive, so disabled
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
}

function autoCompleteMetadata(metadata, field, db_url) {
    $("#" + field).autocomplete({
        source: db_url + "/scripts/metadata_list.py?field=" + field,
        minLength: 2,
        timeout: 1000,
        dataType: "json",
        focus: function( event, ui ) {
            q = ui.item.label.replace(/<\/?span[^>]*?>/g, '');
            q = q.replace(/ CUTHERE /, ' ');
            //$("#" + field).val(q); This is too sensitive, so disabled
            return false;
        },
        select: function( event, ui ) {
            q = ui.item.label.replace(/<\/?span[^>]*?>/g, '');
            q = q.replace(/ CUTHERE /, ' ');
            q = q.split('|');
            q[q.length-1] = '\"' + q[q.length-1].replace(/^\s*/g, '') + '\"'; 
            q = q.join('|');
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
    $("#results_per_page, #collocation_num, #time_series_num, #date_range, #method, #metadata_fields").hide();
    $('#bottom_search').hide()
    if (value == 'collocation') {
        $("#collocation_num, #metadata_fields").show();
        $('#metadata_fields').find('tr').has('#date').show();
        $('#search_terms_container').slideDown(300);
    }
    if (value == 'kwic' || value == "concordance") {
        $("#results_per_page, #method, #metadata_fields").show();
        $('#metadata_fields').find('tr').has('#date').show();
        $('#start_date, #end_date').val('');
        $('#search_terms_container').slideDown(300);
    }
    if (value == 'relevance') {
        $("#results_per_page").show();
    }
    if (value == "time_series") {
        $("#time_series_num, #date_range, #method, #metadata_fields").show();
        $('#metadata_fields').find('tr').has('#date').hide();
        $('#date').val('');
        $('#search_terms_container').slideDown(300);
    }
    if (value == "frequencies") {
        $('#search_terms_container, #method, #results_per_page').hide();
        $('#metadata_fields, #bottom_search').show();   
    }
    adjustBottomBorder();
}

//  Function to show or hide search options
function showMoreOptions(display) {
    $("#more_options").button('option', 'label', 'Hide search options');
    if (display == "all") {
        var report = $('input[name=report]:checked', '#search').val();
        showHide(report);
        $("#search_elements").css('opacity', 0)
            .slideDown(200)
            .animate(
              { opacity: 1 },
              { queue: false, duration: 200 }
            );
    }
    var height = $(document).height() - $(header).height() - $(footer).height();
    $("#search_overlay").css({'top': $('#header').height() + 'px', 'opacity': 0.2, 'height': height});
    setTimeout(searchFormOverlap, 200);
    $("#search_overlay, #header, #footer").click(function() {
        hideSearchForm();
    });
}

function hideSearchForm() {
    $("#search_elements").slideUp(200);
    $("#search_overlay").css({'height': '0px', 'opacity': 0});
    $("#more_options").button('option', 'label', 'Show search options');
    setTimeout(searchFormOverlap, 200);
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



///////////////////////////////////////////////////
////// Functions shared by various reports ////////
///////////////////////////////////////////////////


// Show more context in concordance and concordance from collocation searches
function fetchMoreContext() {
    var db_url = webConfig['db_url'];
    var q_string = window.location.search.substr(1);
    var script = db_url + '/scripts/get_more_context.py?' + q_string;
    $.getJSON(script, function(data) {
        for (var i=0; i < data.length; i++) {
            var more = '<div class="more_length" style="display:none;"' + data[i] + '</div>';
            $('.philologic_context').eq(i).append(more);
        }
        moreContext();
        $('.more_context').animate({color: '#555 !important'},400);
    });
}

function moreContext() {
    $(".more_context").click(function() {
        var context_link = $(this).text();
        var more_context = $(this);
        var parent_div = $(this).parents().siblings('.philologic_context')
        if (context_link == 'More') {
            parent_div.children('.default_length').fadeOut(100, function() {
                parent_div.children('.more_length').fadeIn(100);
            });
            parent_div.prev('div').find('.ui-button-text').empty().fadeIn(100).append('Less');
        } else {
            parent_div.children('.more_length').fadeOut(100, function() {
                parent_div.children('.default_length').show();
            });
            parent_div.prev('div').find('.ui-button-text').empty().fadeIn(100).append('More');
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


// This is to create links for collocations
function colloc_linker(word, q_string, direction, num) {
    q_string = q_string.replace(/report=[^&]+/, 'report=concordance_from_collocation');
    q_string += '&collocate=' + encodeURIComponent(word);
    q_string += '&direction=' + direction;
    q_string += '&collocate_num=' + num;
    return q_string
}