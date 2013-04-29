<%include file="header.mako"/>
<%include file="search_boxes.mako"/>
<div class='philologic_response'>
    <div class='initial_report'>
        <p class='description'>
            <%
             start, end, n = f.link.page_interval(results_per_page, results, q["start"], q["end"])
            %>
            ${q['collocate_num']} occurences of collocate "${q['collocate'].decode('utf-8', 'ignore')}" in the vicinity of "${q['q'].decode('utf-8', 'ignore')}":
            <div class="description">
                Hits <span class="start">${start}</span> - <span class="end">${end}</span> of ${q['collocate_num']}
            </div>
        </p>
    </div>
    <div class="results_container">
        <ol class='philologic_concordance'>
            % for i in results[start - 1:end]:
                <li class='philologic_occurrence'>
                    <%
                     n += 1
                    %>
                    <span class='hit_n'>${n}.</span> ${f.cite.make_div_cite(i)}
                    % if i.collocate_num > 1:
                        <span style="padding-left:20px"><b>At least ${i.collocate_num} occurences of collocate in hit</b></span>
                    % endif
                    <a href="javascript:void(0)" class="more_context">More</a>
                    <div class='philologic_context'>
                       ${fetch_concordance(i, path, q)}
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
<%include file="footer.mako"/>