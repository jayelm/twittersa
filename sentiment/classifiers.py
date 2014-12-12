"""
Implementations of several varations of Naive Bayes Classifiers.

Jesse Mu
"""

from sklearn.naive_bayes import MultinomialNB, BernoulliNB
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.feature_selection import SelectKBest, chi2, VarianceThreshold
# from sklearn.metrics import f1_score
from sklearn.pipeline import Pipeline
# from nltk.corpus.reader.sentiwordnet import SentiWordNetCorpusReader
# NLTK's tokenizer, as opposed to scikit, is more robust
import re
import nltk
from nltk.stem import porter
from random import shuffle
import pickle  # Standard pickle for unicode support

# Look for corpuses in this directory for heroku
nltk.data.path.append('./nltk_data/')

# Get slang dictionary
with open('lib/noslang.pickle', 'r') as fin:
    slang = pickle.load(fin)

# These are twitter specific stopwords
with open('lib/stopwords.pickle', 'r') as fin:
    stopwords = pickle.load(fin)

PUNCTUATION = set('@$%^!?#&*()_+=-{}[]\|/:"\';",.')
porter_stemmer = porter.PorterStemmer()


def preprocess(text):
    """
    Preprocess a tweet by:
     - Removing repeated words
     - Expanding acronyms
     - Porter stemming
     - Removing punctuation
    """
    is_unicode = isinstance(text, unicode)
    # Attempt to decode for word_tokenize
    if not is_unicode:
        codec = 'utf8'
        try:
            text = text.decode(codec)
        except UnicodeDecodeError:
            # Try latin1 instead
            codec = 'latin-1'
            text = text.decode(codec)

    text = text.lower()
    # Remove two or more occurrences of characters`
    text = re.sub(r'(.)\1+', r'\1\1', text)
    text = nltk.word_tokenize(text)
    processed = []
    for i, word in enumerate(text):
        word = porter_stemmer.stem(word)
        if word in PUNCTUATION:
            continue
        if word in slang:
            # Look up the expanded acronym, and break that apart
            words = nltk.word_tokenize(slang[word])
            processed.extend(words)
        else:
            processed.append(word)

    # Reencode string if necessary
    if not is_unicode:
        processed = [s.encode(codec) for s in processed]
    return ' '.join(processed)


class BagOfWords(CountVectorizer):
    """
    Just a renaming of the scikit-learn CountVectorizer class.
    This implements standard bag of words count-based feature extraction.
    """
    pass


def show_most_informative_features(vectorizer, clf, n=20):
    feature_names = vectorizer.get_feature_names()
    coefs_with_fns = sorted(zip(clf.coef_[0], feature_names))
    top = zip(coefs_with_fns[:n], coefs_with_fns[:-(n + 1):-1])
    for (coef_1, fn_1), (coef_2, fn_2) in top:
        print "\t%.4f\t%-15s\t\t%.4f\t%-15s" % (coef_1, fn_1, coef_2, fn_2)


def load_pickle(filename):
    """Loads the pickled data with the given filename"""
    with open(filename, 'r') as fin:
        training = pickle.load(fin)
    return training


