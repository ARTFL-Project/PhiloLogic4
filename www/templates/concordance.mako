<%include file="header.mako"/>
<%include file="search_form.mako"/>
<div class="container-fluid" id='philologic_response'>
    <div id='initial_report'>
       <div id='description'>
            <%
             start, end, n = f.link.page_interval(results_per_page, results, q["start"], q["end"])
             r_status = "."
             if not results.done:
                r_status += " Still working..."
            %>
            <div id="search_arguments">
                Searching database for <b>${q['q'].decode('utf-8', 'ignore')}</b><br>
                Bibliographic criteria: ${biblio_criteria or "<b>None</b>"}
            </div>
            % if end != 0:
                % if end < results_per_page or end < len(results):
                    Hits <span id="start">${start}</span> - <span id="end">${end}</span> of <span id="total_results">${len(results) or results_per_page}</span><span id="incomplete">${r_status}</span>
                % else:
                    Hits <span id="start">${start}</span> - <span id="end">${len(results) or end}</span> of <span id="total_results">${len(results) or results_per_page}</span><span id="incomplete">${r_status}</span>         
                % endif
            % else:
                No results for your query.
            % endif
       </div>
    </div>
    <div class="row hidden-xs" id="act-on-report">
        <div class="col-sm-9 col-md-8 col-lg-6">
            <div id="report_switch" class="btn-group" data-toggle="buttons">
                <label class="btn btn-primary active">
                    <input type="radio" name="report_switch" id="concordance_switch" value="?${q['q_string'].replace('report=kwic', 'report=concordance')}" checked>
                    View occurences with context
                </label>
                <label class="btn btn-primary">
                    <input type="radio" name="report_switch" id="kwic_switch" value="?${q['q_string'].replace('report=concordance', 'report=kwic')}">
                    View occurences line by line (KWIC)
                </label>
            </div>
        </div>
        <div class="col-sm-3 col-md-4 col-lg-4 col-lg-offset-2" id="right-act-on-report">
            <div class="btn-group pull-right">
                <button type="button" class="btn btn-primary dropdown-toggle" data-toggle="dropdown">
                    Display frequency by
                    <span id="selected-sidebar-option" data-selected="${config['facets'][0]}">
                        <%
                        try:
                            default_value = config["metadata_aliases"][config["facets"][0]].title()
                        except KeyError:
                            default_value = config['facets'][0].title()
                        %>
                        ${default_value}
                    </span>
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
        <div id="results_container" class="col-xs-12">
            <ol id='philologic_concordance' class="panel panel-default">
                % for i in results[start - 1:end]:
                    <li class='philologic_occurrence panel panel-default'>
                        <%
                         n += 1
                        %>
                        <div class="citation-container">
                           <div class="citation">
                               <div class="citation-overflow"></div>
                               <span class="cite" data-id="${' '.join(str(s) for s in i.philo_id)}">
                                   ${n}.&nbsp ${f.concordance_citation(db, config, i)}
                               </span>
                               <button class="btn btn-primary more_context" disabled="disabled" data-context="short">
                                   More
                               </button>
                           </div>
                        </div>
                       <div class='philologic_context'>
                           <div class="default_length">${fetch_concordance(i, path, config.concordance_length)}</div>
                       </div>
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