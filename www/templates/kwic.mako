<%include file="header.mako"/>
<%include file="search_boxes.mako"/>
<script type="text/javascript" src="${db.locals['db_url']}/js/concordanceKwic.js"></script>
<div id='philologic_response'>
    <div id='initial_report'>
       <p id='description'>
            <%
             start, end, n = f.link.page_interval(results_per_page, results, q["start"], q["end"])
             r_status = "."
             if not results.done:
                r_status += " Still working.  Refresh for a more accurate count of the results."
             current_pos = start
            %>
            Hits <span class="start">${start}</span> - <span class="end">${end}</span> of ${len(results)}${r_status}
        </p>
        <%include file="show_frequency.mako"/>
        <div id="report_switch">
            <input type="radio" name="report_switch" id="concordance_switch" value="?${q['q_string'].replace('report=kwic', 'report=concordance')}"><label for="concordance_switch">View occurences with context</label>
            <input type="radio" name="report_switch" id="kwic_switch" value="?${q['q_string'].replace('report=concordance', 'report=kwic')}" checked="checked"><label for="kwic_switch">View occurences line by line (KWIC)</label>
        </div>
    </div>
    <div id="results_container" class="results_container">
        <div id="kwic_concordance">
            % for i in fetch_kwic(results, path, q, f.link.byte_query, db, start-1, end):
                <div class="kwic_line">
                    % if len(str(end)) > len(str(current_pos)):
                        <% spaces = ' ' * (len(str(end)) - len(str(current_pos))) %>
                        <span id="position" style="white-space:pre-wrap;">${current_pos}.${spaces}</span>
                    % else:
                        <span id="position">${current_pos}.</span>    
                    % endif
                    ${i}
                    <% current_pos += 1 %>
                </div>
            % endfor
        </div>
    </div>
    <div class="more">
        <%include file="results_paging.mako" args="start=start,results_per_page=results_per_page,q=q,results=results"/> 
        <div style='clear:both;'></div>
    </div>
</div>
<%include file="footer.mako"/>