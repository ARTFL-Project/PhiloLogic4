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
        spin: function( event, ui ) {
            if ( ui.value > 20 ) {
                $( this ).spinner( "value", 1 );
                return false;
            } else if ( ui.value < 1 ) {
                $( this ).spinner( "value", 20 );
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
    
    monkeyPatchAutocomplete();    
    $("#q").autocomplete({
        source: db_url + "/scripts/term_list.py",
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
    ///////// Concordance / KWIC switcher //////////////////////////////////////
    ////////////////////////////////////////////////////////////////////////////
    if ($("#report_switch").length) {
        concordance_kwic_switch(db_url);
        more_context();
        if ($('.kwic_concordance').length) {
            var config = {    
                    over: showBiblio, 
                    timeout: 100,  
                    out: hideBiblio   
                };
            $(".kwic_biblio").hoverIntent(config);
        }
    }
    ////////////////////////////////////////////////////////////////////////////

    if ($(".colloc_concordance")) {
        more_context();
    }
    
    ////////////////////////////////////////////////////////////////////////////
    ///////// Frequency / Frequency per 10,000 switcher ////////////////////////
    ////////////////////////////////////////////////////////////////////////////
    if ($('.philologic_frequency_report').length) {
        frequency_switcher(db_url);
    }
    ////////////////////////////////////////////////////////////////////////////
    
    
    ////////////////////////////////////////////////////////////////////////////
    // This will display the sidebar for various frequency reports /////////////
    ////////////////////////////////////////////////////////////////////////////
    sidebar_reports(q_string, db_url, pathname);
    ////////////////////////////////////////////////////////////////////////////
    
    
    ////////////////////////////////////////////////////////////////////////////
    // Page and reader code ////////////////////////////////////////////////////
    ////////////////////////////////////////////////////////////////////////////
    // Change pages
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
    if ($('.next_obj').length) {
        retrieve_obj(db_url);
        t_o_c_handler(db_url);
        follow_scroll($('.prev_and_toc'), $('.next_and_read'));
        $(window).load(function() {
            scroll_to_highlight();
        });
    } else if ($('.next_page').length) {
        retrieve_page(db_url);
        t_o_c_handler(db_url);
        follow_scroll($('.prev_and_toc'), $('.next_and_read'));
        scroll_to_highlight();
    }
    
    
    // Toggle reading mode
    if ($('.book_page').length) {
        display_overlay();
        page_image_link();
    }
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


function scroll_to_highlight() {
    var word_offset = $('.highlight').offset().top;
    $("html, body").animate({ scrollTop: word_offset }, 'slow');
}

function page_image_link() {
    $('.page_image_link').click(function(e) {
        e.preventDefault();
        var href = $(this).attr('href');
        var image = $("<img />").attr('src', href).load(function() {
            var div = '<div class="image_container" style="display: none;"></div>'
            $('.page_display').prepend(div);
            var close_div = '<div id="close_page_image" class="ui-icon ui-icon-circle-close close_page_image"></div>'
            $('.image_container').append(close_div)
            $("body").append("<div id='overlay' style='display:none;'></div>");
            var header_height = $('#header').height();
            var footer_height = $('#footer').height();
            var overlay_height = $(document).height() - header_height - footer_height;
            $("#overlay")
            .height(overlay_height)
            .css({
               'opacity' : 0.3,
               'position': 'absolute',
               'top': 0,
               'left': 0,
               'background-color': 'white',
               'width': '100%',
               'margin-top': header_height,
               'z-index': 90
             });
            $("html, body").animate({ scrollTop: 140 }, "slow");
            $('.image_container').append(image);
            $('.image_container, #overlay').fadeIn('fast');
            var image_height = $('.image_container').offset().top + $('.image_container').height();
            image_height = image_height + parseInt($('.image_container').css('border-top-width')) + parseInt($('.image_container').css('border-bottom-width'));
            var original_footer_offset = $('#footer').offset().top;
            if (image_height > $('#footer').offset().top) {
                $('#footer').offset({top: image_height});
            }
            $("#close_page_image, #overlay").click(function() {
                $('.image_container, #overlay').fadeOut('fast', function() {
                    $('#overlay').remove();
                    $('.image_container').remove();
                    if ($('#footer').offset().top > original_footer_offset) {
                        $("html, body").animate({ scrollTop: 0 }, function() {
                            $('#footer').animate({top: original_footer_offset});
                        });
                    }
                });
            });
        });
    });
}

// Display overlay to enable a reading mode //
function display_overlay() {
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
            $(".read_button, .next_obj").css('z-index', 100).css('position', 'relative');
            $('.next_and_read').css('z-index', 100);
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
}

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

/// Go to next or previous object in text display
function retrieve_obj(db_url){
    $(".prev_obj, .next_obj").on('click', function() {
        var my_path = db_url.replace(/\/\d+.*$/, '/');
        var philo_id = $(this).attr('id');
        var script = my_path + '/scripts/go_to_obj.py?philo_id=' + philo_id;
        $.getJSON(script, function(data) {
            var scrollto_id = '#' + $(".obj_text").attr('id');
            $('#toc_container').find($(scrollto_id)).attr('style', 'color: #800000;');
            $('.obj_text').fadeOut('fast', function() {
                $(this).html(data['text']).fadeIn('fast');
                $('#footer').css('top', '');
                $('.obj_text').attr("id", philo_id.replace(/ /g, '_'));
                $('.prev_obj').attr('id', data['prev']);
                $('.next_obj').attr('id', data["next"]);
                $("html, body").animate({ scrollTop: 0 }, "fast");
                var scrollto_id = '#' + $(".obj_text").attr('id');
                if ($('#toc_container').find($(scrollto_id)).length) {
                    $('#toc_container').scrollTo($(scrollto_id), 500);
                    $('#toc_container').find($(scrollto_id)).attr('style', 'color: black; font-weight: 700 !important;');
                }
                page_image_link();
                var new_url = my_path + '/dispatcher.py/' + philo_id.replace(/ /g, '/');
                History.pushState(null, '', new_url);
            });
        });
    });
}
function retrieve_page(db_url) {
    $(".prev_page, .next_page").on('click', function() {
        var my_path = db_url.replace(/(\/\d+)+$/, '/');
        var doc_id = db_url.replace(my_path, '').replace(/(\d+)\/*.*/, '$1');
        var page = $(".book_page").attr('id');
        var go_to_page = $(this).attr('id');
        var myscript = my_path + "/scripts/go_to_page.py?philo_id=" + doc_id + "&go_to_page=" + go_to_page + "&doc_page=" + page;
        $.getJSON(myscript, function(data) {
            $(".book_page").attr('id', data[2]);
            $('.obj_text').fadeOut('fast', function () {
                $(this).html(data[3]).fadeIn('fast');
                $('#footer').css('top', '');
                $(".prev_page").attr("id", data[0]);
                $('.next_page').attr('id', data[1]);
                page_image_link();
                var new_url = my_path + '/dispatcher.py/' + philo_id.replace(/ /g, '/');
                History.pushState(null, '', new_url);
            }); 
        });
        
    });
}

/// Switch betwwen concordance and KWIC reports
function concordance_kwic_switch(db_url) {
    $("#report_switch").on("change", function() {
        $('.highlight_options').remove();
        var switchto = $('input[name=report_switch]:checked').val();
        var width = $(window).width() / 3;
        $("#waiting").css("margin-left", width).show();
        $("#waiting").css("margin-top", 200).show();
        $.get(db_url + "/reports/concordance_switcher.py" + switchto, function(data) {
            $("#results_container").hide().empty().html(data).fadeIn('fast');
            $("#waiting").hide();
            if (switchto.match(/kwic/)) {
                var config = {    
                    over: showBiblio, 
                    timeout: 100,  
                    out: hideBiblio   
                };
                $(".kwic_biblio").hoverIntent(config);
                $('#concordance').removeAttr("checked");
                $('#kwic').prop("checked", true)
                var new_url = History.getState().url.replace(/report=concordance/, 'report=kwic');
                History.pushState(null, '', new_url);
            }
            else {
                $('#kwic').removeAttr("checked");
                $('#concordance').prop("checked", true);
                var new_url = History.getState().url.replace(/report=kwic/, 'report=concordance');
                History.pushState(null, '', new_url);
            }
            $("#report").buttonset("refresh");
            display_options_on_selected();
            more_context();
            $('.more').find('a').each(function() {
                if (switchto.match(/kwic/)) {
                    var new_href = $(this).attr('href').replace('concordance', 'kwic');
                }
                else {
                    var new_href = $(this).attr('href').replace('kwic', 'concordance');
                }
                $(this).attr('href', new_href);
            });
        });
    });
}

/// Have previous and next links follow scroll in page and object navigation ///
function t_o_c_handler(db_url) {
    var pathname = window.location.pathname.replace('dispatcher.py/', '');
    var text_position = $('.book_page').offset().left + 20;
    var position = $('#toc_container').offset().top;
    var bottomPosition = $(window).height();
    var footer_pos = $("#footer").offset().top - 30;
    if (bottomPosition < footer_pos) {
        var max_height = bottomPosition - position;
    } else {
        var max_height = footer_pos - position;
    }
    $('#toc_container').css('max-height', max_height);
    $('#toc_container').css('width', text_position);
    var my_path = pathname.replace(/\/\d+.*$/, '/');
    var doc_id = pathname.replace(my_path, '').replace(/(\d+)\/*.*/, '$1');
    var philo_id = doc_id + ' 0 0 0 0 0 0'
    console.log(my_path, doc_id, philo_id)
    var script = my_path + '/scripts/get_table_of_contents.py?philo_id=' + philo_id;
    $('#t_b_c_box').attr('style', 'color: LightGray;');
    $.get(script, function(data) {
        $('#toc_container').css('position', 'absolute');
        $('#toc_container').hide().css('margin-left', '-700px').html(data).show();
        $('#t_b_c_box').animate({color: '#555 !important'},400, function() {
            $("#show_table_of_contents").click(function() {
                show_hide_toc(text_position);
            });
        });
    });
}
function follow_scroll(prev, next) {
    var top = next.offset().top - parseFloat(next.css('marginTop').replace(/auto/, 0));
    $(window).scroll(function (event) {
      // what the y position of the scroll is
        var y = $(this).scrollTop();
      
        // whether that's below the form
        if (y >= top) {
            // if so, ad the fixed class
            next.addClass('fixed');
            prev.addClass('fixed');
        } else {
            // otherwise remove it
            prev.removeClass('fixed');
            next.removeClass('fixed');
        }
        var position = $('#toc_container').offset().top;
        var toc_header_height = $(".prev_and_toc").height() + parseInt($(".prev_and_toc").css("margin-top")) + parseInt($("#toc_container").css("margin-top"));
        var other_content = $(".prev_obj_wrapper").position().top - window.pageYOffset;
        if (other_content > 0) { toc_header_height += other_content; }
        var maxPossibleHeight = $(window).height() - toc_header_height;
        var bottomPosition = $(window).height() + window.pageYOffset;
        var footer_pos = $("#footer").offset().top;        
        var footer_offset = 0;
        if (bottomPosition > footer_pos) {
            footer_offset = bottomPosition - footer_pos;            
        }
        var max_height = maxPossibleHeight - footer_offset;
        $('#toc_container').css('max-height', max_height);
    });
}
function show_hide_toc(top_right) {
    var position = top_right - ($('#toc_container').width() - $('.table_of_contents').width()) - 15;
    var scrollto_id = '#' + $(".obj_text").attr('id');
    if ($("#t_b_c_box").text() == "Show table of contents") {
        $("#t_b_c_box").html("Hide table of contents");
        $('#toc_container').animate({
            'margin-left': '-30px'
            }, 450
            );
        $('#toc_container').scrollTo($(scrollto_id), 500);
        $('#toc_container').find($(scrollto_id)).attr('style', 'color: black;');
    } else {
        $("#t_b_c_box").html("Show table of contents");
        $('#toc_container').animate({
                'margin-left': '-700px'
        }, 450);
        $('#show_table_of_contents').button('refresh');
    }
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
function autocomplete_metadata(metadata, field, db_url) {
    $("#" + field).autocomplete({
        source: db_url + "/scripts/metadata_list.py?field=" + field,
        minLength: 2,
        dataType: "json"
    });
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
    console.log(script_call)
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

function update_colloc(db_url, all_colloc, left_colloc, right_colloc, results_len, colloc_start, colloc_end) {
    var q_string = window.location.search.substr(1);
    var script = db_url + "/scripts/collocation_fetcher.py?" + q_string
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
            update_colloc(db_url, all_new_colloc, left_colloc, right_colloc, results_len, colloc_start, colloc_end);
            collocation_cloud();
            var total = $('#progress_bar').progressbar("option", "max");
            var percent = colloc_end / total * 100;
            if (colloc_end < total) {
                $('#progress_bar').progressbar({value: colloc_end});
                $('.progress-label').text(percent.toString().split('.')[0] + '%');
            }
        }));
    }
    else {
        var total = $('#progress_bar').progressbar("option", "max");
        $('#progress_bar').progressbar({value: total});
        $('.progress-label').text('Complete!');
        $("#progress_bar").delay(500).fadeOut('slow');
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
    $("#collocate_counts").fadeIn('fast');
}

// SHow more context in concordance searches
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