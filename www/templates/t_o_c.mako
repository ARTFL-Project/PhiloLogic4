<%include file="header.mako"/>
<%include file="search_form.mako"/>
<div id='philologic_response' class="container-fluid">
    <div class="row" id="toc-report-title">
        <div class="col-xs-offset-2 col-xs-8">
            <span class='philologic_cite'>${f.biblio_citation(db,config, obj)}</span>
        </div>
    </div>
    <div class="panel panel-default">
        % if db.locals['debug'] == True:
            <button id="show-header" class="btn btn-primary">Show Header</button>
            <div id="tei-header" style="white-space: pre; font-family: 'Droid Sans Mono', sans-serif; font-size: 80%; display: none;"></div>
        % endif
        <div id="toc-report" data-script="${config.db_url + '/scripts/get_table_of_contents.py?philo_id='}">
            <div id="toc-content"></div>
        </div>
    </div>
</div>
<%include file="footer.mako"/>