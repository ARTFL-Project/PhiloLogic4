#!/usr/bin/env python3
from distutils.core import setup

setup(name = "philologic",
      version = "5.0alpha",
      author = "The ARTFL Project",
      author_email = "artfl@artfl.uchicago.edu",
      packages = ["philologic", "philologic.runtime", "philologic.utils", "philologic.runtime.reports"],
      scripts=["scripts/philoload5"]
     )
