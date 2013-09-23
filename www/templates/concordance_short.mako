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
            ${f.cite.make_abs_div_cite(db,i)}
        </span>
        <span class="more_context">More</span>
    </div>
     <div class='philologic_context'>${fetch_concordance(i, path, q)}</div>
   </li>
  % endfor
</ol>
<script>
    $(document).ready(function() {
        $('.more_context').button();
    });
</script>