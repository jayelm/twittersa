# -*- coding: utf-8 -*-
"""
BC CSCI339 NLP Final Project
Twittersa: Sentiment Analysis for Twitter

Jesse Mu
"""

import os
import logging
from flask import Flask, render_template, request
app = Flask(__name__)

import tweepy
import sentiment.classifiers as sa
from dateutil.relativedelta import relativedelta

USER_API_CALLS = 2


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
    # User search
    if q.startswith('@'):
        return user(q)
    return render_template(
        'error.html',
        error="Invalid user - make sure to use use @"
    )


def user(username):
    """Display historical sentiment of a given user's tweets."""
    global_timeline = []
    for x in range(USER_API_CALLS):  # Nunmber of tweets is 200 * this num
        # TODO pagination might be easier
        timeline = api.user_timeline(
            screen_name=username,
            include_rts=True,
            result_type='mixed',
            # Get up to the last id polled
            max_id=global_timeline[-1].id - 1 if global_timeline else None,
            count=200  # 200 is the max for a single API call
        )
        global_timeline.extend(timeline)
        # app.logger.warn([t.created_at for t in timeline])
    global_timeline = global_timeline[::-1]
    # app.logger.warn([t.created_at for t in global_timeline])
    tweetsents = classifier.predict_many(global_timeline)
    data, tweet_bins = transform_timeline(tweetsents)
    return render_template(
        'user.html',
        username=username,
        data=data,
        # This reverse is mirrored in data.labels|reverse in the template
        tweet_bins=tweet_bins[::-1]
    )


def transform_timeline(tweetsents):
    tweetsents.sort()

    min_date = tweetsents[0].tweet.created_at
    min_date = min_date.replace(day=1, hour=0, minute=0, second=0)
    max_date = tweetsents[-1].tweet.created_at + relativedelta(months=+1)
    max_date = max_date.replace(day=1, hour=0, minute=0, second=0)

    r = relativedelta(max_date, min_date)

    months_diff = (r.years * 12) + r.months
    if months_diff < 5:  # A lot of data, we can use weeks
        # isocalendar gets number of week
        max_week = max_date.isocalendar()[1]
        min_week = min_date.isocalendar()[1]
        weeks_diff = max_week - min_week
        # If negative, there's a year offset - fix it
        if weeks_diff < 0:
            weeks_diff = 52 + max_week - min_week
        app.logger.warn(weeks_diff)
        dates = [add_weeks(min_date, x) for x in range(0, weeks_diff)]
        human_dates = [d.strftime('%b %d') for d in dates]
    else:
        # Stick to months
        dates = [add_months(min_date, x) for x in range(0, months_diff)]
        human_dates = [d.strftime('%b %y') for d in dates]
    # app.logger.warn(min_date)
    # app.logger.warn(max_date)
    # app.logger.warn(months_diff)

    # Create histogram bins
    avg_bins = [[] for x in range(len(dates))]  # Calculates average
    tweet_bins = [[] for x in range(len(dates))]  # For tweet table
    # Current date index, we loop from bottom
    i = 0
    for tweetsent in tweetsents:
        if tweetsent.tweet.created_at > dates[i] and i != len(dates) - 1:
            # Shift the bins
            i += 1
        avg_bins[i].append(tweetsent.sentiment.prob_scaled)
        tweet_bins[i].append(tweetsent)

    app.logger.warn(avg_bins)
    # Make this readable
    averages = [round(bin_averages(b), 3) for b in avg_bins]
    data = {
        'labels': human_dates,
        'datasets': [{
            'data': averages,
            'label': 'averages',
            'fillColor': 'rgba(220,220,220,0.2)',
            'strokeColor': 'rgba(220,220,220,1)',
            'pointColor': 'rgba(220,220,220,1)',
            'pointStrokeColor': '#fff',
            'pointHighlightFill': '#fff',
            'pointHighlightStroke': 'rgba(220,220,220,1)'
        }]
    }
    app.logger.warn(data)
    return data, tweet_bins


def add_months(delta, months):
    return delta + relativedelta(months=+months)


def add_weeks(delta, weeks):
    return delta + relativedelta(weeks=+weeks)


def bin_averages(b):
    if len(b) == 0:
        return 0
    else:
        return sum(b)/len(b)


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


def setup_logging():
    logger_handler = logging.StreamHandler()
    logger_handler.setFormatter(
        logging.Formatter(
            '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
        )
    )
    app.logger.addHandler(logger_handler)
    app.logger.setLevel(logging.INFO)

setup_logging()
api = tweepy_init()
app.logger.info('Loading classifier...')
classifier = sa.TwitterClassifier()
classifier.train()
app.logger.info('Done')

if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument(
        '-d', '--debug', action='store_true',
        help='run application in debug mode'
    )
    args = parser.parse_args()

    # app.debug = args.debug
    app.run(debug=True)
