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
            <div class="col-xs-6" id="col-author">
                <div class="panel panel-default">
                    <div class="panel-heading">
                        Author
                    </div>
                    <div class="panel-body">
                        <ul id="author-range-selectors" class="row" data-type="author">
                            <li class="col-xs-6 col-sm-4 col-lg-2"><a data-target="author-group-1" data-range="A-D">A-D</a></li>
                            <li class="col-xs-6 col-sm-4 col-lg-2"><a data-target="author-group-2" data-range="E-I">E-I</a></li>
                            <li class="col-xs-6 col-sm-4 col-lg-2"><a data-target="author-group-3" data-range="J-M">J-M</a></li>
                            <li class="col-xs-6 col-sm-4 col-lg-2"><a data-target="author-group-4" data-range="N-R">N-R</a></li>
                            <li class="col-xs-6 col-sm-4 col-lg-2"><a data-target="author-group-5" data-range="S-V">S-V</a></li>
                            <li class="col-xs-6 col-sm-4 col-lg-2"><a data-target="author-group-6" data-range="W-Z">W-Z</a></li>
                        </ul>
                    </div>
                </div>
            </div>
            <div class="col-xs-6" id="col-title">
                <div class="panel panel-default">
                    <div class="panel-heading">
                        Title
                    </div>
                    <div class="panel-body">
                        <ul id="title-range-selectors" class="row" data-type="title">
                            <li class="col-xs-6 col-sm-4 col-lg-2"><a data-target="title-group-1" data-range="A-D">A-D</a></li>
                            <li class="col-xs-6 col-sm-4 col-lg-2"><a data-target="title-group-2" data-range="E-I">E-I</a></li>
                            <li class="col-xs-6 col-sm-4 col-lg-2"><a data-target="title-group-3" data-range="J-M">J-M</a></li>
                            <li class="col-xs-6 col-sm-4 col-lg-2"><a data-target="title-group-4" data-range="N-R">N-R</a></li>
                            <li class="col-xs-6 col-sm-4 col-lg-2"><a data-target="title-group-5" data-range="S-V">S-V</a></li>
                            <li class="col-xs-6 col-sm-4 col-lg-2"><a data-target="title-group-6" data-range="W-Z">W-Z</a></li>
                        </ul>
                    </div>
                </div>
            </div>
            <div class="col-xs-12" id="col-year">
                <div class="panel panel-default">
                    <div class="panel-heading">
                        Year
                    </div>
                    <div class="panel-body">
                        <ul id="year-range-selectors" class="row" data-type="year">
                            <li class="col-xs-6 col-sm-4 col-md-3 col-lg-2"><a data-target="year-group-1" data-range="1700-1709">1700-1709</a></li>
                            <li class="col-xs-6 col-sm-4 col-md-3 col-lg-2"><a data-target="year-group-2" data-range="1710-1719">1710-1719</a></li>
                            <li class="col-xs-6 col-sm-4 col-md-3 col-lg-2"><a data-target="year-group-3" data-range="1720-1729">1720-1729</a></li>
                            <li class="col-xs-6 col-sm-4 col-md-3 col-lg-2"><a data-target="year-group-4" data-range="1730-1739">1730-1739</a></li>
                            <li class="col-xs-6 col-sm-4 col-md-3 col-lg-2"><a data-target="year-group-5" data-range="1740-1749">1740-1749</a></li>
                            <li class="col-xs-6 col-sm-4 col-md-3 col-lg-2"><a data-target="year-group-6" data-range="1750-1759">1750-1759</a></li>
                            <li class="col-xs-6 col-sm-4 col-md-3 col-lg-2"><a data-target="year-group-7" data-range="1760-1769">1760-1769</a></li>
                            <li class="col-xs-6 col-sm-4 col-md-3 col-lg-2"><a data-target="year-group-8" data-range="1770-1779">1770-1779</a></li>
                            <li class="col-xs-6 col-sm-4 col-md-3 col-lg-2"><a data-target="year-group-8" data-range="1780-1789">1780-1789</a></li>
                            <li class="col-xs-6 col-sm-4 col-md-3 col-lg-2"><a data-target="year-group-8" data-range="1790-1799">1790-1799</a></li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
        <div id="landing-page-content" class="panel panel-default">
            <div id="author-range-display"></div>
            <div id="title-range-display"></div>
            <div id="year-range-display"></div>
        </div>
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
<script src="js/split/landingPage.js"></script>
