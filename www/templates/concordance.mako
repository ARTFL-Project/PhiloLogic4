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
                 description = concordance['description']
                 r_status = "."
                 if not concordance['query_done']:
                    r_status += " Still working..."
                %>
                <div id="search_arguments">
                    Searching database for <b>${q['q'].decode('utf-8', 'ignore')}</b><br>
                    Bibliographic criteria: ${biblio_criteria or "<b>None</b>"}
                </div>
                <div id="search-hits" data-script="${config.db_url + '/scripts/get_total_results.py?' + q['q_string']}">
                    % if end != 0:
                        % if description['end'] < description['results_per_page'] or description['end'] < concordance['results_len']:
                            Hits <span id="start">${description['start']}</span> - <span id="end">${description['end']}</span> of <span id="total_results">${concordance['results_len'] or description['results_per_page']}</span><span id="incomplete">${r_status}</span>
                        % else:
                            Hits <span id="start">${description['start']}</span> - <span id="end">${concordance['results_len'] or description['end']}</span> of <span id="total_results">${concordance['results_len'] or description['results_per_page']}</span><span id="incomplete">${r_status}</span>         
                        % endif
                    % else:
                        No results for your query.
                    % endif
                </div>
            </div>
            <div class="row hidden-xs" id="act-on-report">
                <div class="col-sm-9 col-md-8 col-lg-6">
                    <%include file="concordance_kwic_switcher.mako"/>
                </div>
                <div class="col-sm-3 col-md-4 col-lg-4 col-lg-offset-2" id="right-act-on-report">
                    <%include file="sidebar_menu.mako"/>
                </div>
            </div>
        </div>
        <div class="row">
            <div id="results_container" class="col-xs-12">
                <ol id='philologic_concordance' data-more-context="${config.db_url + '/scripts/get_more_context.py?' + q['q_string']}">
                    % for pos, i in enumerate(concordance['results']):
                        <li class='philologic_occurrence panel panel-default'>
                            <%
                             n = description['start'] + pos
                            %>
                            <div class="citation-container row">
                                <div class="col-xs-12 col-sm-10 col-md-11">
                                   <span class="cite" data-id="${' '.join(str(s) for s in i['philo_id'])}">
                                       ${n}.&nbsp ${i['citation']}
                                   </span>
                                </div>
                                <div class="hidden-xs col-sm-2 col-md-1">
                                   <button class="btn btn-primary more_context pull-right" disabled="disabled" data-context="short">
                                       More
                                   </button>
                                </div>
                            </div>
                           <div class='philologic_context'>
                               <div class="default_length">${i['context']}</div>
                           </div>
                        </li>
                    % endfor
                </ol>
            </div>
            <%include file="show_frequency.mako"/>
        </div>
    </div>
    <div class="more">
        <%include file="results_paging.mako"/>
        <div style='clear:both;'></div>
    </div>
</div>
<%include file="footer.mako"/>