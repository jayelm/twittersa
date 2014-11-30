"""
BC CSCI339 NLP Final Project
TwitterSA: Sentiment Analysis for Twitter

Jesse Mu
"""

import os
import logging
from flask import Flask, render_template, request
app = Flask(__name__)

import tweepy


@app.route('/')
def index():
    """Return an index page."""
    return render_template('index.html')


@app.route('/search')
def search():
    """Display sentiment on tweets for a given search."""
    q = request.args.get('q', '')
    if not q:
        app.logger.info(
            "Requested /search endpoint with invalid parameters {}".format(
                str(request.args))
        )
        return render_template('error.html', error="Invalid search query")
    # FIXME: only 100 tweets is interesting and (probably bad), it results in
    # a pretty low sample size based on relevancy, and
    # (for popular search terms) changes very, very rapidly.
    # Options:
    # 1. Make multiple api calls
    #   - Disadvantages: ++load times, ++api calls, dealing with overlaps
    results = api.search(q=q, count=100)
    return render_template('search.html', results=results)


@app.route('/user')
def user():
    """Display historical sentiment of a given user's tweets."""
    username = request.args.get('username', '')
    if not username:
        app.logger.info(
            "Requested /user endpoint with invalid parameters {}".format(
                str(request.args))
        )
        return render_template('error.html', error="Invalid username")
    timeline = api.user_timeline(
        screen_name=username,
        include_rts=True,
        count=3200  # 2014-11-30: 3200 tweets is the max
    )
    return render_template('user.html', username=username, timeline=timeline)


@app.before_first_request
def setup_logging():
    """In production, make sure we log to stderr."""
    if not app.debug:
        logger_handler = logging.StreamHandler()
        logger_handler.setFormatter(
            logging.Formatter(
                '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
            )
        )
        app.logger.addHandler(logger_handler)
        app.logger.setLevel(logging.INFO)


def tweepy_init():
    """
    Create an authorized Tweepy API instance with API keys in the environment
    We only require the Consumer Key and the Consumer Secret because we only
    use app-level endpoints and they give us higher rate limits.
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
        '-d', '--debug', action='store_true',
        help='run application in debug mode'
    )
    args = parser.parse_args()

    app.debug = args.debug
    app.run()
