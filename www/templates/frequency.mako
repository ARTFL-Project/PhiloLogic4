<%include file="header.mako"/>
<%include file="search_boxes.mako"/>
<div class="results_container">
<div class='philologic_frequency_report'>
<% field, counts = generate_frequency(results, q, db) %>
<p class='description'>Frequency by ${field}</p>
 <p class='status'></p>
 Top 100 ${field}s displayed
<table border="1" class="philologic_table">
  <tr><th class="table_header">${field}</th><th class="table_header">count</th></tr>
% for k,v,url in counts:
   <tr><td class="table_column"><a href='${url}'>${k}</a></td><td class="table_column">${v}</td></tr>
% endfor
</table>
</div>
</div>
<%include file="footer.mako"/>