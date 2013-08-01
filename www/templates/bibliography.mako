<%include file="header.mako"/>
<%include file="search_boxes.mako"/>
<script type="text/javascript" src="${db.locals['db_url']}/js/bibliography.js"></script>
<div class='philologic_response'>
    <div class='initial_report'>
        <p class='description'>
        <%
        start, end, n = f.link.page_interval(results_per_page, results, q["start"], q["end"])
        r_status = "."
        if not results.done:
           r_status += " Still working.  Refresh for a more accurate count of the results."
        %>
        Bibliography Report: Hits <span class="start">${start}</span> - <span class="end">${end}</span> of ${len(results)}${r_status}
        </p>
        <%include file="show_frequency.mako"/>
    </div>
    <div class="results_container">
        <div class='bibliographic_results'>
            <ol class='philologic_cite_list'>
                % for i in results[start-1:end]:
                    <li class='philologic_occurrence'>
                        <%
                        n += 1
                        %>
                        <span class='hit_n'>${n}.</span>
                        ##<input type="checkbox" name="philo_id" value="${i.philo_id}">
                        % if i.type == 'doc':
                            <span class='philologic_cite'>${f.cite.make_abs_doc_cite(db,i)} <b>Volume ${i.volume}</b></span>
                        % else:
                            <span class='philologic_cite'>${f.cite.make_abs_div_cite(db,i)}</span>
                        % endif
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
<%include file="footer.mako"/>
