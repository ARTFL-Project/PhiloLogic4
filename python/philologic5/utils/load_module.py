#!/usr/bin/env python3
"""Load Python source file"""

from importlib.machinery import SourceFileLoader
from importlib.util import spec_from_loader, module_from_spec


def load_module(module_name, path):
    """Load arbitrary Python source file"""
    loader = SourceFileLoader(module_name, path)
    spec = spec_from_loader(loader.name, loader)
    module = module_from_spec(spec)
    loader.exec_module(module)
    return module
