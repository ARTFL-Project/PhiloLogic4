#!/usr/bin/env python3
"""This script converts PhiloLogic 4.6 web_config.cfg files to 4.7"""


import os
import sqlite3
import sys

from philologic.Config import Config, WEB_CONFIG_DEFAULTS, WEB_CONFIG_HEADER
from philologic.utils import load_module
from philologic.utils import pretty_print
from black import format_str, FileMode


DEFAULT_CONFIG_VALUES = [
    "default_landing_page_display",
    "simple_landing_citation",
    "dico_letter_range",
    "kwic_bibliography_fields",
    "concordance_biblio_sorting",
    "time_series_year_field",
    "page_image_extension",
    "search_syntax_template",
    "metadata_choice_values",
    "dictionary",
    "dictionary_bibliography",
    "landing_page_browsing",
    "dbname",
    "metadata",
    "facets",
    "search_examples",
    "kwic_bibliography_fields",
    "concordance_biblio_sorting",
    "metadata_aliases",
    "header_in_toc",
    "external_page_images",
    "skip_table_of_contents",
    "query_parser_regex",
    "report_error_link",
    "concordance_formatting_regex",
    "kwic_formatting_regex",
    "navigation_formatting_regex",
    "kwic_metadata_sorting_fields",
    "page_images_url_root",
    "time_series_interval",
    "stopwords",
    "link_to_home_page",
]


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
    error = False
    for l in landing_page:
        try:
            l["citation"] = citations_filter(l["citation"])
        except KeyError:
            error = True
            break
        new_landing_page.append(l)
    if error is True:
        return WEB_CONFIG_DEFAULTS["default_landing_page_browsing"]["value"]
    return new_landing_page


def convert_web_config(web_config_path, philo_db):
    # Deal with TOMS db changes
    data_dir = os.path.join(philo_db, "data")
    toms_path = os.path.join(data_dir, "toms.db")

    # Regenerate new WebConfig file
    old_config = load_module("old_config", web_config_path)
    start_date, end_date = get_time_series_dates(toms_path)
    config_values = {
        "time_series_start_end_date": {"start_date": start_date, "end_date": end_date},
    }
    for config_value in DEFAULT_CONFIG_VALUES:
        try:
            if config_value in (
                "concordance_citation",
                "bibliography_citation",
                "navigation_citation",
                "table_of_contents_citation",
            ):
                config_values[config_value] = citations_filter(getattr(old_config, config_value))
            elif config_value == "default_landing_page_browsing":
                config_values[config_value] = convert_landing_page_browsing(old_config.default_landing_page_browsing)
            elif config_value == "metadata_input_style":
                config_values["metadata_input_style"] = {**old_config.metadata_input_style, "year": "int"}
            else:
                config_values[config_value] = getattr(old_config, config_value)
        except AttributeError:
            config_values["external_page_images"] = WEB_CONFIG_DEFAULTS[config_value]["value"]
    if config_value["dictionary"] is True:
        if "head" not in config_value["metadata"]:
            config_value["metadata"] = ["head", *config_value["metadata"]]
    os.system(f"mv {web_config_path} {web_config_path}_old")
    new_config = MakeWebConfig(web_config_path, **config_values)
    with open(web_config_path, "w") as output_file:
        print(format_str(str(new_config), mode=FileMode()), file=output_file)
    os.system(f"chmod 775 {web_config_path}")


if __name__ == "__main__":
    web_config_path = sys.argv[1]
    philo_db = sys.argv[2]
    convert_web_config(web_config_path, philo_db)
