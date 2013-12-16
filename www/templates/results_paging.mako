<%page args="start", "results_per_page", "q", "results"/>
<%
current_page, my_pages, page_num = f.link.pager(start, results_per_page, q, results)
%>
<div id='page_links'>
    % for page, link in my_pages:
        % if page == current_page:
            <a href="${link}" id="current_results_page">${page}</a>
         % else:
            <a href="${link}">${page}</a>
         % endif
    % endfor
    % if results.done and page_num != my_pages[-1][0]:
        <%
        page_num = f.link.find_page_number(len(results), results_per_page)
        link = f.link.page_linker(page_num, results_per_page, q)
        %>
        % if current_page > my_pages[-1][0]:
           <a href="${link}" id="current_results_page">Last</a>
        % else:
           <a href="${link}">Last
        % endif
    % endif
</div>