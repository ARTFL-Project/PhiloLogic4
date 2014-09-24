<%include file="header.mako"/>
<%include file="search_form.mako"/>
<div class="container-fluid" id='philologic_response'>
    <div>
        <a href="${config.db_url}/">Return to search form</a>
        <p>
            <a id="return_to_colloc">
                Return to previous results page
            </a>
        </p>
    </div>
    <div id='initial_report'>
        <div id='description'>
            <%
             start, end, n = f.link.page_interval(results_per_page, results, q["start"], q["end"])
            %>
            <div id="search_arguments">
                Displaying ${q['collocate_num']} occurences of collocate <b>${q['collocate'].decode('utf-8', 'ignore')}</b> in the vicinity of <b>${q['q'].decode('utf-8', 'ignore')}</b><br>
                Bibliographic criteria: ${biblio_criteria or "<b>None</b>"}
            </div> 
            Hits <span class="start">${start}</span> - <span class="end">${end}</span>
        </div>
    </div>
    <% occurences = 0 %>
    <div class="row">
        <div id="results_container" class="col-xs-12">
            <ol id='philologic_concordance' class="panel panel-default">
                % for i in results[start - 1:end]:
                    <li class="philologic_occurrence panel panel-default">
                        <%
                        n += 1
                        occurences += i.collocate_num
                        %>
                        <div class="citation-container row">
                            <div class="col-xs-12 col-sm-10 col-md-11">
                               <span class="cite" data-id="${' '.join(str(s) for s in i.philo_id)}">
                                   ${n}.&nbsp ${f.concordance_citation(db, config, i)}
                               </span>
                            </div>
                            <div class="hidden-xs col-sm-2 col-md-1">
                               <button class="btn btn-primary more_context pull-right" disabled="disabled" data-context="short">
                                   More
                               </button>
                            </div>
                        </div>
                        % if i.collocate_num > 1:
                            <div style="padding-left:5px;"><b>At least ${i.collocate_num} occurences of collocate in hit</b></div>
                        % endif
                        <div class='philologic_context'>
                            <div class="default_length">${colloc_concordance(i, path, q, config['concordance_length'])}</div>
                        </div>
                    </li>
                % endfor
            </ol>
        </div>
     </div>
     <div class="more">
        <%include file="results_paging.mako" args="start=start,results_per_page=results_per_page,q=q,results=results"/> 
        <div style='clear:both;'></div>
     </div>
</div>
<script>
var occurences = ${occurences};
</script>
<script type="text/javascript" src="${config.db_url}/js/concordanceFromCollocation.js"></script>
<%include file="footer.mako"/>
