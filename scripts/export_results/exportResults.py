#!/usr/bin/env python

import requests
import sys
from optparse import OptionParser, BadOptionError, AmbiguousOptionError
from json import dumps


class PhiloLogicRequest(object):
    """
    Process a PhiloLogic request and save the full result set in a text file
    in JSON or tab delimited
    """
    
    def __init__(self, db_url=None, report=None, format="json", **args):
        self.db_url = db_url
        self.report = report
        self.philo_args = args
        self.query_params = {"format": "json"}
        self.query_params["report"] = report
        self.query_params.update(args)
        if "method" not in self.query_params:
            self.query_params["method"] = "proxy"
        if "results_per_page" not in self.query_params:
            self.query_params["results_per_page"] = 100
        if "q" not in self.query_params:
            self.query_params["q"] = ''
        self.results_per_page = self.query_params["results_per_page"]
        self.total_hits()
        print >> sys.stderr, "Total hits:", self.total
        
        ## Count number of queries needed to retrieve the full result set
        self.steps = self.total / self.results_per_page
        remainder = self.total % self.results_per_page
        if remainder:
            self.steps += 1
        print >> sys.stderr, "%d queries will be performed to retrieve the full result set" % self.steps
            
    def total_hits(self):
        r = requests.get(self.db_url + "/scripts/get_total_results.py", params=self.query_params)
        self.total = int(r.json())
    
    def query(self, params=None):
        if params == None:
            params = self.query_params
        response = requests.get(self.db_url + "/dispatcher.py", params=params)
        return response
    
    def concatenate_concordance(self):
        params = dict(self.query_params)
        self.results = {"results": []}
        for i in range(self.steps):
            start = i * self.results_per_page
            end = start + self.results_per_page - 1
            params["start"] = start
            params["end"] = end
            response = self.query(params=params)
            print >> sys.stderr, "Retrieving %s" % response.url
            for k, v in response.json().iteritems():
                if k == "results":
                    self.results["results"] += v
                    continue
                if k not in self.results:
                    self.results[k] = v

class PassThroughOptionParser(OptionParser):
    """
    An unknown option pass-through implementation of OptionParser.

    When unknown arguments are encountered, bundle with largs and try again,
    until rargs is depleted.  

    sys.exit(status) will still be called if a known argument is passed
    incorrectly (e.g. missing arguments or bad argument types, etc.)        
    """
    def _process_args(self, largs, rargs, values):
        while rargs:
            try:
                OptionParser._process_args(self,largs,rargs,values)
            except (BadOptionError,AmbiguousOptionError), e:
                largs.append(e.opt_str)

def parse_command_line(arguments):
    parser = PassThroughOptionParser()
    parser.add_option("-r", "--report", action="store", default="report", type="string", dest="report", help="select PhiloLogic search report")
    parser.add_option("-d", "--db-url", action="store", default="", type="string", dest="db_url", help="select database URL for search")
    
    ## Parse command-line arguments
    options, args = parser.parse_args(arguments)
    
    ## Parse all other options
    arg_dict = {}
    while args:
        key = args.pop(0).replace('-', '')
        val = args.pop(0)
        arg_dict[key] = val
    
    return options.db_url, options.report, arg_dict 


if __name__ == '__main__':
    db_url, report, query_args = parse_command_line(sys.argv[1:])
    philo_request = PhiloLogicRequest(report=report, db_url=db_url, **query_args)
    philo_request.concatenate_concordance()    