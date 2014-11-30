"""
BC CSCI339 NLP Final Project
TwitterSA: Sentiment Analysis for Twitter

TODO: Get logging working with Foreman and Heroku

Jesse Mu
"""

from flask import Flask, render_template
app = Flask(__name__)

import tweepy


@app.route('/')
def hello_world():
    """Return an index page."""
    tweets = api.search(q="hello")
    return render_template('index.html', tweets=tweets)


def parser_init():
    """Initiate an ArgumentParser with running options."""
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument(
        '-d', '--debug', action='store_true',
        help="enable debug logging"
    )
    parser.add_argument(
        # Exactly two keys requirement is enforced when getting Twitter Keys
        '-k', '--keys', nargs='+', default=None,
        help="manually specify Twitter API keys. "
             "First key must be Consumer Key, second must be Consumer Secret"
    )
    return parser


def get_twitter_keys(args):
    """
    Get Twitter keys from either environment variables or command line.

    Quits script with error message on misconfigured variables.
    """
    import os
    import sys
    if args.keys is None:
        consumer_key = os.environ.get('TWITTER_CONSUMER_KEY')
        consumer_secret = os.environ.get('TWITTER_CONSUMER_SECRET')
        if not (consumer_key and consumer_secret):
            sys.exit("Could not find Twitter API environment variables, "
                     "ensure TWITTER_CONSUMER_KEY and TWITTER_CONSUMER_SECRET "
                     "are defined")
    elif args.keys:
        if len(args.keys) != 2:
            sys.exit("TwitterSA.py: error: not enough keys: "
                     "Consumer Key and Consumer Secret required")
        consumer_key = args.keys[0]
        consumer_secret = args.keys[1]
    else:
        sys.exit("TwitterSA.py: error: no keys specified with --keys flag")
    return consumer_key, consumer_secret


def tweepy_init(consumer_key, consumer_secret):
    """
    Create an authorized Tweepy API instance with the given API keys
    We only require the Consumer Key and the Consumer Secret because the
    application only requires app-based authentication.
    """
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    api = tweepy.API(auth)
    return api

if __name__ == '__main__':
    parser = parser_init()
    args = parser.parse_args()

    consumer_key, consumer_secret = get_twitter_keys(args)

    api = tweepy_init(consumer_key, consumer_secret)

    app.debug = args.debug
    app.run()
