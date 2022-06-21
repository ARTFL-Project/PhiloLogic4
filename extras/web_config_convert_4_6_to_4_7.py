#!/usr/bin/env python3
"""This script converts PhiloLogic 4.6 web_config.cfg files to 4.7"""


import os
import sqlite3
import sys

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
    for config_name, config_value in WEB_CONFIG_DEFAULTS.items():
        try:
            if config_name in (
                "concordance_citation",
                "bibliography_citation",
                "navigation_citation",
                "table_of_contents_citation",
            ):
                config_values[config_name] = citations_filter(getattr(old_config, config_name))
            elif config_name == "default_landing_page_browsing":
                config_values[config_name] = convert_landing_page_browsing(old_config.default_landing_page_browsing)
            elif config_name == "metadata_input_style":
                config_values["metadata_input_style"] = {**old_config.metadata_input_style, "year": "int"}
            elif config_name == "metadata_choice_values":
                config_values[config_name] = old_config.metadata_dropdown_values
            elif config_name == "search_reports":
                config_values[config_name] = (
                    old_config.search_reports[:2] + ["aggregation"] + old_config.search_reports[2:]
                )
            elif config_name == "dictionary_lookup":
                config_values[config_name] = {"url_root": "", "keywords": False}
            else:
                config_values[config_name] = getattr(old_config, config_name)
        except AttributeError:
            config_values["external_page_images"] = config_value["value"]
    if config_values["dictionary"] is True:
        if "head" not in config_values["metadata"]:
            config_values["metadata"] = ["head", *config_values["metadata"]]
    os.system(f"mv {web_config_path} {web_config_path}_old")
    new_config = MakeWebConfig(web_config_path, **config_values)
    with open(web_config_path, "w") as output_file:
        print(format_str(str(new_config), mode=FileMode()), file=output_file)
    os.system(f"chmod 775 {web_config_path}")


if __name__ == "__main__":
    web_config_path = sys.argv[1]
    philo_db = sys.argv[2]
    print(f"Converting {web_config_path}...", end="")
    convert_web_config(web_config_path, philo_db)
    print("done.")
