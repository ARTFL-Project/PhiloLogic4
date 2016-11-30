#!/usr/bin/env python
"""Bootstrap Web app"""

from __future__ import absolute_import
from __future__ import print_function
import imp
import os.path
import sys

from philologic.runtime import WebConfig
from philologic.runtime import WSGIHandler

global_config = imp.load_source("philologic4", "/etc/philologic/philologic4.cfg")
path = os.path.abspath(os.path.dirname(__file__))
dbname = path.strip().split('/')[-1]

config = WebConfig(os.path.abspath(os.path.dirname(__file__)))
theme = config.theme

css_files = [
    "app/assets/css/bootstrap.min.css",
    "app/assets/css/split/style.css", "app/assets/css/split/%s" % theme,
    "app/assets/css/split/searchForm.css",
    "app/assets/css/split/landingPage.css",
    "app/assets/css/split/concordanceKwic.css",
    "app/assets/css/split/timeSeries.css",
    "app/assets/css/image_gallery/blueimp-gallery.min.css",
    "app/assets/css/split/textObjectNavigation.css"
]

# External JavaScript assets
js_plugins = [
    "app/assets/js/plugins/ui-utils.min.js",
    "app/assets/js/plugins/ng-infinite-scroll.min.js",
    "app/assets/js/plugins/jquery.tagcloud.js",
    "app/assets/js/plugins/blueimp-gallery.min.js",
    "app/assets/js/plugins/jquery.scrollTo.min.js",
    "app/assets/js/plugins/Chart.min.js",
    "app/assets/js/plugins/angular-chart.min.js",
    "app/assets/js/plugins/bootstrap.min.js",
    "app/assets/js/plugins/velocity.min.js",
    "app/assets/js/plugins/velocity.ui.min.js",
    "app/assets/js/plugins/angular-velocity.min.js"
]

# Full List of all AngularJS specific JavaScript
js_files = [
    "app/bootstrapApp.js", "app/philoLogicMain.js", "app/routes.js",
    "app/shared/directives.js", "app/shared/services.js",
    "app/shared/config.js", "app/shared/filters.js", "app/shared/values.js",
    "app/shared/searchArguments/searchArgumentsDirective.js",
    "app/shared/exportResults/exportResults.js",
    "app/components/landingPage/landingPageDirectives.js",
    "app/components/landingPage/landingPage.js",
    "app/shared/searchForm/searchFormServices.js",
    "app/shared/searchForm/searchFormFilters.js",
    "app/shared/searchForm/searchFormDirectives.js",
    "app/shared/searchForm/searchForm.js",
    "app/components/concordanceKwic/concordanceKwicValues.js",
    "app/components/concordanceKwic/concordanceKwicDirectives.js",
    "app/components/concordanceKwic/facetsDirectives.js",
    "app/components/concordanceKwic/concordanceKwicFilters.js",
    "app/components/concordanceKwic/concordanceKwic.js",
    "app/components/textNavigation/textNavigationFilters.js",
    "app/components/textNavigation/textNavigationValues.js",
    "app/components/textNavigation/textNavigationDirectives.js",
    "app/components/textNavigation/textNavigationCtrl.js",
    "app/components/tableOfContents/tableOfContents.js",
    "app/components/collocation/collocationDirectives.js",
    "app/components/collocation/collocation.js",
    "app/components/timeSeries/timeSeriesFilters.js",
    "app/components/timeSeries/timeSeriesDirectives.js",
    "app/components/timeSeries/timeSeries.js",
    "app/shared/accessControl/accessControlDirective.js",
    "app/shared/accessControl/accessControlCtrl.js"
]


def angular(environ, start_response):
    headers = [('Content-type', 'text/html; charset=UTF-8'),
               ("Access-Control-Allow-Origin", "*")]
    if not config.valid_config:  # This means we have an error in the webconfig file
        html = build_misconfig_page(config.traceback, 'webconfig.cfg')
    # TODO handle errors in db.locals.py
    else:
        request = WSGIHandler(environ, config)
        if config.access_control:
            if not request.authenticated:
                token = f.check_access(environ, config)
                if token:
                    print("ISSUING TOKEN", file=sys.stderr)
                    h, ts = token
                    headers.append(("Set-Cookie", "hash=%s" % h))
                    headers.append(("Set-Cookie", "timestamp=%s" % ts))
                else:
                    print("NOT AUTHENTICATED", file=sys.stderr)
        html = build_html_page(config)
    start_response('200 OK', headers)
    return html


def build_html_page(config):
    html_page = open('%s/app/index.html' % config.db_path).read()
    html_page = html_page.replace('$DBNAME', config.dbname)
    html_page = html_page.replace('$DBURL', os.path.join(global_config.url_root, dbname))
    html_page = html_page.replace('$CSS', load_CSS())
    html_page = html_page.replace('$JS', load_JS())
    return html_page


def build_misconfig_page(traceback, config_file):
    html_page = open('%s/app/misconfiguration.html' % path).read()
    html_page = html_page.replace('$CSS', load_CSS())
    html_page = html_page.replace('$TRACEBACK', traceback)
    html_page = html_page.replace('$CONFIG_FILE', config_file)
    return html_page


def load_CSS():
    mainCSS = os.path.join(path, "app/assets/css/philoLogic.css")
    if os.path.exists(mainCSS):
        if not config.production:
            css_links = concat_CSS()
    else:
        css_links = concat_CSS()
    if config.production:
        return '<link rel="stylesheet" href="app/assets/css/philoLogic.css">'
    else:
        return '\n'.join(css_links)


def concat_CSS():
    css_string, css_links = concatenate_files(css_files, 'css')
    output = open(os.path.join(path, 'app/assets/css/philoLogic.css'), 'w')
    output.write(css_string)
    return css_links


def load_JS():
    mainJS = os.path.join(path, "app/assets/js/philoLogic.js")
    if os.path.exists(mainJS):
        if not config.production:
            js_links, js_plugins_links = concat_JS()
    else:
        js_links, js_plugins_links = concat_JS()
    if config.production:
        scripts = '<script src="app/assets/js/plugins/philoLogicPlugins.js"></script>'
        scripts += '<script src="app/assets/js/philoLogic.js"></script>'
        return scripts
    else:
        return '\n'.join(js_plugins_links + js_links)


def concat_JS():
    js_plugins_string, js_plugins_links = concatenate_files(js_plugins, 'js')
    plugin_output = open(os.path.join(
        path, 'app/assets/js/plugins/philoLogicPlugins.js'), 'w')
    plugin_output.write(js_plugins_string)
    js_string, js_links = concatenate_files(js_files, "js")
    output = open(os.path.join(path, 'app/assets/js/philoLogic.js'), 'w')
    output.write(js_string)
    return js_links, js_plugins_links


def concatenate_files(file_list, file_type):
    string = []
    links = []
    for file_path in file_list:
        try:
            string.append(open(os.path.join(path, file_path)).read())
            if not config.production:
                if file_type == "css":
                    links.append(
                        '<link rel="stylesheet" href="%s">' % file_path)
                else:
                    links.append('<script src="%s"></script>' % file_path)
        except IOError:
            pass
    string = '\n'.join(string)
    return string, links
