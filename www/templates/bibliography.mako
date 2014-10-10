<%include file="header.mako"/>
% if not config.dictionary:
    <%include file="search_form.mako"/>
% else:
    <%include file="dictionary_search_form.mako"/>
% endif
<div class="container-fluid">
    <div id='philologic_response' class="panel panel-default">
        <div id='initial_report'>
            <div id='description'>
                <button type="button" id="export-results" class="btn btn-default btn-xs pull-right" data-toggle="modal" data-target="#export-dialog">
                        Export results
                </button>
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
            <div class="row" id="act-on-report">
                <div class="col-xs-12">
                    <%include file="sidebar_menu.mako"/>
                </div>
            </div>
        </div>
        <div class="row">
            <div id='results_container' class="col-xs-12">
                <ol class="bibliographic-results">
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
</div>
<%include file="footer.mako"/>
