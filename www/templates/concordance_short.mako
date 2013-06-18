<% start, end, n = f.link.page_interval(results_per_page, results, q["start"], q["end"]) %>
<ol class='philologic_concordance'>
  % for i in results[start - 1:end]:
   <li class='philologic_occurrence'>
    <%
     n += 1
    %>
    <span class='hit_n'>${n}.</span> ${f.cite.make_abs_div_cite(db,i)}
    <a href="#" class="more_context">More</a>
    <div class='philologic_context'>${fetch_concordance(i, path, q)}</div>
   </li>
  % endfor
 </ol>