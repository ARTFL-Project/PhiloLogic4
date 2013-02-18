<%include file="header.mako"/>
<a href="javascript:void(0)" class="show_search_form">Show search form</a>
<%include file="search_boxes.mako"/>
<div class='philologic_response'>
  <div class='initial_report'>
   <p class='description'>
    <%
     start, end, n = f.link.page_interval(results_per_page, results, q["start"], q["end"])
    %>
    % if q['theme_rheme'] == 'full':
        <% 
        start = 1 
        end = -1
        %>
    % endif
    Hits <span class="start">${start}</span> - <span class="end">${end}</span> of ${len(results)}
   </p>
  </div>
<%include file="show_frequency.mako"/>
<div class="results_container">
 <ol class='philologic_concordance'>
  % for i in results[start - 1:end]:
   <li class='philologic_occurrence'>
    <%
     n += 1
    %>
    <span class='hit_n'>${n}.</span> ${f.cite.make_div_cite(i)}
    <a href="javascript:void(0)" class="more_context">Show more context</a>
    <br><b>${i.position} of clause: [${i.score} = ${i.percentage}]</b><br>
    <div class='philologic_context'>${i.concordance}</div>
   </li>
  % endfor
 </ol>
 % if q['theme_rheme'] == 'full':
    <div class='theme_rheme_full_report'>Full report:<br>
    Front of clause: ${full_report['Front']} out of ${len(results)}<br>
    Middle of clause: ${full_report['Middle']} out of ${len(results)}<br>
    End of clause: ${full_report['End']} out of ${len(results)}
    </div>
 % endif
 </div>
 <div class="more">
  <%include file="pages.mako" args="start=start,results_per_page=results_per_page,q=q,results=results"/>
   <div style='clear:both;'></div>
 </div>
</div>
<%include file="footer.mako"/>