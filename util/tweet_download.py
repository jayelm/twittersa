"""
NOTE: This is no longer used in the actual web app, since I grab automatically
labeled tweets from Sentiment140. But, I keep it around for convenience.

A script to download tweets in a .tsv of the form

Status ID      User ID     Sentiment
====================================

used mainly to get tweets from the SemEval Twitter sentiment corpus.

We use plain old HTML parsing to avoid API rate limits.

Inspired from aritter/twitter_download

Jesse Mu
"""

import requests
from bs4 import BeautifulSoup
import csv
import pickle  # Standard pickle for unicode support
import sys


def scrape_tweets(files, quiet=False):
    """
    Scrape tweets from a list of .tsv files with the aforementioned format.

    Returns an association list of tweets and their sentiments.

    Only grabs tweets labeled as "positive" or "negative" for usage in a
    binary classifier.
    """
    tweets = []
    total_tweets = 0
    for filename in files:
        with open(filename, 'r') as f:
            reader = csv.reader(f, delimiter='\t')
            rows = list(reader)

        if not quiet:
            print "{}: {} tweets".format(filename, len(rows))
        for sid, uid, sentiment in rows:
            total_tweets += 1
            print total_tweets

            if not (sentiment == 'positive' or sentiment == 'negative'):
                if not quiet:
                    print (
                        "Skipping neutral tweet with uid {} and sid {}".format(
                            uid, sid
                        )
                    )
                continue

            url = 'https://twitter.com/{}/status/{}'.format(uid, sid)
            r = requests.get(url)
            soup = BeautifulSoup(r.text)

            tweet_text_paragraphs = soup.find_all('p', {'class': 'tweet-text'})

            if len(tweet_text_paragraphs) > 1:
                original_tweet_div = soup.find(
                    'div', {'class': 'js-original-tweet'}
                )
                tweet_text_paragraphs = original_tweet_div.find_all(
                    'p', {'class': 'tweet-text'}
                )

            if not tweet_text_paragraphs:
                if not quiet:
                    print "Can't find tweet with uid {} and sid {}".format(
                        uid, sid
                    )
                continue

            tweet_text = tweet_text_paragraphs[0].text
            tweets.append([tweet_text, sentiment])

    print "Got {} tweets out of {}".format(len(tweets), total_tweets)
    return tweets


def serialize(filename, tweets, quiet=False):
    """Output tweet lists to a file with pickle."""
    if filename == '-' or not filename:
        if not quiet:  # Not sure why someone would specify verbose for stdout
            print "Writing to stdout"
        pickle.dump(tweets, sys.stdout)
    else:
        if not quiet:
            print "Writing to {}".format(filename)
        with open(filename, 'w') as fout:
            pickle.dump(tweets, fout)


def handle_filename(filename):
    """Prepare the filename - if directory specified, add default name"""
    if filename[-1] == '/':
        filename += 'noslang.p'
    return filename

if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument(
        'files', nargs='+',
        help=".tsv files containing status id, user id, and sentiment"
    )
    parser.add_argument(
        '-o', '--output', nargs="?", const='lib/tweets.p', default='-',
        help="specify output file (defaults to lib/tweets.p "
             "if specified without file or stdout if not specified)"
    )
    parser.add_argument(
        # Quiet is used here because default behavior should be to output
        # information about missed tweets
        '-q', '--quiet', action='store_true',
        help='be quiet'
    )

    args = parser.parse_args()

    filename = handle_filename(args.output)

    tweets = scrape_tweets(args.files, args.quiet)
    serialize(filename, tweets, args.quiet)
