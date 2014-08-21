<% start, end, n = f.link.page_interval(results_per_page, results, q["start"], q["end"]) %>
<ol id='philologic_concordance' class="panel panel-default">
  % for i in results[start - 1:end]:
      <li class='philologic_occurrence panel panel-default'>
          <%
           n += 1
          %>
          <div class="citation-container">
             <div class="citation">
                 <div class="citation-overflow"></div>
                 <span class="cite" data-id="${' '.join(str(s) for s in i.philo_id)}">
                     ${n}.&nbsp ${f.concordance_citation(db, config, i)}
                 </span>
                 <button class="btn btn-primary more_context" disabled="disabled" data-context="short">
                     More
                 </button>
             </div>
          </div>
         <div class='philologic_context'>
             <div class="default_length">${fetch_concordance(i, path, config.concordance_length)}</div>
         </div>
      </li>
  % endfor
</ol>