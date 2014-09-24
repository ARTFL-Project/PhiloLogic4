<% start, end, n = f.link.page_interval(results_per_page, results, q["start"], q["end"]) %>
<ol id='philologic_concordance'>
  % for i in results[start - 1:end]:
      <li class='philologic_occurrence panel panel-default'>
          <%
           n += 1
          %>
          <div class="citation-container row">
              <div class="col-xs-12 col-sm-10 col-md-11">
                 <span class="cite" data-id="${' '.join(str(s) for s in i.philo_id)}">
                     ${n}.&nbsp ${f.concordance_citation(db, config, i)}
                 </span>
              </div>
              <div class="hidden-xs col-sm-2 col-md-1">
                 <button class="btn btn-primary more_context pull-right" disabled="disabled" data-context="short">
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