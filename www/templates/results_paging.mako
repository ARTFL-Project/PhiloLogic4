<div id='page_links' class="btn-group">
    % for page, link in pages['page_links']:
        % if page == pages['current_page']:
            <a href="${link}" id="current_results_page" class="btn btn-default btn-lg active">${page}</a>
         % else:
            <a href="${link}" class="btn btn-default btn-lg">${page}</a>
         % endif
    % endfor
</div>