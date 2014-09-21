 <%
    start, end, n = f.link.page_interval(results_per_page, results, q["start"], q["end"])
    current_pos = start
 %>
<div id="kwic_concordance" class="panel panel-default">
  % for i in fetch_kwic(results, path, q, f.link.byte_query, db, start-1, end):
      <div class="kwic_line">
          % if len(str(end)) > len(str(current_pos)):
              <% spaces = '&nbsp' * (len(str(end)) - len(str(current_pos))) %>
              <span>${current_pos}.${spaces}</span>
          % else:
              <span>${current_pos}.</span>    
          % endif
          ${i}
          <% current_pos += 1 %>
      </div>
  % endfor
</div>