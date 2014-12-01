"""
Implementations of several varations of Naive Bayes Classifiers.

Jesse Mu
"""
import nltk
import pickle  # Standard pickle for unicode support
from collections import defaultdict
# from pprint import pprint as pp

PROD_TRAINING_SET = 'lib/training.1000.p'
PROD_TEST_SET = 'lib/testdata.manual.2009.06.14.p'

# Get slang dictionary
with open('lib/noslang.p', 'r') as f:
    slang = pickle.load(f)


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
        codec = 'latin-1'
        text = text.decode(codec)

    text = nltk.word_tokenize(text)
    processed = []
    for i, word in enumerate(text):
        if word in slang:
            # Look up the expanded acronym, and break that apart
            words = nltk.word_tokenize(slang[word])
            processed.extend(words)
        else:
            processed.append(word)

    # Reencode string
    return [s.encode(codec) for s in processed]


def features1(tweet):
    """Just returns a list of all words present."""
    return dict((word, True) for word in tweet)


def features2(tweet):
    pass


def prepare_data(filename, feat_func):
    """
    Converts a .csv file with rows
    label   tweet
    =============
    to a list of the form
    (feature dictionary, label)

    while preprocessing and extracting features with the provided
    features function.
    """
    with open(filename, 'r') as fin:
        training = pickle.load(fin)
    # Preprocess tweets
    training = [(preprocess(tweet), sent) for tweet, sent in training]
    return [(feat_func(tweet), sent) for tweet, sent in training]


class BinaryNaiveBayesClassifier(object):
    """
    A binary Naive Bayes classification algorithm.

    Works only on binary features, i.e. those with True or False or 0 or 1.
    """
    def __init__(self):
        pass

    def train(self, training_data):
        # TODO: perhaps use log probabilities?
        self._training_data = training_data

        # Get all possible features
        self._labels = set(label for features, label in self._training_data)

        # This defaultdict initializes a dictionary with count=0 for each
        # label in the training set for each new word
        self._raw_counts = defaultdict(
            lambda: {label: 0 for label in self._labels}
        )

        # First, accumulate raw counts (requiring binary features)
        # word: {positive: counts, negative: counts}
        for features, label in self._training_data:
            for word in features:
                # Assert binary features
                assert int(features[word] == features[word]), \
                    "Features are not binary"
                self._raw_counts[word][label] += features[word]

        # Then, calculate percentage distribution of occurrences
        # word: {positive: percentage, negative: percentage}
        self._count_percentages = {}
        for word in self._raw_counts:
            counts = self._raw_counts[word]
            # Get total number of counts, float for division later
            total = float(sum(counts[label] for label in counts))
            self._count_percentages[word] = {
                label: counts[label]/total for label in counts
            }

        # Transform to get P(word|label)
        # {
        # positive: {word: probability,
        #            word: probability,
        #            ...
        #           }
        # negative: {word: probability,
        #            word: probability,
        #            ...
        #           }
        # }
        self._cond_probabilities = defaultdict(dict)
        for word in self._count_percentages:
            percentages = self._count_percentages[word]
            for label in percentages:
                probability = percentages[label]
                self._cond_probabilities[label][word] = probability

    def classify(self, features):
        """
        Classify an example according to its features.

        Features must be processed identically to how they were processed
        while training.
        """

        if not self._cond_probabilities:
            raise Exception("Classifier has not yet been trained!")

        probs = (
            (self._calculate_probs(features, label), label)
            for label in self._labels
        )
        best_prob = max(probs, key=lambda x: x[0])
        return best_prob[1]

    def _calculate_probs(self, features, label):
        """
        Calculate probabilities of a given
        Assume labels are equally likely.
        """
        # README FIXME OPTIMIZE TODO binary features aren't working
        # correctly...right now I'm assuming all true
        # FIXME laplace smoothing? Or something to take care of 0 prob
        # Check NLTK naive bayes, model after that
        label_dict = self._cond_probabilities[label]
        probability = 1
        for word in features:
            if word not in label_dict:
                # If we have an unseen word, ignore it, instead of
                # setting probability 0 and flatlining everything else
                continue
            probability = 0
        return probability


if __name__ == '__main__':
    # Demo
    classifier = BinaryNaiveBayesClassifier()
    classifier.train(prepare_data(PROD_TRAINING_SET, features1))
