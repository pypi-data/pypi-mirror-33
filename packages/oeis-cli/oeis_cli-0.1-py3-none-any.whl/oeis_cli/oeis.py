# Copyright (c) 2018 Dominic Benjamin
#
# The author is not affiliated with the On-Line Encyclopedia of Integer
# Sequences (OEIS).
#
# For more information on OEIS, visit https://oeis.org/

import argparse
import urllib.request

ERROR_MESSAGE = ("An error occured. Please try again, or submit the sequence "
                  "you tried to https://github.com/dfbenjamin/oeis_cli/"
                )

""" Format url for oeis search from given ints. """
def format_url(ints, unordered):
    separator = '+' if unordered else ','
    return "https://oeis.org/search?fmt=text&q=" + separator.join(map(str, ints))

""" Extract sequence terms from line containing them. """
def format_terms(line):
    res = line[11:]
    if res[-1] == ',': res = res[:-1]
    return res

""" Extrat sequence code and name from line containing them. """
def format_title(line):
    return line[3:10] + ": " + line[11:]

""" Extract information from search result. """
def format_data(data):
    if "crawling" in next(data): return "Too many requests - slow down!"
    next(data); next(data)
    identifier = next(data)
    if "No results" in identifier: return "No sequence found."
    if "Too many results" in identifier: return "Too many results."
    next(data); next(data)
    terms = format_terms(next(data))
    x = next(data)
    while len(x) < 2 or x[1] != 'N' : x = next(data)
    title = format_title(x)
    return title + "\n" + terms

""" Trim useless characters from each line. """
def fix_line(line):
    return str(line)[2:-3]

""" Perform search for ints, and return formatted result. """
def search(ints, unordered):
    if len(ints) > 20: return "Too many terms - use 20 or less."
    url = format_url(ints, unordered)
    data = urllib.request.urlopen(url)
    return format_data(map(fix_line, data))

def main():
    parser = argparse.ArgumentParser(description='Lookup an integer sequence.')
    parser.add_argument('integers', type=int, nargs='+')
    parser.add_argument('--unordered', help='ignore order of terms')
    args = parser.parse_args()
    print(search(args.integers, args.unordered))

if __name__ == "__main__":
    main()

