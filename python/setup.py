#!/usr/bin/env python3
from distutils.core import setup

setup(
    name="philologic5",
    version="5.0a1",
    author="The ARTFL Project",
    author_email="artfl@artfl.uchicago.edu",
    packages=[
        "philologic5",
        "philologic5.runtime",
        "philologic5.utils",
        "philologic5.runtime.reports",
        "philologic5.loadtime",
    ],
    scripts=["scripts/philoload5"],
    install_requires=[
        "lxml",
        "python-levenshtein",
        "natsort",
        "multiprocess",
        "tqdm",
        "sklearn",
        "numpy",
        "python-rapidjson",
        "black",
    ],
)
