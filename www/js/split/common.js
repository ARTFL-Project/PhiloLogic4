"use strict";

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
    
    // Show search form on click
    $('#show-search-form').click(function() {
        $('#search_elements').css('z-index', 150);
        if ($(this).data('display') == "none") {
            showMoreOptions("all");
            $(this).data('display', 'block');
            $('#show-search-form').html('Hide search options');
        } else {
            hideSearchForm();
            $(this).data('display', 'none');
            $('#show-search-form').html('Show search options');
        }
    });
    
    $('#show-search-form').show();
    showHide($('input[name=report]:checked', '#search').val());
    
    // Handler for clicks on report tabs
    $('#report label').click(function() {
        var report = $(this).find('input').attr('id');
        if ($("#search_elements").css('display') != 'none') {
            showHide(report);
            if (report != "frequencies") {
                $("#search_elements")
                    .velocity("fadeIn",
                               {duration: 250, 'easing': 'easeIn'}
                               );
            }
            showMoreOptions();
        } else {
            $("#show-search-form").data('display', 'block');
            $('#show-search-form').html('Hide search options');
            showHide(report);
            if (report != "frequencies") {
                $("#search_elements")
                .velocity("slideDown",{duration: 250, 'easing': 'easeIn'});
            }
            showMoreOptions();
        }
    });
    
    // Close search form when clicking outside it
    $("#search_overlay, #header, #footer").click(function(e) {
        e.stopPropagation();
        $('#show-search-form').data('display', 'none');
        $('#show-search-form').html('Show search options');
        hideSearchForm();
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
                $('#report input').removeAttr('checked');
                $('#report label').removeClass('active');
                $('#' + value).prop('checked', true);
                $('#' + value).parent().addClass('active');
            } else if (key == "method") {
                $('#method-buttons input').removeAttr('checked');
                $('#method-buttons label').removeClass('active');
                $('#method-buttons input[name=method][value=' + value + ']').prop('checked', true);
                $('#method-buttons input[name=method][value=' + value + ']').parent().addClass('active');
            } else if (key =='pagenum') {
                $('#page_num input').removeAttr('checked');
                $('#page_num label').removeClass('active');
                $('#page_num input[name=pagenum][value=' + value + ']').prop('checked', true);
                $('#page_num input[name=pagenum][value=' + value + ']').parent().addClass('active');
            }
            else if (key == 'year_interval') {
                $('#year_interval input').removeAttr('checked');
                $('#year_interval label').removeClass('active');
                $('#year_interval input[name=year_interval][value=' + value + ']').prop('checked', true);
                $('#year_interval input[name=year_interval][value=' + value + ']').parent().addClass('active');
            }
            else if (key == 'field') {
                $('select[name=' + key + ']').val(value);
            }
            else if (key == "q") {
                console.log(value)
                $('#q').val(value);
                $('#q2').val(value);
            }
            else {
                $('#' + key).val(value);
            }
        }
    }
    
    //  Clear search form
    $("#reset_form").click(function() {
        $('#form_body input').removeAttr('checked');
        $('#form_body .btn').removeClass('active');
        $('#report input:first, #method-buttons input:first, #page_num input:first, #year_interval input:first').prop('checked', true);
        $('#report input:first, #method-buttons input:first, #page_num input:first, #year_interval input:first').parent().addClass('active');
        showHide($('#report input:first').attr('id'));
    });
    
    //  This is to select the right option when clicking on the input box  
    $("#arg_proxy").focus(function() {
        $("#arg_phrase").val('');
        $('#method-buttons input').removeAttr('checked');
        $('#method-buttons label').removeClass('active');
        $('#method-buttons input[name=method][value=proxy]').prop('checked', true);
        $('#method-buttons input[name=method][value=proxy]').parent().addClass('active');
    });
    $("#arg_phrase").focus(function() {
        $("#arg_proxy").val('');
        $('#method-buttons input').removeAttr('checked');
        $('#method-buttons label').removeClass('active');
        $('#method-buttons input[name=method][value=phrase]').prop('checked', true);
        $('#method-buttons input[name=method][value=phrase]').parent().addClass('active');
    });
    $('#method3').parent().click(function() {
        $("#arg_proxy, #arg_phrase").val('');
    });
    
    
    metadataRemove();
    
    
    // Catch Enter keypress when focused on fixed search bar input
    $("#q2").keyup(function(e) {
        e.preventDefault();
        if (e.keyCode == 13) {
            $('#button-search2').trigger('click');
        }
    });
    // Trigger form submit using value from fixed search bar
    $('#button-search2').click(function() {
        $('#q').val($("#q2").val());
        $("#search").trigger('submit');
    });
    
    // Add spinner to indicate that a query is running in the background
    // and close autocomplete
    $('#search').submit(function(e) {
        $('.ui-autocomplete').remove();
        var width = $(window).width() / 2 - 100;
        hideSearchForm();
        $("#waiting").css("margin-left", width).css('margin-top', 100).show();
        var new_q_string = $(this).serialize();
        // Set a timeout in case the browser hangs: redirect to no hits after 10 seconds
        setTimeout(function() {
            e.preventDefault();
            $("#waiting").fadeOut();
            var selected_report = $('#report').find('input:checked').attr('id');
            window.location = "?" + new_q_string.replace(/report=[^&]*/, 'report=error') + "&error_report=" + selected_report;
        }, 10000);
    });
    
    // Fixed search bar only in KWIC, concordance and collocation reports //
    if (global_report == "concordance" || global_report == "kwic" || global_report == "collocation") {
        $('#fixed-search').affix({
            offset: {
            top: function() {
                return (this.top = $('#description').offset().top)
                },
            bottom: function() {
                return (this.bottom = $('#footer').outerHeight(true))
              }
            }
        });
        $('#fixed-search').on('affix.bs.affix', function() {
            $(this).addClass('fixed');
            $(this).css({'opacity': 1, "pointer-events": "auto"});
        });
        $('#fixed-search').on('affixed-top.bs.affix', function() {
            $(this).css({'opacity': 0, "pointer-events": "none"});
            setTimeout(function() {
               $(this).removeClass('fixed'); 
            });
        });
        $("#back-to-full-search").click(function() {
            $("body").velocity('scroll', {duration: 800, easing: 'easeOutCirc', offset: 0});
            setTimeout(function() {
                showMoreOptions("all");
                $("#show-search-form").data('display', 'block');
                $('#show-search-form').html('Hide search options');
            }, 800);            
        });
        $("#top-of-page").click(function() {
            $("body").velocity('scroll', {duration: 800, easing: 'easeOutCirc', offset: 0});
        });
    }
    
    // Keep footer at bottom and make sure content doesn't overlap footer
    //setTimeout(searchFormOverlap, 400); // delay to give time for the full height of the search form to be generated
    $(window).resize(function() {
        searchFormOverlap(); 
    });
    
});

