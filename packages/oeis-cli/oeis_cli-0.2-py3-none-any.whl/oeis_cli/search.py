# Copyright (c) 2018 Dominic Benjamin
#
# The author is not affiliated with the On-Line Encyclopedia of Integer
# Sequences (OEIS).
#
# For more information on OEIS, visit https://oeis.org/
#
# Logic for performing a search.

import urllib.request

URL_HEAD = "https://oeis.org/search?fmt=text&q="

def format_url_terms(terms, unordered):
    separator = '+' if unordered else ','
    return URL_HEAD + separator.join(map(str, terms))

def format_url_name(name):
    return URL_HEAD + name

def fix_line(line):
    return str(line)[2:-3] # Remove trailing newline and 'b at start

def search_terms(terms, unordered):
    url = format_url_terms(terms, unordered)
    return map(fix_line, urllib.request.urlopen(url))

def search_name(name):
    url = format_url_name(name)
    return map(fix_line, urllib.request.urlopen(url))
