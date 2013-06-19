#!/usr/bin/env python

def custom_format():
    """This is where custom formatting can be done for display purposes"""
    ## By default, we'd leave format as an empty dict
    format = {}
    format["p"] = "\n<p/>"
    format["/p"] = ""
    format["br"] = "<br/>\n"
    format["/br"] = ""
    format["span"] = "<span>"
    format["/span"] = "</span>"
    format["b"] = "<b>"
    format["/b"] = "</b>"
    format["/a"] = "</a>"
    format["s"] = ""
    format["/s"] = ""
    format["l"] = ""
    format["/l"] = "<br/>\n"
    format["/ab"] = "<br/>\n"
    format["speaker"] = "<p><b>"
    format["/speaker"] = "</b></p>"
    format["stage"] = "<br/><i>"
    format["/stage"] = "</i>"
    format["head"] = "<p/><b>"
    format["/head"] = "</b><br/>"
    format["i"] = "<i>"
    format["/i"] = "</i>"
    format["sc"] = "<span class='small-caps'>"
    format["/sc"] = "</span>"
    format["scx"] = "<span class='small-caps'>"
    format["/scx"] = "</span>"
    return format
