---
title: How to customize bibliographic citations
---

In order to customize bibliographic citations, you need to use a custom version of the citations function from the main PhiloLogic library. Note that you can control for which reporting function this custom citation is active.

## Setting up custom functions

Inside the database directory, you will find a `custom_functions/` directory. The first step is to determine for which reporting function (concordance, kwic, collocation, time series, table of contents, text navigation) you whish to enable the new citation. We will take the case of text navigation:
1) Copy the `navigation.py` file from the installation directory of PhiloLogic4 (you will find it (as well as other reports) in `python/philologic/runtime/reports/`) to the `custom_functions` directory. 
2) Copy the `citations.py`file from `python/philologic/runtime/`to the `custom_functions` directory. 
3) Add the following to the `custom_functions/__init__.py`file to import the navigation reporting function:
```python
from .navigation import generate_text_object
```
4) Edit the `navigation.py` file. Change the following in order to import the local version of `citations.py`:

from 
```python 
from philologic.runtime.citations import citation_links, citations
```
to 
```python
from .citations import citation_links, citations
```
5) Finally, edit the citations functions (and all other associated functions with the `citations.py` file) to suit your needs.


#### In order to apply the same custom citation to other reports, just copy the other reports you need (such as in step 2), and edit the `__init__.py` accordingly (like in step 3)
