from philologic.app.access_control import check_access, login_access
from philologic.app.find_similar_words import find_similar_words
from philologic.app.FragmentParser import FragmentParser
from philologic.app.get_text import get_concordance_text
from philologic.app.landing_page import (group_by_metadata, group_by_range,
                                         landing_page_bibliography)
from philologic.app.pages import page_interval
from philologic.app.query_parser import parse_query
from philologic.app.reports import (bibliography_results, collocation_results,
                                    concordance_results,
                                    filter_words_by_property,
                                    frequency_results, generate_text_object,
                                    generate_time_series, generate_toc_object,
                                    generate_word_frequency,
                                    get_start_end_date, kwic_hit_object,
                                    kwic_results)
from philologic.app.web_config import WebConfig
from philologic.app.wsgi_handler import WSGIHandler
