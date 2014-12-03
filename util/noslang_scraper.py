"""
This script grabs data from the slang dictionary
http://www.noslang.com/dictionary and converts it into a python dictionary for
serialization.

Obviously contingent on noslang's format consistency.

Jesse Mu
"""

from bs4 import BeautifulSoup
import requests
import pickle  # Standard pickle for unicode support
import sys

NOSLANG_URL = "http://www.noslang.com/dictionary/{}/"


def scraper(verbose=False):
    """Return a dictionary containing abbrevations from noslang."""
    noslang_dict = {}

    for letter in '1abcdefghijklmnopqrstuvwxyz':
        url = NOSLANG_URL.format(letter)
        if verbose:
            print "Parsing url {}".format(url)
        r = requests.get(url)
        soup = BeautifulSoup(r.text)
        tables = soup.find_all('table')
        assert len(tables) == 2, "format discrepancy: > 2 tables on page"
        # Get second table
        table = tables[1]
        tabletext = str(table)
        # Check to make (reasonably) sure this is the correct table
        assert '<a name=' in tabletext and '<abbr title=' in tabletext, \
            """format discrepancy: this doesn't seem to be an abbrevation table
            (or format has changed)!"""
        # noslang table has information in attributes in each dt
        dts = table.find_all('dt')
        abbrevations = [(dt.a['name'], dt.abbr['title']) for dt in dts]
        noslang_dict.update(dict(abbrevations))

    return noslang_dict


def serialize(filename, dictionary, verbose=False):
    """Output to a file or stdout with pickle."""
    if filename == '-' or not filename:
        if verbose:  # Not sure why someone would specify verbose for stdout
            print "Writing to stdout"
        pickle.dump(dictionary, sys.stdout)
    else:
        if verbose:
            print "Writing to {}".format(filename)
        with open(filename, 'w') as fout:
            pickle.dump(dictionary, fout)


def handle_filename(filename):
    """Prepare the filename - if directory specified, add default name"""
    if filename[-1] == '/':
        filename += 'noslang.pickle'
    return filename

if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument(
        '-o', '--output', nargs="?", const='lib/noslang.pickle', default='-',
        help="specify output file (defaults to lib/noslang.pickle "
             "if specified without file or stdout if not specified)"
    )
    parser.add_argument(
        # Verbose is used here because default behavior should be silent
        '-v', '--verbose', action='store_true',
        help="be verbose"
    )

    args = parser.parse_args()

    filename = handle_filename(args.output)

    noslang_dict = scraper(args.verbose)
    serialize(filename, noslang_dict, args.verbose)
