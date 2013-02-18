<%include file="header.mako"/>
<%include file="search_boxes.mako"/>
<div class='philologic_response'>
 <div class='initial_report'>
 <p class='description'>
  <%
  start, end, n = f.link.page_interval(results_per_page, results, q["start"], q["end"])
  r_status = "."
  if not results.done:
     r_status += " Still working.  Refresh for a more accurate count of the results."  
  %>
  Hits <span class="start">${start}</span> - <span class="end">${end}</span> of ${len(results)}${r_status}
  </p>
 </div>
 <div id="report_switch">
 <input type="radio" name="report_switch" id="concordance_switch" value="?${q['q_string'].replace('report=kwic', 'report=concordance')}"><label for="concordance_switch">View occurences with context</label>
 <input type="radio" name="report_switch" id="kwic_switch" value="?${q['q_string'].replace('report=concordance', 'report=kwic')}" checked="checked"><label for="kwic_switch">View occurences line by line (KWIC)</label>
  </div>
 <%include file="show_frequency.mako"/>
 <div class="results_container" style="border-top-style:solid;border-top-width:1px;border-top-color: #CCCCCC;padding-top:10px;padding-bottom:10px;">
 <% current_pos = start %>
  % for i in fetch_kwic(results, path, q, f.link.byte_query, start-1, end):
   <div class="kwic_concordance">
   % if len(str(end)) > len(str(current_pos)):
    <% spaces = ' ' * (len(str(end)) - len(str(current_pos))) %>
    <span id="position" style="white-space:pre-wrap;">${current_pos}.${spaces}</span>
   % else:
    <span id="position">${current_pos}.</span>    
   % endif
   ${i}</div>
   <% current_pos += 1 %>
  % endfor
 </div>
 <div class="more">
 <%include file="pages.mako" args="start=start,results_per_page=results_per_page,q=q,results=results"/>
 <div style='clear:both;'></div>
 </div>
</div>
<%include file="footer.mako"/>
