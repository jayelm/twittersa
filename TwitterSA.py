"""
BC CSCI339 NLP Final Project
TwitterSA: Sentiment Analysis for Twitter

TODO: Get logging working with Foreman and Heroku

Jesse Mu
"""

import os
import logging
from flask import Flask, render_template
app = Flask(__name__)

import tweepy


@app.before_first_request
def setup_logging():
    if not app.debug:
        # In production, make sure we log to stderr
        app.logger.addHandler(logging.StreamHandler())
        app.logger.setLevel(logging.INFO)


@app.route('/')
def hello_world():
    """Return an index page."""
    tweets = api.search(q="hello")
    return render_template('index.html', tweets=tweets)


def tweepy_init():
    """
    Create an authorized Tweepy API instance with API keys in the environment
    We only require the Consumer Key and the Consumer Secret because the
    application only requires app-based authentication.
    """
    consumer_key = os.environ['TWITTER_CONSUMER_KEY']
    consumer_secret = os.environ['TWITTER_CONSUMER_SECRET']
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    api = tweepy.API(auth)
    return api


api = tweepy_init()

if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument(
        '-d', '--debug', action='store_const',
        help='run application in debug mode'
    )
    args = parser.parse_args()

    app.debug = args.debug
    app.run()
