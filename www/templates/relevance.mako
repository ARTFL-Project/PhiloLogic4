<%include file="header.mako"/>
<%include file="search_boxes.mako"/>
<script type="text/javascript" src="${db.locals['db_url']}/js/rankedRelevance.js"></script>
<div class='philologic_response'>
    <div id='initial_report'>
        <%include file="show_frequency.mako"/> 
        <p id='description'>
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
                        hit_num = len(i.bytes)
                    %>
                    <span class='hit_n'>${n}.</span>
                    % if i.type == 'doc':
                        <span class='tooltip_link' title="Click to see title">${f.cite.make_abs_doc_cite(db,i)}</span>
                    % else:
                        <span class='tooltip_link' title="Click to see document">${f.cite.make_abs_div_cite(db,i)}</span>
                    % endif
                    % if hit_num:
                        <%
                            metadata = {}
                            for m in db.locals['metadata_fields']:
                                metadata[m] = '"' + i[m].encode('utf-8', 'ignore') + '"'
                            url = f.link.make_query_link(q["q"],q["method"],q["arg"],report='concordance',**metadata)
                        %>
                        <span style"padding-left:25px">
                            ##<b>${hit_num} occurences</b>
                            <a href='${url}' title="Click to retrieve all ${hit_num} occurences" class="tooltip_link">${hit_num} occurences</a>
                        </span>
                        <div class='philologic_context'>
                            <span class='philologic_context'>${fetch_relevance(i, path, q)}...</span>
                        </div>
                    % else:
                        <span style"padding-left:25px" style="font-style:italic">
                            No occurences in the text itself
                        </span>
                    % endif
                </li>
            % endfor
        </ol>
    </div>
    <div class="more">
        <%include file="results_paging.mako" args="start=start,results_per_page=results_per_page,q=q,results=results"/>
        <div style='clear:both;'></div>
   </div>
</div>
<%include file="footer.mako"/>