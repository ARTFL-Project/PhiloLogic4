#!/usr/bin/env python3
from distutils.core import setup

with open("README", encoding="utf8") as input_file:
    long_description = input_file.read()

setup(
    name="philologic",
    version="4.7.1.3",
    author="Clovis Gladstone",
    author_email="clovisgladstone@artfl.uchicago.edu",
    description="A concordance search engine for TEI-XML",
    long_description=long_description,
    url="https://github.com/ARTFL-Project/PhiloLogic4",
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
        "orjson",
        "black",
        "msgpack",
        "unidecode",
        "lz4",
    ],
    python_requires=">=3.8",
)
