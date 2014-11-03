<% description = concordance['description'] %>
<ol id='philologic_concordance' data-more-context="${config.db_url + '/scripts/get_more_context.py?' + q['q_string']}">
    <% n = description['n'] %>
    % for i in concordance['results']:
        <li class='philologic_occurrence panel panel-default'>
            <%
             n += 1
            %>
            <div class="citation-container row">
                <div class="col-xs-12 col-sm-10 col-md-11">
                   <span class="cite" data-id="${' '.join(str(s) for s in i['philo_id'])}">
                       ${n}.&nbsp ${i['citation']}
                   </span>
                </div>
                <div class="hidden-xs col-sm-2 col-md-1">
                   <button class="btn btn-primary more_context pull-right" disabled="disabled" data-context="short">
                       More
                   </button>
                </div>
            </div>
            <div class='philologic_context'>
               <div class="default_length">${i['context']}</div>
            </div>
        </li>
    % endfor
</ol>