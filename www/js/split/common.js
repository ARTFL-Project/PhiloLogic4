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
    
    // Close search form when clicking outside it
    $("#search_overlay, #header, #footer").click(function(e) {
        e.stopPropagation();
        $('#show-search-form').data('display', 'none');
        $('#show-search-form').html('Show search options');
        hideSearchForm();
    });
    
    // Set-up autocomplete for words and metadata
    autoCompleteWord(db_url);
    for (var i=0; i < webConfig.metadata.length; i++) {
        var  metadata = $("#" + webConfig.metadata[i]).val();
        var field = webConfig.metadata[i];
        autoCompleteMetadata(metadata, field, db_url);
    }
    
    
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
                var report = $('#report label.active input').attr('id');
                displayReportOptions(report);
                showMoreOptions();
                $("#show-search-form").data('display', 'block');
                $('#show-search-form').html('Hide search options');
            }, 800);            
        });
        $("#top-of-page").click(function() {
            $("body").velocity('scroll', {duration: 800, easing: 'easeOutCirc', offset: 0});
        });
    }
    
    // Export results handler
    $('#export-buttons button').click(function() {
        if (global_report == 'time_series') {
            var data = sessionStorage[window.location.href];
            var data = "text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(data));
            $('<a href="data:' + data + '" download="time_series.json">Download JSON file</a>').appendTo('#export-download-link');
            $("#export-download-link").velocity('slideDown');
        } else {
            var script = window.location.href + "&format=" + $(this).data('format');
            $.getJSON(script, function(data) {
                data = "text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(data));
                $('#export-download-link a').attr('href', 'data:' + data).attr('download', global_report + '.json');
                //$('<a href="data:' + data + '" download="' + global_report + '.json">Download JSON file</a>').appendTo('#export-download-link');
                $("#export-download-link").velocity('slideDown');
            });
        }
    });
    
});

function autoCompleteWord(db_url) {
    $("#q").autocomplete({
        source: $('#q').data('script'),
        minLength: 2,
        "dataType": "json",
        focus: function( event, ui ) {
            var q = ui.item.label.replace(/<\/?span[^>]*?>/g, '');
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
            .append(term)
            .appendTo(ul);
    };
    $("#q2").autocomplete({
        source: $('#q').data('script'),
        minLength: 2,
        "dataType": "json",
        focus: function( event, ui ) {
            var q = ui.item.label.replace(/<\/?span[^>]*?>/g, '');
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
            .append(term)
            .appendTo(ul);
    };
}

function autoCompleteMetadata(metadata, field, db_url) {
    $("#" + field).autocomplete({
        source: $("#metadata_fields").data('script') + field,
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
            .append(term)
            .appendTo(ul);
     };
}

///////////////////////////////////////////////////
////// Functions shared by various reports ////////
///////////////////////////////////////////////////

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