<%include file="header.mako"/>
<%include file="search_boxes.mako"/>
<div class='philologic_response'>
 <p class='description'>Bibliography Report: ${len(results)} results.</p>
 <div class="results_container">
 <div class='bibliographic_results'>
 <ol class='philologic_cite_list'>
 % for i in results:
  <li class='philologic_occurrence'>
##  <input type="checkbox" name="philo_id" value="${i.philo_id}">
  % if i.type == 'doc':
  <span class='philologic_cite'>${f.cite.make_doc_cite(i)} <b>Volume ${i.volume}</b></span>
  % else:
  <span class='philologic_cite'>${f.cite.make_div_cite(i)}</span>
  % endif
  </li>
 % endfor
 </ol>
</div>
</div>
</div>
<%include file="footer.mako"/>
