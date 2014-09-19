## -*- coding: utf-8 -*-
<%include file="header.mako"/>	  	
<%include file="search_form.mako"/>
<div class="container-fluid" id='philologic_response'>
    <div class="row" id="landingGroup">
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
                        <li class="col-xs-6 col-sm-4 col-md-3 col-lg-2"><a data-target="year-group-1" data-range="1600-1624">1600-1624</a></li>
                        <li class="col-xs-6 col-sm-4 col-md-3 col-lg-2"><a data-target="year-group-2" data-range="1625-1649">1625-1649</a></li>
                        <li class="col-xs-6 col-sm-4 col-md-3 col-lg-2"><a data-target="year-group-3" data-range="1650-1674">1650-1674</a></li>
                        <li class="col-xs-6 col-sm-4 col-md-3 col-lg-2"><a data-target="year-group-4" data-range="1675-1699">1675-1699</a></li>
                        <li class="col-xs-6 col-sm-4 col-md-3 col-lg-2"><a data-target="year-group-5" data-range="1700-1724">1700-1724</a></li>
                        <li class="col-xs-6 col-sm-4 col-md-3 col-lg-2"><a data-target="year-group-6" data-range="1725-1749">1725-1749</a></li>
                        <li class="col-xs-6 col-sm-4 col-md-3 col-lg-2"><a data-target="year-group-7" data-range="1750-1774">1750-1774</a></li>
                        <li class="col-xs-6 col-sm-4 col-md-3 col-lg-2"><a data-target="year-group-8" data-range="1775-1799">1775-1799</a></li>
                    </ul>
                </div>
            </div>
        </div>
    </div>
    <div id="landing-page-content" class="panel panel-default">
        <div id="author-range-display">
            <div id="author-group-1" style="padding: 10px; display: none;"></div>
            <div id="author-group-2" style="padding: 10px; display: none;"></div>
            <div id="author-group-3" style="padding: 10px; display: none;"></div>
            <div id="author-group-4" style="padding: 10px; display: none;"></div>
            <div id="author-group-5" style="padding: 10px; display: none;"></div>
            <div id="author-group-6" style="padding: 10px; display: none;"></div>
        </div>
        <div id="title-range-display">
            <div id="title-group-1" style="padding: 10px; display: none;"></div>
            <div id="title-group-2" style="padding: 10px; display: none;"></div>
            <div id="title-group-3" style="padding: 10px; display: none;"></div>
            <div id="title-group-4" style="padding: 10px; display: none;"></div>
            <div id="title-group-5" style="padding: 10px; display: none;"></div>
            <div id="title-group-6" style="padding: 10px; display: none;"></div>
        </div>
        <div id="year-range-display">
            <div id="year-group-1" style="padding: 10px; display: none;"></div>
            <div id="year-group-2" style="padding: 10px; display: none;"></div>
            <div id="year-group-3" style="padding: 10px; display: none;"></div>
            <div id="year-group-4" style="padding: 10px; display: none;"></div>
            <div id="year-group-5" style="padding: 10px; display: none;"></div>
            <div id="year-group-6" style="padding: 10px; display: none;"></div>
            <div id="year-group-7" style="padding: 10px; display: none;"></div>
            <div id="year-group-8" style="padding: 10px; display: none;"></div>
        </div>
    </div>
</div>
<%include file="footer.mako"/>
<script src="js/split/landingPage.js"></script>
