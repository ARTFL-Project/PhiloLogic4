## -*- coding: utf-8 -*-
<%include file="header.mako"/>
% if not config.dictionary:
    <%include file="search_form.mako"/>
% else:
    <%include file="dictionary_search_form.mako"/>
% endif
<div class="container-fluid" id='philologic_response'>
    % if not config.dictionary:
        <div class="row" id="landingGroup" data-script="${config.db_url + '/scripts/landing_page_content.py?landing_page_content_type='}">
            % if config.landing_page_browsing["author"]:
                <div class="col-xs-6" id="col-author">
                    <div class="panel panel-default">
                        <div class="panel-heading">
                            Author
                        </div>
                        <div class="panel-body">
                            <ul id="author-range-selectors" class="row" data-type="author">
                                <% author_range = ['A-D', 'E-I', 'J-M', 'N-R', 'S-V', 'W-Z'] %>
                                % for range in author_range:
                                    <li class="col-xs-6 col-sm-4 col-lg-2"><a data-range="${range}">${range}</a></li>
                                % endfor
                            </ul>
                        </div>
                    </div>
                </div>
            % endif
            % if config.landing_page_browsing["title"]:
                <div class="col-xs-6" id="col-title">
                    <div class="panel panel-default">
                        <div class="panel-heading">
                            Title
                        </div>
                        <div class="panel-body">
                            <ul id="title-range-selectors" class="row" data-type="title">
                                <% title_range = ['A-D', 'E-I', 'J-M', 'N-R', 'S-V', 'W-Z'] %>
                                % for range in title_range:
                                    <li class="col-xs-6 col-sm-4 col-lg-2"><a data-range="${range}">${range}</a></li>
                                % endfor
                            </ul>
                        </div>
                    </div>
                </div>
            % endif
            % if config.landing_page_browsing["date"]:
                <div class="col-xs-12" id="col-year">
                    <div class="panel panel-default">
                        <div class="panel-heading">
                            Year
                        </div>
                        <div class="panel-body">
                            <ul id="year-range-selectors" class="row" data-type="year">
                                <%
                                start = config.landing_page_browsing['date']['start']
                                end = config.landing_page_browsing['date']['end']
                                interval = config.landing_page_browsing['date']['interval']
                                %>
                                % for start_date in xrange(start, end, interval):
                                    <% end_date = start_date + interval - 1 %>
                                    <li class="col-xs-6 col-sm-4 col-md-3 col-lg-2"><a data-range="${start_date}-${end_date}">${start_date}-${end_date}</a></li>
                                % endfor
                            </ul>
                        </div>
                    </div>
                </div>
            % endif
        </div>
        <div id="landing-page-content" ></div>
    % else:
        <div class="row">
            <div id="dico-landing-volume" class="col-xs-6 panel panel-default" style="border-width: 0px; box-shadow: 0 0 0;" data-script="${config.db_url + '/scripts/get_bibliography.py?object_level=doc'}">
                <div class="panel-heading" style="margin-left: -15px; margin-right: -15px">
                    Browse by volume
                </div>
                <div class="panel-body" >
                    <ul class="list-group" style="margin-left: -15px; margin-right: -15px"></ul>
                </div>
            </div>
            <div id="dico-landing-alpha" class="col-xs-6 panel panel-default" style="border-width: 0px; box-shadow: 0 0 0;" data-script="${config.db_url + '/dispatcher.py?report=bibliography&head='}">
                <div class="panel-heading">
                    Browse by letter
                </div>
                <div class="panel-body">
                    <table class="table table-bordered">
                        <tr>
                            <td>A</td>
                            <td>B</td>
                            <td>C</td>
                            <td>D</td>
                        </tr>
                        <tr>
                            <td>E</td>
                            <td>F</td>
                            <td>G</td>
                            <td>H</td>
                        </tr>
                        <tr>
                            <td>I</td>
                            <td>J</td>
                            <td>K</td>
                            <td>L</td>
                        </tr>
                        <tr>
                            <td>M</td>
                            <td>N</td>
                            <td>O</td>
                            <td>P</td>
                        </tr>
                        <tr>
                            <td>Q</td>
                            <td>R</td>
                            <td>S</td>
                            <td>T</td>
                        </tr>
                        <tr>
                            <td>U</td>
                            <td>V</td>
                            <td>W</td>
                            <td>X</td>
                        </tr>
                        <tr>
                            <td>Y</td>
                            <td>Z</td>
                            <td></td>
                            <td></td>
                        </tr>
                    </table>
                </div>
            </div>
        </div>
    % endif
</div>
<%include file="footer.mako"/>
