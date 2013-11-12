<%include file="header.mako"/>
<%include file="search_form.mako"/>
<script type="text/javascript" src="${db.locals['db_url']}/js/concordanceKwic.js"></script>
<div id='philologic_response'>
    <div id='initial_report'>
       <p id='description'>
            <%
             start, end, n = f.link.page_interval(results_per_page, results, q["start"], q["end"])
             r_status = "."
             if not results.done:
                r_status += " Still working.  Reload the page for a more accurate count of the results."
            %>
            Hits <span class="start">${start}</span> - <span class="end">${end}</span> of ${len(results)}${r_status}
        </p>
        <%include file="show_frequency.mako"/>
        <div id="report_switch">
            <input type="radio" name="report_switch" id="concordance_switch" value="?${q['q_string'].replace('report=kwic', 'report=concordance')}" checked="checked"><label for="concordance_switch">View occurences with context</label>
            <input type="radio" name="report_switch" id="kwic_switch" value="?${q['q_string'].replace('report=concordance', 'report=kwic')}"><label for="kwic_switch">View occurences line by line (KWIC)</label>
        </div>
    </div>
    <div id="results_container" class="results_container">
        <ol id='philologic_concordance'>
            % for i in results[start - 1:end]:
                <li class='philologic_occurrence'>
                 <%
                  n += 1
                 %>
                 <div class="citation cite_gradient" style="overflow:hidden;">
                    <span class='hit_n'>${n}.</span>
                    <span class="cite" style="display: inline-block;overflow:hidden;white-space: nowrap;text-overflow:ellipsis;-o-text-overflow:ellipsis;">
                        ${f.cite.make_abs_div_cite(db,i)}
                    </span>
                    <span class="more_context_and_close">
                        <span class="more_context">More</span>
                        <span class="close_concordance">X</span>
                    </span>
                </div>
                 <div class='philologic_context'>${fetch_concordance(i, path, q)}</div>
                </li>
            % endfor
        </ol>
    </div>
    <div class="more">
        <%include file="results_paging.mako" args="start=start,results_per_page=results_per_page,q=q,results=results"/> 
        <div style='clear:both;'></div>
    </div>
</div>
<%include file="footer.mako"/>