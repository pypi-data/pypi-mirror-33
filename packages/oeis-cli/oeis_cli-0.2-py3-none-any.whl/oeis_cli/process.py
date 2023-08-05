# Copyright (c) 2018 Dominic Benjamin
#
# The author is not affiliated with the On-Line Encyclopedia of Integer
# Sequences (OEIS).
#
# For more information on OEIS, visit https://oeis.org/
#
# Logic for formatting the data given by a search.

def format_terms(line):
    res = line[11:] # Trim OEIS code and tag
    if res[-1] == ',': res = res[:-1] # Trim trailing comma
    return res

def format_title(line):
    return line[3:10] + ": " + line[11:] # Trim tag

def format_data(data):
    if "crawling" in next(data): return "Too many requests - slow down!"
    next(data); next(data) # Useless lines
    identifier = next(data) # Contains information on search status
    if "No results" in identifier: return "No sequence found."
    if "Too many results" in identifier: return "Too many results."
    next(data); next(data) # Useless lines
    terms = format_terms(next(data)) # Contains first terms
    x = next(data) # Skip past terms until we find the name
    while len(x) < 2 or x[1] != 'N' : x = next(data)
    title = format_title(x)
    return title + "\n" + terms


