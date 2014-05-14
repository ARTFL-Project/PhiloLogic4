<%include file="header.mako"/>
<%include file="search_form.mako"/>
<script>
    $(document).ready(function() {
        var new_margin = parseInt($('#philologic_response').css("margin-top")) + 10;
        $('#philologic_response').css("margin-top", new_margin + "px");
        var pathname = window.location.pathname.replace('dispatcher.py/', '');
        var my_path = pathname.replace(/\/\d+.*$/, '/');
        var doc_id = pathname.replace(my_path, '').replace(/(\d+)\/*.*/, '$1');
        var philo_id = doc_id + ' 0 0 0 0 0 0'
        var script = my_path + '/scripts/get_table_of_contents.py?philo_id=' + philo_id;
        $.get(script, function(data) {
            toc_container = '<div id="toc_wrapper" style="display:none">' + data + "</div>";
            $('#philologic_response').append(toc_container);
            $("#toc_wrapper").fadeIn();
        });
        $('#show_header').button();
        $('#show_header').click(function() {
            if ($('#show_header span').text() == "Show Header") {
                $.get(my_path + '/scripts/get_header.py?philo_id=' + philo_id, function(data) {
                    $('#tei_header').append(data).show();
                    $('#show_header span').html("Hide Header");                
                });
            } else {
                $('#tei_header').hide().empty();
                $('#show_header span').html("Show Header");
            }
        });
    })
</script>
<div id='philologic_response'>
    <div id='t_o_c_title'>
        <span class='philologic_cite'>${f.biblio_citation(db,config, obj)}</span>
    </div>
    % if db.locals['debug'] == True:
        <button id="show_header">Show Header</button>
        <div id="tei_header" style="white-space: pre; font-family: 'Droid Sans Mono', sans-serif; font-size: 80%; display: none;"></div>
    % endif
</div>
<%include file="footer.mako"/>