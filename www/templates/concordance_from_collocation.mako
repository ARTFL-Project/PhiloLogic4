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
                <span id='colloc_in_hits'></span> occurences in
                hits <span class="start">${start}</span> - <span class="end">${end}</span>
            </div>
        </p>
    </div>
    <% occurences = 0 %>
    <div class="results_container">
        <ol class='colloc_concordance'>
            % for i in results[start - 1:end]:
                <li class='philologic_occurrence'>
                    <%
                    n += 1
                    occurences += i.collocate_num
                    %>
                    <span class='hit_n'>${n}.</span> ${f.cite.make_abs_div_cite(db,i)}
                    % if i.collocate_num > 1:
                        <span style="padding-left:20px"><b>At least ${i.collocate_num} occurences of collocate in hit</b></span>
                    % endif
                    <a href="javascript:void(0)" class="more_context">More</a>
                    <div class='philologic_context'>
                       ${colloc_concordance(i, path, q, db)}
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
$(document).ready(function() {
    $('#colloc_in_hits').append(${occurences});
});
</script>
<%include file="footer.mako"/>