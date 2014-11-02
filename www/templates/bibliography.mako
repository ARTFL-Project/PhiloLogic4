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
                description = bibliography['description']
                r_status = "."
                #if not bibliography['query_done']:
                #    r_status += " Still working..."
                %>
                <div id="search_arguments">
                        Bibliographic criteria: ${biblio_criteria or "<b>None</b>"}<br>
                </div>
                Hits <span class="start">${description['start']}</span> - <span class="end">${description['end']}</span> of <span id="total_results">${bibliography['results_len']}</span>${r_status}
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
                    <% n = description['n'] %>
                    % for i in bibliography['results']:
                        <li class='biblio-occurrence panel panel-default'>
                            <%
                            n += 1
                            %>
                            <span style="padding-left: 5px;">${n}.</span>
                            <span class='philologic_cite'>${i['citation']}</span>
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