function searchFormOverlap() {
    var form_offset = $('#form_body').offset().top + $('#form_body').height();
    var footer_offset = $('#footer').offset().top;
    if (form_offset > footer_offset) {
        $('#footer').css('top', form_offset + 20);
    } else {
        $('#footer').css('top', 'auto');
    }
}

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


function autoCompleteWord(db_url) {
    $("#q").autocomplete({
        source: db_url + "/scripts/term_list.py",
        minLength: 2,
        "dataType": "json",
        focus: function( event, ui ) {
            var q = ui.item.label.replace(/<\/?span[^>]*?>/g, '');
            //$("#" + field).val(q); This is too sensitive, so disabled
            return false;
        },
        select: function( event, ui ) {
            var q = ui.item.label.replace(/<\/?span[^>]*?>/g, '');
            $("#q").val(q);
            return false;
        }
    }).data("ui-autocomplete")._renderItem = function (ul, item) {
        var term = item.label.replace(/^[^<]*/g, '');
        return $("<li></li>")
            .data("item.autocomplete", item)
            .append("<a>" + term + "</a>")
            .appendTo(ul);
    };
    $("#q2").autocomplete({
        source: db_url + "/scripts/term_list.py",
        minLength: 2,
        "dataType": "json",
        focus: function( event, ui ) {
            var q = ui.item.label.replace(/<\/?span[^>]*?>/g, '');
            //$("#" + field).val(q); This is too sensitive, so disabled
            return false;
        },
        select: function( event, ui ) {
            var q = ui.item.label.replace(/<\/?span[^>]*?>/g, '');
            $("#q2").val(q);
            return false;
        }
    }).data("ui-autocomplete")._renderItem = function (ul, item) {
        var term = item.label.replace(/^[^<]*/g, '');
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
            var q = ui.item.label.replace(/<\/?span[^>]*?>/g, '');
            q = q.replace(/ CUTHERE /, ' ');
            //$("#" + field).val(q); This is too sensitive, so disabled
            return false;
        },
        select: function( event, ui ) {
            var q = ui.item.label.replace(/<\/?span[^>]*?>/g, '');
            q = q.split('|');
            q[q.length - 1] = q[q.length - 1].replace(/.*CUTHERE /, '');
            q[q.length-1] = '\"' + q[q.length-1].replace(/^\s*/g, '') + '\"'; 
            q = q.join('|').replace(/""/g, '"');
            $("#" + field).val(q);
            return false;
        }
    }).data("ui-autocomplete")._renderItem = function (ul, item) {
        var term = item.label.replace(/.*(?=CUTHERE)CUTHERE /, '');
        return $("<li></li>")
            .data("item.autocomplete", item)
            .append("<a>" + term + "</a>")
            .appendTo(ul);
     };
}

