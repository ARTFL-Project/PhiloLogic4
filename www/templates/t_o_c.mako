<%include file="header.mako"/>
<%include file="search_form.mako"/>
<div id='philologic_response' class="container-fluid">
    <div id='toc-title'>
        <span class='philologic_cite'>${f.biblio_citation(db,config, obj)}</span>
    </div>
    <div class="panel panel-default">
        % if db.locals['debug'] == True:
            <button id="show-header" class="btn btn-primary">Show Header</button>
            <div id="tei-header" style="white-space: pre; font-family: 'Droid Sans Mono', sans-serif; font-size: 80%; display: none;"></div>
        % endif
        <div id="toc-report">
            <div id="toc-content"></div>
        </div>
    </div>
</div>
<%include file="footer.mako"/>