PROD_TRAINING_FILE = 'lib/training.15000.pickle'
PROD_TRAINING_DATA = load_pickle(PROD_TRAINING_FILE)
PROD_PROCESSOR = BagOfWords(
    min_df=1,
    analyzer='word',
    encoding='utf-8',
    decode_error='replace',
    preprocessor=preprocess,
    tokenizer=nltk.word_tokenize,
    stop_words=stopwords,
    ngram_range=(1, 2),
    binary=True
)
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
    def prob_scaled(self):
        if self._label == 'positive':
            return self.positivity - 0.5
        else:
            return -self.negativity + 0.5

    @property
    def prob_scaled_rounded(self):
        return round(self.prob_scaled, 3)

    @property
    def prob(self):
        if self._label == 'positive':
            return self.positivity
        else:
            return self.negativity

    @property
    def probs(self):
        return self._probs

    def __str__(self):
        return "<{}, {}>".format(self.label, self.prob)

    def __repr__(self):
        return "<{}>".format(self.probs)

    def __float__(self):
        return self.prob_scaled

    def __add__(self, other):
        return self.prob_scaled + other.prob_scaled


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

    @property
    def created_at_human(self):
        """Human-readable timestamp"""
        return self._tweet.created_at.strftime('%b %d %Y')

    def __str__(self):
        """This is not, and should not, be used by Flask."""
        return "<{}: {}>".format(
            self._tweet.text, self._sentiment
        )

    def __unicode__(self):
        return u"<{}: {}>".format(
            self._tweet.text, self._sentiment
        )

    def __repr__(self):
        return "<{}: {}>".format(repr(self._tweet), repr(self._sentiment))

    def __cmp__(self, other):
        """Compare by dates,"""
        return (int(self.tweet.created_at.strftime('%s')) -
                int(other.tweet.created_at.strftime('%s')))

    def __add__(self, other):
        return self.sentiment + other.sentiment


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
        '-s', '--stopwords', action='store_true',
        help="filter out stopwords before processing"
    )
    parser.add_argument(
        '-n', '--ngram', type=int, default=1,
        help="use ngrams in addition to unigrams"
    )
    tf_options = parser.add_mutually_exclusive_group()
    tf_options.add_argument(
        '--tf', action='store_true',
        help="use tf feature normalization"
    )
    tf_options.add_argument(
        '--tfidf', action='store_true',
        help="use tf-idf feature normalization (incompatible with --tf)"
    )
    parser.add_argument(
        '--show-best-features', dest='showfeats', action='store_true',
        help="show most informative features for each classifier iteration"
    )
    parser.add_argument(
        '-k', '--k-best', type=int, dest='kbest', default=None,
        help="select k best features with chi-squared statistical test"
    )
    parser.add_argument(
        '-v', '--variance-threshold', type=float, dest='threshold', const=0.0,
        nargs='?', default=None,
        help="remove features with variance below threshold"
    )
    parser.add_argument(
        '-p', '--pickle', type=str, nargs='?',
        const='./lib/classifier.pickle',
        default=None,
        help="save last classifier to given destination"
    )
    parser.add_argument(
        '-N', '--num', type=int, default=1,
        help="number of times to train each classifier"
    )
    parser.add_argument(
        '-r', '--repl', action='store_true',
        help="enter REPL for last classifier"
    )

    args = parser.parse_args()

    if not args.corpus and not args.all:
        sys.exit('classifiers.py: error: must specify corpus files')

    corpus = args.corpus
    if args.all:
        corpus = sorted(['lib/{}'.format(f) for f in os.listdir('lib/') if
                         f.startswith('training') and f.endswith('.pickle')])

    print "size,accuracy,fscore"
    for filename in corpus:
        if not args.all:  # Format the filename correctly
            n = filename
            filename = 'lib/training.{}.pickle'.format(str(filename))
        else:
            n = int(filename[13:-7])  # Just get the number
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

            vectorizer = CountVectorizer(
                min_df=1,
                analyzer='word',  # Would I ever use char n-grams?
                encoding='utf-8',
                decode_error='replace',  # For the one-off latin-1 tweets
                ngram_range=(1, args.ngram),
                preprocessor=preprocess,
                tokenizer=nltk.word_tokenize,
                stop_words=stopwords if args.stopwords else None,
                binary=(args.classifier == 'bernoulli'),
            )

            # Assume pos/neg tweets are equally likely
            if args.classifier == 'bernoulli':
                nb = BernoulliNB(class_prior=[0.5, 0.5])
            elif args.classifier == 'multinomial':
                nb = MultinomialNB(class_prior=[0.5, 0.5])
            else:
                sys.exit(
                    'classifiers.py: error: unknown classifier {}'.format(
                        args.classifier
                    )
                )

            selector = SelectKBest(chi2, k=args.kbest)
            tfidf = TfidfTransformer(use_idf=args.tfidf)
            pipe = []
            pipe.append(('vectorizer', vectorizer))
            if args.tfidf or args.tf:
                pipe.append(('tfidf', tfidf))
            if args.kbest is not None:
                pipe.append(('selector', selector))
            if args.threshold is not None:
                pipe.append(('variance_threshold', VarianceThreshold(
                    threshold=args.threshold
                )))
            pipe.append(('clf', nb))

            X, y = map(list, zip(*training))

            classifier_pipeline = Pipeline(pipe)

            # print classifier_pipeline
            classifier = classifier_pipeline.fit(X, y)

            X_test, y_test = map(list, zip(*testing))
            accuracy = classifier.score(X_test, y_test)

            # x = vectorizer.transform(X_test)
            # print x.shape
            # x = tfidf.transform(x)
            # print x.shape
            # x = selector.transform(x)
            # print x.shape

            # FIXME this has not been updated to use zipping
            # y_predict = classifier.predict(X_test)

            # fscore = f1_score(y_test, y_predict, pos_label='positive')
            fscore = 1000

            # Add totals for running average
            if args.showfeats:
                show_most_informative_features(vectorizer, nb)

            accuracy_list.append(accuracy)
            fscore_list.append(fscore)

        average_accuracy = sum(accuracy_list) / len(accuracy_list)
        # print accuracy_list
        average_fscore = sum(fscore_list) / len(fscore_list)
        # This is designed to be redirected to a file
        print "{},{},{}".format(n, average_accuracy, average_fscore)
        if args.pickle is not None:
            with open(args.pickle, 'w') as pout:
                pickle.dump(classifier, pout)
        if args.repl:
            while True:
                x = unicode(raw_input('> '))
                print classifier.predict([x])
                print classifier.predict_proba([x])