// Display different search parameters based on the type of report used
function showHide(value) {
    $("#results_per_page, #collocation_num, #time_series_num, #date_range, #method, #metadata_fields").hide();
    if (value == 'collocation') {
        $("#collocation_num, #metadata_fields").show();
        $('#metadata_fields').find('tr').has('#date').show();
    }
    if (value == 'kwic' || value == "concordance" || value == "bibliography") {
        console.log(value)
        $("#results_per_page, #method, #metadata_fields").show();
        $('#metadata_fields').find('tr').has('#date').show();
        $('#start_date, #end_date').val('');
    }
    if (value == 'relevance') {
        $("#results_per_page").show();
    }
    if (value == "time_series") {
        $("#time_series_num, #date_range, #method, #metadata_fields").show();
        $('#metadata_fields').find('tr').has('#date').hide();
        $('#date').val('');
    }
    if (value == "frequencies") {
        $('#search_terms_container, #method, #results_per_page').hide();
        $('#metadata_fields').show();   
    }
}

//  Function to show or hide search options
function showMoreOptions(display) {
    var height = $("#wrapper").height() - 50;
    if (display == "all") {
        var report = $('#report label.active input').attr('id') || global_report;
        showHide(report);
        $("#search_elements").velocity("slideDown",{duration: 250, 'easing': 'easeIn'});
        
    }
    if (global_report != "landing_page") {
        setTimeout(function() {$("#search_overlay").css({'top': '50px', 'opacity': 0.2, 'height': height})}, 250);
    }
    setTimeout(searchFormOverlap, 250);
}

function hideSearchForm() {
    $("#search_elements").velocity('slideUp', {duration: 250, easing: 'easeOut'});
    setTimeout(function() {
        $("#search_overlay").css({'opacity': 0});
    }, 300);
    setTimeout(function() {
        $("#search_overlay").css('height', '0px');
    }, 500);
    setTimeout(searchFormOverlap, 250);
}


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
        $('.more_context').removeAttr('disabled');
    });
}

function moreContext() {
    $(".more_context").click(function() {
        var context_link = $(this).text();
        var parent_div = $(this).parents().siblings('.philologic_context')
        if ($(this).data('context') == 'short') {
            parent_div.children('.default_length').fadeOut(100, function() {
                parent_div.children('.more_length').fadeIn(100);
            });
            $(this).empty().fadeIn(100).append('Less');
            $(this).data('context', 'long');
        } else {
            parent_div.children('.more_length').fadeOut(100, function() {
                parent_div.children('.default_length').show();
            });
            $(this).empty().fadeIn(100).append('More');
            $(this).data('context', 'short');
        }
    });
}

// This is to create links for collocations
function colloc_linker(word, q_string, direction, num) {
    q_string = q_string.replace(/report=[^&]+/, 'report=concordance_from_collocation');
    q_string += '&collocate=' + encodeURIComponent(word);
    q_string += '&direction=' + direction;
    q_string += '&collocate_num=' + num;
    return q_string
}

// Delay function calls in repeated actions:
// used in Time Series to redraw chart after resize
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

// Custom HTML replace function for text objects since jQuery's html is too slow:
// See here: https://groups.google.com/forum/#!msg/jquery-en/RG_dJD8DlSc/R4pDTgtzU4MJ
$.fn.replaceHtml = function( html ) {
    var stack = [];
    return this.each( function(i, el) {
        var oldEl = el;
        var newEl = oldEl.cloneNode(false);
        newEl.innerHTML = html;
        try {
            oldEl.parentNode.replaceChild(newEl, oldEl);   
        } catch(e) {}
        /* Since we just removed the old element from the DOM, return a reference
        to the new element, which can be used to restore variable references. */
        stack.push( newEl );
    }).pushStack( stack );
};