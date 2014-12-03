"""
Implementations of several varations of Naive Bayes Classifiers.

Jesse Mu
"""

from sklearn.naive_bayes import MultinomialNB, BernoulliNB
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import f1_score
# from nltk.corpus.reader.sentiwordnet import SentiWordNetCorpusReader
# NLTK's tokenizer, as opposed to scikit, is more robust
from nltk import word_tokenize
from random import shuffle
import pickle  # Standard pickle for unicode support

# Get slang dictionary
with open('lib/noslang.pickle', 'r') as fin:
    slang = pickle.load(fin)


def preprocess(text):
    """
    Preprocess a tweet by:
     - Removing repeated words
     - Expanding acronyms
     - Removing punctuation
    """
    text = text.lower()
    # Attempt to decode for word_tokenize
    codec = 'utf8'
    try:
        text = text.decode(codec)
    except UnicodeDecodeError:
        # Try latin1 instead
        codec = 'latin-1'
        text = text.decode(codec)

    text = word_tokenize(text)
    processed = []
    for i, word in enumerate(text):
        if word in slang:
            # Look up the expanded acronym, and break that apart
            words = word_tokenize(slang[word])
            processed.extend(words)
        else:
            processed.append(word)

    # Reencode string
    return [s.encode(codec) for s in processed]


class BagOfWords(CountVectorizer):
    """
    Just a renaming of the scikit-learn CountVectorizer class.
    This implements standard bag of words count-based feature extraction.
    """
    pass


def load_pickle(filename):
    """Loads the pickled data with the given filename"""
    with open(filename, 'r') as fin:
        training = pickle.load(fin)
    return training


PROD_TRAINING_FILE = 'lib/training.5000.pickle'
PROD_TRAINING_DATA = load_pickle(PROD_TRAINING_FILE)
PROD_PROCESSOR = BagOfWords(min_df=1, analyzer=preprocess)
PROD_CLASSIFIER = BernoulliNB()


class TwitterClassifier(object):
    """
    A wrapper for a scikit classifier that simplifies fitting and training.
    """
    def __init__(self, clf=PROD_CLASSIFIER):
        self.clf = clf

    def train(self, data=PROD_TRAINING_DATA, processor=PROD_PROCESSOR):
        self.data = data
        self.processor = processor

        shuffle(self.data)
        X = self.processor.fit_transform([x[0] for x in self.data])
        y = [x[1] for x in self.data]

        self.clf.fit(X, y)

    def predict(self, tweet):
        """
        Return a TweetSentiment instance for the provided Tweepy tweet.
        """
        X = self.processor.transform([tweet.text])
        probs = self.clf.predict_proba(X)
        probs_dict = {self.clf.classes_[i]: p for i, p in enumerate(probs[0])}
        label = max(probs_dict, key=lambda x: probs_dict[x])
        sentiment = Sentiment(label, probs_dict)
        tweetsent = TweetSentiment(tweet, sentiment)
        return tweetsent

    def predict_many(self, tweets):
        """
        Return a TweetSentiment instance for the provided list of
        Tweepy tweets.
        """
        X = self.processor.transform([t.text for t in tweets])
        probs = self.clf.predict_proba(X)
        tweetsents = []
        for prob, tweet in zip(probs, tweets):
            probs_dict = {self.clf.classes_[i]: p for i, p in enumerate(prob)}
            label = max(probs_dict, key=lambda x: probs_dict[x])
            sentiment = Sentiment(label, probs_dict)
            tweetsents.append(TweetSentiment(tweet, sentiment))
        return tweetsents


class Sentiment(object):
    """
    A class representing the sentiment of a tweet.

    Currently doesn't hold much, but this is designed to be extensible,
    and enable adding more detailed information about the sentiment
    (besides a raw percentage)
    """
    def __init__(self, label, probs):
        self._label = label
        self._probs = probs

    @property
    def label(self):
        return self._label

    @property
    def positivity(self):
        return self._probs['positive']

    @property
    def negativity(self):
        return self._probs['negative']

    @property
    def prob(self):
        if self._label == 'positive':
            return self._probs['positive']
        else:
            return self._probs['negative']

    @property
    def probs(self):
        return self._probs

    def __str__(self):
        return "<{}, {}>".format(self.label, self.prob)

    def __repr__(self):
        return "<{}>".format(self.probs)


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

    def __str__(self):
        return "<{}: {}>".format(self._tweet.text, self._sentiment)

    def __repr__(self):
        return "<{}: {}>".format(repr(self._tweet), repr(self._sentiment))


if __name__ == '__main__':
    from argparse import ArgumentParser
    import sys
    import os
    parser = ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        'corpus', nargs='*', type=int, default=[],
        help="corpus sizes (must be the size of a .pickle file in lib/)"
    )
    group.add_argument(
        '-a', '--all', action='store_true',
        help='grab all training .pickle files in lib'
    )
    parser.add_argument(
        '-c', '--classifier', default='bernoulli',
        help='specifiy classifier (bernoulli or multinomial)'
    )
    parser.add_argument(
        '-n', '--num', type=int, default=1,
        help="number of times to train each classifier"
    )

    args = parser.parse_args()

    if not args.corpus and not args.all:
        sys.exit('classifiers.py: error: must specify corpus files')

    corpus = args.corpus
    if args.all:
        corpus = sorted(['lib/{}'.format(f) for f in os.listdir('lib/') if
                         f.startswith('training') and f.endswith('.pickle')])

    for filename in corpus:
        if not args.all:  # Format the filename correctly
            n = filename
            filename = 'lib/training.{}.pickle'.format(str(filename))
        else:
            n = int(filename[13:-2])  # Just get the number
        accuracy_list = []
        fscore_list = []
        for i in range(args.num):
            # sys.stdout.write('{}...'.format(i))
            # sys.stdout.flush()
            all_features = load_pickle(filename)
            shuffle(all_features)

            cutoff = (len(all_features) * 7) / 10
            training = all_features[:cutoff]
            testing = all_features[cutoff:]

            vectorizer = CountVectorizer(min_df=1, analyzer=preprocess)
            X_train = vectorizer.fit_transform([x[0] for x in training])
            X_test = vectorizer.transform([x[0] for x in testing])
            y_train = ([x[1] for x in training])
            y_test = ([x[1] for x in testing])

            if args.classifier == 'bernoulli':
                classifier = BernoulliNB()
            elif args.classifier == 'multinomial':
                classifier = MultinomialNB()
            else:
                sys.exit(
                    'classifiers.py: error: unknown classifier {}'.format(
                        args.classifier
                    )
                )
            classifier.fit(X_train, y_train)

            accuracy = classifier.score(X_test, y_test)

            y_predict = classifier.predict(X_test)

            fscore = f1_score(y_test, y_predict, pos_label='positive')

            # Add totals for running average
            accuracy_list.append(accuracy)
            fscore_list.append(fscore)

        average_accuracy = sum(accuracy_list) / len(accuracy_list)
        average_fscore = sum(fscore_list) / len(fscore_list)
        # This is designed to be redirected to a file
        print "size,accuracy,fscore"
        print "{},{},{}".format(n, average_accuracy, average_fscore)
