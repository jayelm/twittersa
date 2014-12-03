"""
Small module implementing Twitter sentiment analysis functionality for
the TwitterSA web app.

Jesse Mu
"""
import re
# nltk is used to quickly automate tasks not related to my assignment,
# such as stemming, tokenization, and frequency distribution
import classifiers

CLASSIFIER = classifiers.NaiveBayesClassifier1


class Sentiment(object):
    """
    A class representing the sentiment of a tweet.

    Currently doesn't hold much, but this is designed to be extensible,
    and enable adding more detailed information about the sentiment
    (besides a raw percentage)
    """
    def __init__(self, polarity, subjectivity=None):
        self._polarity = polarity
        self._subjectivity = subjectivity

    @property
    def polarity(self):
        return self._polarity

    @property
    def subjectivity(self):
        self._subjectivity


class TweetSentiment(object):
    """A class encapsulating a tweet and its associated sentiment object."""
    def __init__(self, tweet, sentiment=None):
        self._tweet = tweet
        self._sentiment = sentiment

    @property
    def tweet(self):
        return self._tweet

    @property
    def sentiment(self):
        return self._sentiment


def analyze_sentiment(tweet):
    sentiment = Sentiment(0)
    return TweetSentiment(tweet, sentiment)
