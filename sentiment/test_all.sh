echo "Bernoulli Data Set Improvement"
python sentiment/classifiers.py --all -N 5 -c bernoulli | sort -n > sentiment/results/bernoulli_improvement.csv
echo "Multinomial Data Set Improvement"
python sentiment/classifiers.py --all -N 5 -c multinomial | sort -n > sentiment/results/multinomial_improvement.csv
echo "Bernoulli Bag of Words - Base"
python sentiment/classifiers.py 25000 -N 5 -c bernoulli
echo "Multinomial Bag of Words - Base"
python sentiment/classifiers.py 25000 -N 5 -c multinomial
# echo "Bernoulli Bag of Words - Stopword Filtering"
# python sentiment/classifiers.py 25000 -N 5 -c bernoulli
echo "Multi BoW - Stopword Filtering"
python sentiment/classifiers.py 25000 -N 5 -c multinomial
# echo "Bernoulli Bag of Words - Bigram, All"
# python sentiment/classifiers.py 25000 -n 2 -N 5 -c bernoulli
echo "Multi BoW - Bigram All"
python sentiment/classifiers.py 25000 -n 2 -N 5 -c multinomial
echo "Multi BoW - Bigram All - TFIDF"
python sentiment/classifiers.py 25000 -n 2 -N 5 --tfidf -c multinomial
# Bigram counts aren't implemented yet
# echo "Bernoulli Bag of Words - Bigram, 200 Significant"
# python sentiment/classifiers.py --all -n 2 --ngram-count 200 -N 5 -c bernoulli
echo "Multi BoW 10000"
python sentiment/classifiers.py 25000 -n 2 --bow-count 10000 -N 5 -c multinomial
echo "Multi BoW 10000 - Bigram 200"
python sentiment/classifiers.py 25000 -n 2 --bow-count 10000 --ngram-count 200 -N 5 -c multinomial
echo "Multi BoW 10000 - Bigram 200 - TFIDF"
python sentiment/classifiers.py 25000 -n 2 --bow-count 10000 --ngram-count 200 -N 5 --tfidf -c multinomial
# TFIDF?
# TODO: Grid Search
