<%def name="bibliography(biblio, *metadata, **template_args)">
     <% biblio_set = set([]) %>
     % for i in biblio:
          % if i.philo_id[0] in biblio_set:
                <% continue %>
          % else:
                <li>
                <% biblio_set.add(i.philo_id[0]) %>
          % endif
          % if template_args['form']:
              <input type="checkbox" name="title" value="${i.title}">
          % endif
         <% href = "./" + str(i.philo_id[0]) %>
         <a href="${href}">
         % for field in metadata:
             % if field == 'volume':
                 Vol. ${i.volume},
             % else:
                 ${i[field]},
             % endif
         % endfor
         </a></li>
     % endfor
</%def>