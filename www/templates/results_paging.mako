<%page args="start", "results_per_page", "q", "results"/>
<%
current_page, my_pages, page_num = f.link.pager(start, results_per_page, q, results)
%>
<div id='page_links' class="btn-group">
    % for page, link in my_pages:
        % if page == current_page:
            <a href="${link}" id="current_results_page" class="btn btn-default btn-lg active">${page}</a>
         % else:
            <a href="${link}" class="btn btn-default btn-lg">${page}</a>
         % endif
    % endfor
    % if results.done and page_num != my_pages[-1][0]:
        <%
        page_num = f.link.find_page_number(len(results), results_per_page)
        link = f.link.page_linker(page_num, results_per_page, q)
        %>
        % if current_page > my_pages[-1][0]:
           <a href="${link}" id="current_results_page" class="btn btn-default btn-lg active">Last</a>
        % else:
           <a href="${link}" class="btn btn-default btn-lg">Last</a>
        % endif
    % endif
</div>