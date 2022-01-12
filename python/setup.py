#!/usr/bin/env python3
from distutils.core import setup

setup(
    name="philologic",
    version="4.7b3",
    author="The ARTFL Project",
    author_email="clovisgladstone@artfl.uchicago.edu",
    packages=[
        "philologic",
        "philologic.runtime",
        "philologic.utils",
        "philologic.runtime.reports",
        "philologic.loadtime",
    ],
    scripts=["scripts/philoload4"],
    install_requires=[
        "regex",
        "lxml",
        "python-levenshtein",
        "natsort",
        "multiprocess",
        "tqdm",
        "sklearn",
        "numpy",
        "orjson",
        "black",
        "msgpack",
        "lz4",
    ],
)
