"""Runtime exports"""

from philologic.runtime.access_control import check_access, login_access
from philologic.runtime.find_similar_words import find_similar_words
from philologic.runtime.FragmentParser import FragmentParser
from philologic.runtime.get_text import get_concordance_text, get_tei_header
from philologic.runtime.pages import page_interval
from philologic.runtime.query_parser import parse_query
from philologic.runtime.reports import (
    bibliography_results,
    collocation_results,
    concordance_results,
    filter_words_by_property,
    frequency_results,
    generate_text_object,
    generate_time_series,
    generate_toc_object,
    generate_word_frequency,
    get_start_end_date,
    kwic_hit_object,
    kwic_results,
    group_by_metadata,
    group_by_range,
    landing_page_bibliography,
)
from philologic.runtime.web_config import WebConfig
from philologic.runtime.wsgi_handler import WSGIHandler
