<%include file="header.mako"/>
<%include file="search_form.mako"/>
<script>
    $(document).ready(function() {
        var pathname = window.location.pathname.replace('dispatcher.py/', '');
        var my_path = pathname.replace(/\/\d+.*$/, '/');
        var doc_id = pathname.replace(my_path, '').replace(/(\d+)\/*.*/, '$1');
        var philo_id = doc_id + ' 0 0 0 0 0 0'
        var script = my_path + '/scripts/get_table_of_contents.py?philo_id=' + philo_id;
        $.get(script, function(data) {
            $('#philologic_response').append(data);
        });
    })
</script>
<div id='philologic_response'>
    <div class='t_o_c_title'>
        <span class='philologic_cite'>${f.cite.make_abs_doc_cite(db,obj)}</span>
    </div>
</div>
<%include file="footer.mako"/>