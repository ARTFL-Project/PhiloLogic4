<%include file="header.mako"/>
<%include file="search_form.mako"/>
<div id='philologic_response' style="margin-top:0px;">
    <div>
        <a href="${config.db_url}/">Return to search form</a>
        <p>
            <span id="return_to_colloc">
                Return to previous results page
            </span>
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
            
            <br><br><span id='colloc_in_hits'></span> occurences in
            hits <span class="start">${start}</span> - <span class="end">${end}</span>
        </div>
    </div>
    <% occurences = 0 %>
    <div id="results_container" class="results_container">
        <ol id='colloc_concordance'>
            % for i in results[start - 1:end]:
                <li class='philologic_occurrence'>
                    <%
                    n += 1
                    occurences += i.collocate_num
                    %>
                    <div class="citation cite_gradient" style="overflow:hidden;">
                        <span class='hit_n'>${n}.</span>
                        <span class="cite" style="display: inline-block;overflow:hidden;white-space: nowrap;text-overflow:ellipsis;-o-text-overflow:ellipsis;">
                            ${f.cite.make_abs_div_cite(db,config, i)}
                        </span>
                        <span class="more_context_and_close">
                            <span class="more_context">More</span>
                        </span>
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