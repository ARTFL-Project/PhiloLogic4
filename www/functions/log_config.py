#!/usr/bin env python

import os
import logging
from logging import FileHandler, StreamHandler

path = os.getcwd().replace('functions', "").replace('scripts', '').replace('reports', '')

root = logging.getLogger()
root.setLevel(logging.INFO)
formatter = logging.Formatter('\n%(asctime)s ## %(levelname)s ##\n%(message)s\n')

## All info logging ##
#info_formatter = logging.Formatter('%(asctime)s %(message)s')
handler = FileHandler("%s/data/log/info.log" % path, "a")
handler.setLevel(0)
handler.setFormatter(formatter)
root.addHandler(handler)

## Error logging ##
error_formatter = logging.Formatter("%(message)s")
console_error_handler = StreamHandler()
console_error_handler.setFormatter(error_formatter)
handler = FileHandler("%s/data/log/error.log" % path, "a")
handler.setLevel(logging.ERROR)
handler.setFormatter(formatter)
root.addHandler(console_error_handler)
root.addHandler(handler)

## Usage logging ##
usage_formatter = logging.Formatter('%(asctime)s\t%(message)s\n')
handler = FileHandler('%s/data/log/usage.log' %path, "a")
handler.setFormatter(usage_formatter)
handler.setLevel(20)
root.addHandler(handler)
