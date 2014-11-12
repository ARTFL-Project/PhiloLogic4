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
                 description = kwic['description']
                 r_status = "."
                 if not kwic['query_done']:
                    r_status += " Still working..."
                 current_pos = description['start']
                %>
                <div id="search_arguments">
                    Searching database for <b>${q['q'].decode('utf-8', 'ignore')}</b></br>
                    Bibliographic criteria: ${biblio_criteria or "None"}
                </div>
                <div id="search-hits" data-script="${config.db_url + '/scripts/get_total_results.py?' + q['q_string']}">
                    % if kwic['results_len'] != 0:
                        % if description['end'] < description['results_per_page'] or description['end'] < kwic['results_len']:
                            Hits <span id="start">${description['start']}</span> - <span id="end">${description['end']}</span> of <span id="total_results">${kwic['results_len'] or description['results_per_page']}</span><span id="incomplete">${r_status}</span>
                        % else:
                            Hits <span id="start">${description['start']}</span> - <span id="end">${kwic['results_len'] or description['end']}</span> of <span id="total_results">${kwic['results_len'] or description['results_per_page']}</span><span id="incomplete">${r_status}</span>         
                        % endif
                    % else:
                        No results for your query.
                    % endif
                </div>
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
        <div class="row">
            <div id="results_container" class="col-xs-12" style="overflow: hidden;">
                <div id="kwic_concordance">
                    % for i in kwic['results']:
                        <div class="kwic_line">
                            % if len(str(description['end'])) > len(str(current_pos)):
                                <% spaces = '&nbsp' * (len(str(description['end'])) - len(str(current_pos))) %>
                                <span>${current_pos}.${spaces}</span>
                            % else:
                                <span>${current_pos}.</span>    
                            % endif
                            ${i['context']}
                            <% current_pos += 1 %>
                        </div>
                    % endfor
                </div>
            </div>
            <%include file="show_frequency.mako"/>
        </div>
    <!--    <div id="results-bibliography">
            <span id="show-results-bibliography">Results Bibliography in current page:</span>
        </div>-->
    </div>
    <div class="more">
        <%include file="results_paging.mako"/> 
        <div style='clear:both;'></div>
    </div>
</div>
<%include file="footer.mako"/>