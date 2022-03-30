#!/usr/bin/env python3
"""This script converts PhiloLogic 4.6 web_config.cfg files to 4.7"""


from builtins import AttributeError
import os
import sqlite3
import sys
from importlib_metadata import metadata

from philologic.Config import Config, WEB_CONFIG_DEFAULTS, WEB_CONFIG_HEADER
from philologic.utils import load_module
from philologic.utils import pretty_print
from black import format_str, FileMode


class CustomConfig(Config):
    def __str__(self):
        string = "\n".join([line.strip() for line in self.header.splitlines() if line.strip()]) + "\n\n"
        written_keys = []
        for key, value in self.defaults.items():
            if value["comment"]:
                string += "\n" + "\n".join(line.strip() for line in value["comment"].splitlines() if line.strip())
            if key == "aggregation_config":
                string += (
                    f"\n{key} = "
                    + "[{"
                    + """"field": "author", "object_level": "doc", "break_up_field": "title",
                        "field_citation": [citations["author"]], "break_up_field_citation": [
                        citations["title"], citations["pub_place"], citations["publisher"], citations["collection"],citations["year"]
                        ],"""
                    + "}, {"
                    + """"field": "title", "object_level": "doc", "field_citation": [citations["title"],
                        citations["pub_place"], citations["publisher"], citations["collection"], citations["year"]],"break_up_field": None,
                        "citation": citations["title"], "break_up_field_citation": None, """
                    + "}]"
                )
            else:
                string += "\n%s = %s\n" % (key, pretty_print(self.data[key]))
            written_keys.append(key)
        for key in self.data:
            if key not in written_keys:
                string += "\n%s = %s\n" % (key, pretty_print(self.data[key]))
                written_keys.append(key)
        return string


def MakeWebConfig(path, **extra_values):
    """Build web_config with non-default arguments"""
    web_config = CustomConfig(path, WEB_CONFIG_DEFAULTS, header=WEB_CONFIG_HEADER)
    if extra_values:
        for key, value in extra_values.items():
            web_config[key] = value
    return web_config


def get_time_series_dates(toms_path):
    # Find default start and end dates for times series
    with sqlite3.connect(toms_path) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT min(year), max(year) FROM toms")
            min_year, max_year = cursor.fetchone()
            try:
                start_date = int(min_year)
            except (TypeError, ValueError):
                start_date = 0
            try:
                end_date = int(max_year)
            except (TypeError, ValueError):
                end_date = 2100
        except sqlite3.OperationalError:
            return 0, 0
    return start_date, end_date


def citations_filter(citations):
    new_citations = []
    for citation in citations:
        try:
            del citation["separator"]
        except KeyError:
            pass
        new_citations.append(citation)
    return new_citations


def convert_landing_page_browsing(landing_page):
    new_landing_page = []
    for l in landing_page:
        l["citation"] = citations_filter(l["citation"])
        new_landing_page.append(l)
    return new_landing_page


def convert_web_config(web_config_path, philo_db):
    # Deal with TOMS db changes
    data_dir = os.path.join(philo_db, "data")
    toms_path = os.path.join(data_dir, "toms.db")

    # Regenerate new WebConfig file
    old_config = load_module("old_config", web_config_path)

    start_date, end_date = get_time_series_dates(toms_path)
    metadata_input_style = {**old_config.metadata_input_style, "year": "int"}
    config_values = {
        "dbname": old_config.dbname,
        "metadata": old_config.metadata,
        "facets": old_config.facets,
        "time_series_start_end_date": {"start_date": start_date, "end_date": end_date},
        "search_examples": old_config.search_examples,
        "metadata_input_style": metadata_input_style,
        "kwic_metadata_sorting_fields": old_config.kwic_metadata_sorting_fields,
        "kwic_bibliography_fields": old_config.kwic_bibliography_fields,
        "concordance_biblio_sorting": old_config.concordance_biblio_sorting,
        "page_images_url_root": old_config.page_images_url_root,
        "link_to_home_page": old_config.link_to_home_page,
        "metadata_aliases": old_config.metadata_aliases,
        "stopwords": old_config.stopwords,
        "time_series_interval": old_config.time_series_interval,
        "header_in_toc": old_config.header_in_toc,
        "default_landing_page_browsing": convert_landing_page_browsing(old_config.default_landing_page_browsing),
        "default_landing_page_display": old_config.default_landing_page_display,
        "simple_landing_citation": old_config.simple_landing_citation,
        "dico_letter_range": old_config.dico_letter_range,
        "concordance_citation": citations_filter(old_config.concordance_citation),
        "bibliography_citation": citations_filter(old_config.bibliography_citation),
        "navigation_citation": citations_filter(old_config.navigation_citation),
        "kwic_bibliography_fields": old_config.kwic_bibliography_fields,
        "concordance_biblio_sorting": old_config.concordance_biblio_sorting,
        "kwic_metadata_sorting_fields": old_config.kwic_metadata_sorting_fields,
        "time_series_year_field": old_config.time_series_year_field,
        "page_image_extension": old_config.page_image_extension,
        "search_syntax_template": old_config.search_syntax_template or "default",
        "metadata_choice_values": old_config.metadata_dropdown_values,
        "dictionary": old_config.dictionary,
        "landing_page_browsing": old_config.landing_page_browsing,
    }
    # Check for the presence of some new config options
    try:
        config_values["table_of_contents_citation"] = citations_filter(old_config.table_of_contents_citation)
    except AttributeError:
        config_values["table_of_contents_citation"] = WEB_CONFIG_DEFAULTS["table_of_contents_citation"]["value"]
    try:
        config_values["external_page_images"] = old_config.external_page_images
    except AttributeError:
        config_values["external_page_images"] = WEB_CONFIG_DEFAULTS["external_page_images"]["value"]
    try:
        config_values["skip_table_of_contents"] = old_config.skip_table_of_contents
    except AttributeError:
        config_values["skip_table_of_contents"] = False
    try:
        config_values["query_parser_regex"] = old_config.query_parser_regex
    except AttributeError:
        config_values["query_parser_regex"] = WEB_CONFIG_DEFAULTS["query_parser_regex"]["value"]
    try:
        config_values["report_error_link"] = old_config.report_error_link
    except AttributeError:
        config_values["report_error_link"] = WEB_CONFIG_DEFAULTS["report_error_link"]["value"]
    try:
        config_values["concordance_formatting_regex"] = old_config.concordance_formatting_regex
    except AttributeError:
        config_values["concordance_formatting_regex"] = WEB_CONFIG_DEFAULTS["concordance_formatting_regex"]["value"]
    try:
        config_values["kwic_formatting_regex"] = old_config.kwic_formatting_regex
    except AttributeError:
        config_values["kwic_formatting_regex"] = WEB_CONFIG_DEFAULTS["kwic_formatting_regex"]["value"]
    try:
        config_values["navigation_formatting_regex"] = old_config.navigation_formatting_regex
    except AttributeError:
        config_values["navigation_formatting_regex"] = WEB_CONFIG_DEFAULTS["navigation_formatting_regex"]["value"]
    os.system(f"mv {web_config_path} {web_config_path}_old")
    new_config = MakeWebConfig(web_config_path, **config_values)
    with open(web_config_path, "w") as output_file:
        print(format_str(str(new_config), mode=FileMode()), file=output_file)


if __name__ == "__main__":
    web_config_path = sys.argv[1]
    philo_db = sys.argv[2]
    convert_web_config(web_config_path, philo_db)
