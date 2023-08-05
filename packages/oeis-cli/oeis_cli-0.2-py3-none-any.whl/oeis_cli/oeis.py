# Copyright (c) 2018 Dominic Benjamin
#
# The author is not affiliated with the On-Line Encyclopedia of Integer
# Sequences (OEIS).
#
# For more information on OEIS, visit https://oeis.org/
#
# Main logic - parsing arguments and calling relevant functionality.

import argparse
import oeis_cli.process as process
import oeis_cli.search as search

def main():
    parser = argparse.ArgumentParser(description='Lookup an integer sequence.')
    search_terms = parser.add_mutually_exclusive_group(required=True)
    search_terms.add_argument('--name', '-n', help='name of sequence to search for')
    search_terms.add_argument('terms', type=int, nargs='*', default=[],
                               help='integer terms to search for')
    parser.add_argument('--unordered', '-u',
                        help='ignore order of terms',
                        action='store_true')
    args = parser.parse_args()
    data = (search.search_name(args.name) if args.name
            else search.search_terms(args.terms, args.unordered))
    print(process.format_data(data))

