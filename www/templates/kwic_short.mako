 <%
 description = kwic['description']
 current_pos = description['start']
 %>
<div id="kwic_concordance">
    % for i in kwic['results']:
        <div class="kwic_line">
            % if len(str(description['end'])) > len(str(current_pos)):
                <% spaces = '&nbsp' * (len(str(description['end'])) - len(str(current_pos))) %>
                <span>${current_pos}.${spaces}</span>
            % else:
                <span>${current_pos}.</span>    
            % endif
            ${i['context']}
            <% current_pos += 1 %>
        </div>
    % endfor
</div>