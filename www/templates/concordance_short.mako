<% start, end, n = f.link.page_interval(results_per_page, results, q["start"], q["end"]) %>
<ol class='philologic_concordance'>
  % for i in results[start - 1:end]:
   <li class='philologic_occurrence'>
    <%
     n += 1
    %>
    <div class="citation cite_gradient" style="overflow:hidden;">
        <span class='hit_n'>${n}.</span>
        <span class="cite" style="display: inline-block;overflow:hidden;white-space: nowrap;text-overflow:ellipsis;-o-text-overflow:ellipsis;">
            ${f.concordance_citation(db,config, i)}
        </span>
        <span class="more_context_and_close">
            <span class="more_context" style="color:lightGray;">More</span>
        </span>
    </div>
     <div class='philologic_context'>
        <div class="default_length">${fetch_concordance(i, path, config.concordance_length)}</div>
    </div>
   </li>
  % endfor
</ol>
<script>
    $(document).ready(function() {
        $('.more_context').button();
    });
</script>