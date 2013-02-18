<%include file="header.mako"/>
<%include file="search_boxes.mako"/>
<div class='philologic_response'>
  <div class='initial_report'>
  <%include file="show_frequency.mako"/> 
   <p class='description'>
    <%
     start, end, n = f.link.page_interval(results_per_page, results, q["start"], q["end"])
    %>
    Hits <span class="start">${start}</span> - <span class="end">${end}</span> of ${len(results)}
    </p> 
  </div>
 <div class="results_container">
 <ol class='philologic_concordance'>
  % for i in results[start - 1:end]:
    <li class='philologic_occurrence'>
   <%
   n += 1
   author = i.author
   title = i.title
   from copy import deepcopy
   link_metadata = deepcopy(q["metadata"])
   link_metadata['author'] = author.encode('utf-8', 'ignore')
   link_metadata['title'] = title.encode('utf-8', 'ignore')
   url = f.link.make_query_link(q["q"],q["method"],q["arg"],**link_metadata)
   hit_num = len(i.bytes)
   %>
   <span class='hit_n'>${n}.</span>
   <a href='${url}' title="Click to retrieve all ${hit_num} occurences" class="tooltip_link"> ${title}, ${author}</a>
   <span style="font-weight:700; padding-left:25px;">${hit_num} occurences</span>
   <div class='philologic_context'>
   <span class='philologic_context'>${fetch_relevance(i, path, q)}...</span>
   </div>
   </li>
  % endfor
  </ol>
  </div>
  <div class="more">
  <%include file="pages.mako" args="start=start,results_per_page=results_per_page,q=q,results=results"/>
 <div style='clear:both;'></div>
 </div>
</div>
<%include file="footer.mako"/>