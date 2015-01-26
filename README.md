# Twittersa

BC CSCI339 (Natural Language Processing) Final Project

A Twitter sentiment analysis web app written with Flask.

## Setup and Deployment

> **Note**: deployment to Heroku depends on scikit-learn and the numpy/scipy
stack, which is tricky to run with Heroku. We depend on @thenovices custom
Heroku/scipy [buildpack](https://github.com/thenovices/heroku-buildpack-scipy)
which can be set with `heroku config:set
BUILDPACK_URL=https://github.com/thenovices/heroku-buildpack-scipy`

This is a Heroku app with gunicorn as the web server, but the standalone app
can be run on localhost with `python twittersa.py` or `foreman start` and
requires Flask, Tweepy, and Scikit-Learn + dependencies, which can be installed
with

    pip install -r requirements.txt

Twittersa requires application-level authentication from a registered Twitter
application, and thus requires valid Consumer Key and Consumer Secret API keys
from http://dev.twitter.com/apps.

These keys must be set as environment variables (export `CONSUMER_KEY` and
`CONSUMER_SECRET`), or set them in `.env` and run with `foreman` or Heroku.

## Classifiers

`sentiment/classifiers.py` includes a command-line script to facilitate the
testing of various Naive Bayes classifiers with different data sets and feature
extraction techniques.

Usage should be pretty self explanatory by accessing help:

    python sentiment/classifiers.py --help

### Examples

    # MultinomialNB, tested with random sampling 5 times, unigrams + bigrams,
    # and TF-IDF weighted transformation. Accuracy is printed as an average
    # of the 5 samples.
    python sentiment/classifiers.py -N 5 -n 2 25000 --tfidf -c multinomial

    # BernoulliNB with unigrams and bigrams, 0 variance threshold removal,
    # serialization of the classifier, and an interactive REPL for
    # classification after training on the 25000 tweet data set
    python sentiment/classifiers.py -n 2 25000 -vpr

Currently the global variables present in the script prefixed with `PROD_` will
be automatically selected in Twittersa to serve as the classifier backing the
web application.

## Testing

    python tests.py

## Util

Contains helper scripts for related tasks. **NB**: These are intended to be ran
from the repository home directory, e.g. `python util/noslang_parser.py`. I
should probably make this a module?

 - `noslang_parser.py`
     - Parses and serializes abbrevations from
       [noslang](http://www.noslang.com/) dictionary
 - `semeval/`
     - Contains Tweet corpora from the SemEval 2013 (?) classification task
     - To download, use `tweet_download.py`
 - `tweet_download.py`
     - Downloads Tweets in the SemEval .tsv files by scraping URLs.
 - `pickle_corpus.py`
     - Grabs training .csv files specified in `corpora/`, parses them, removes
         everything but sentiment and text, and serializes them in `lib/`.
