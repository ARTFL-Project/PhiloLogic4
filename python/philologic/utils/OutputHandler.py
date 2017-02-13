#!/usr/bin/env python3


import sys


class OutputHandler(object):
    """Modifies the default sys.stdout in several ways:
    - unbuffers sys.stdout
    - adds ability to print to file and console with one print statement
    - adds ability to disable logging or printing to console"""

    def __init__(self, console=True, log=False):
        self.stream = sys.stdout
        self.console = console
        if log:
            self.log = open(log, 'w')
        else:
            self.log = False

    def write(self, data):
        if self.console:
            self.stream.write(data)
            self.stream.flush()
        if self.log:
            self.log.write(data)

    def __getattr__(self, attr):
        return getattr(self.stream, attr)
