<div id='page_links' class="btn-group">
    % for page, link in pages['my_pages']:
        % if page == pages['current_page']:
            <a href="${link}" id="current_results_page" class="btn btn-default btn-lg active">${page}</a>
         % else:
            <a href="${link}" class="btn btn-default btn-lg">${page}</a>
         % endif
    % endfor
    % if pages['last_page_link']:
        % if pages['current_page'] > pages['my_pages'][-1][0]:
           <a href="${pages['last_page_link']}" id="current_results_page" class="btn btn-default btn-lg active">Last</a>
        % else:
           <a href="${pages['last_page_link']}" class="btn btn-default btn-lg">Last</a>
        % endif
    % endif
</div>