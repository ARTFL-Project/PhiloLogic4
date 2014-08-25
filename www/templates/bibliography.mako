<%include file="header.mako"/>
<%include file="search_form.mako"/>
<div class="container-fluid" id='philologic_response'>
    <div id='initial_report'>
        <div id='description'>
        <%
        start, end, n = f.link.page_interval(results_per_page, results, q["start"], q["end"])
        r_status = "."
        if not results.done:
           r_status += " Still working.  Refresh for a more accurate count of the results."
        %>
        <div id="search_arguments">
                Bibliographic criteria: ${biblio_criteria or "<b>None</b>"}<br>
        </div>
        Hits <span class="start">${start}</span> - <span class="end">${end}</span> of <span id="total_results">${len(results)}</span>${r_status}
        </div>
    </div>
    <div class="row" id="act-on-report">
        <div class="col-xs-12">
            <div class="btn-group pull-right">
                <button type="button" class="btn btn-primary dropdown-toggle" data-toggle="dropdown">
                    Display frequency by
                    <span id="selected-sidebar-option" data-selected="${config['facets'][0]}">${config["metadata_aliases"][config["facets"][0]].title()}</span>
                    <span class="caret"></span>
                </button>
                <ul class="dropdown-menu" role="menu" id="frequency_field">
                    % for facet in config["facets"]:
                        <%
                        if facet in config["metadata_aliases"]:
                            alias = config["metadata_aliases"][facet]
                        else:
                            alias = facet
                        %>
                        <li><a class="sidebar-option" id="side_opt_${facet}" data-value='${facet}' data-display='${facet}'>Display frequency by ${alias}</a></li>
                    % endfor
                    % if report != 'bibliography':
                        <li class="divider"></li>
                        <li><a class="sidebar-option" id="side_opt_collocate" data-value='collocation_report' data-display='collocate'>Display collocates</a></li>
                    % endif
                </ul>
                <button type="button" id="hide-sidebar-button" class="btn btn-primary" style="display: none";>
                    <span class="glyphicon glyphicon-remove-circle" style="vertical-align: text-top"></span>
                </button>
            </div>
        </div>
    </div>
    <div class="row">
        <div id='results_container' class="col-xs-12">
            <ol class="panel panel-default bibliographic-results">
                % for i in results[start-1:end]:
                    <li class='biblio-occurrence panel panel-default'>
                        <%
                        n += 1
                        %>
                        <span style="padding-left: 5px;">${n}.</span>
                        ##<input type="checkbox" name="philo_id" value="${i.philo_id}">
                        % if i.type == 'doc':
                            <span class='philologic_cite'>${f.biblio_citation(db, config, i)}</span>
                        % else:
                            <span class='philologic_cite'>${f.concordance_citation(db, config, i)}</span>
                        % endif
                    </li>
                % endfor
            </ol>
        </div>
        <%include file="show_frequency.mako"/>
   </div>
   <div class="more">
        <%include file="results_paging.mako" args="start=start,results_per_page=results_per_page,q=q,results=results"/> 
        <div style='clear:both;'></div>
    </div>
</div>
<%include file="footer.mako"/>
