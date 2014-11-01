<%include file="header.mako"/>
% if not config.dictionary:
    <%include file="search_form.mako"/>
% else:
    <%include file="dictionary_search_form.mako"/>
% endif
<div id='philologic_response' class="container-fluid">
    <div class="row" id="toc-report-title">
        <div class="col-xs-offset-2 col-xs-8">
            <span class='philologic_cite'>${toc['citation']}</span>
        </div>
    </div>
    <div class="panel panel-default">
        % if db.locals['debug'] == True:
            <button id="show-header" class="btn btn-primary">Show Header</button>
            <div id="tei-header" style="white-space: pre; font-family: 'Droid Sans Mono', sans-serif; font-size: 80%; display: none;"></div>
        % endif
        <div id="toc-report">
            <div id="toc-content">
                % for philo_id, philo_type, head, link in toc['content']:
                    <%
                    link = '<a href="%s" id="%s">%s</a>' % (link, philo_id.replace(' ', '_'), head)
                    %>
                    % if philo_type == "div2":
                        <div class="toc-div2">
                            <span class="bullet-point-div2"></span>
                            ${link}
                        </div>
                    % elif philo_type == "div3":
                        <div class="toc-div3"><span class="bullet-point-div3"></span>
                            ${link}
                        </div>
                    % else:
                        <div class="toc-div1"><span class="bullet-point-div1"></span>
                            ${link}
                        </div>
                    % endif
                % endfor
            </div>
        </div>
    </div>
</div>
<%include file="footer.mako"/>