from sklearn.cluster import KMeans
import pandas
import numpy
import nltk
import json
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import string
from nltk.stem.wordnet import WordNetLemmatizer
import os
import time
from random import random
from datetime import datetime, timedelta



topics_by_book = pd.read_csv('test/topics_by_book_test.csv', delimiter='\t', encoding='utf-8', index_col=0)

k = 10

km = KMeans(n_clusters=k, init='k-means++', max_iter=1000, n_init=1000, n_jobs=-1)

stop_words = ['book', 'read', 'reading', 'fiction', 'novel', 'story', 'chapter', 'page', 'author', 'character',
              'kindle', 'paperback', 'copy', 'reader', 'com', 'http', 'blogspot', 'jacquelinesreads', 'amazon', 'more',
              'facebook', 'twitter', 'blog', 'amzn', 'review', '...', "''", '""', '``', "'", '"', 'books', '--', "n't",
              "'m", "'s", 'writing', 'write', 'written', 'would', 'should', 'could', 'like', 'really', 'much',
              'first', 'second', 'third', 'fourth', 'one', 'two','three', 'four', 'trilogy', 'good', 'get', 'find',
              'recommend', 'fan', 'enjoyed', 'next', 'also', 'put', 'ca', 'wrote', 'favorite', 'know','even',
              'nan', 'well', 'many', 'new', 'best', 'better', 'thing', 'way', 'another', 'make', 'great','found',
              'go', 'going', 'even', 'end', 'little', 'back', 'enjoy', 'still','always', 'never', 'something',
              'five', 'think', 'give', 'got', 'hardcopy', 'hard copy', ]
stop_words.extend(list(string.punctuation))
stop_words.extend(set(stopwords.words('english')))

topics_by_book['combined_docs'] = topics_by_book['0'] + ' ' + topics_by_book['1'] + ' ' + topics_by_book['2'] + ' ' \
                                 + topics_by_book['3'] + ' ' + topics_by_book['4'] + " " + topics_by_book['5'] + ' ' \
                                 + topics_by_book['6'] + " " + topics_by_book['7'] + ' ' + topics_by_book['8'] + ' ' \
                                 + topics_by_book['9'] + ' ' + topics_by_book['10'] + ' ' + topics_by_book['11'] + " " \
                                 + topics_by_book['12'] + ' ' + topics_by_book['13'] + " " + topics_by_book['14'] + ' ' \
                                 + topics_by_book['15'] + ' ' + topics_by_book['16'] + " " + topics_by_book['17'] + ' ' \
                                 + topics_by_book['18'] + ' ' + topics_by_book['19']

topics_by_book['combined_docs'] = topics_by_book['combined_docs'].astype(str)

docs = topics_by_book['combined_docs']

vectorizer = TfidfVectorizer(encoding=u'utf-8', decode_error=u'strict', strip_accents='ascii', lowercase=True,
                            tokenizer=None, analyzer=u'word', stop_words=stop_words,ngram_range=(1, 1), max_df=0.5,
                            min_df=25, max_features=5000, use_idf=True, smooth_idf=True, binary=False)

tokens = [word_tokenize(doc, language = 'english') for doc in docs]
lemmed = [' '.join([lemmatizer.lemmatize(word) for word in i]) for i in tokens]
data_vectors = vectorizer.fit_transform(lemmed)

X = data_vectors

fitted = km.fit(X)

clust_lables = km.labels_

topics_by_book['cluster_label'] = clust_lables

books_with_clusters = topics_by_book[['cluster_label']]

books_with_clusters = books_with_clusters.reset_index()

books_with_clusters.rename(columns = lambda x: x.replace('index', 'all_isbns'), inplace = True)

# if __name__ == '__main__':
#     topics_by_book = pd.read_csv('test/topics_by_book_test.csv', delimiter='\t', encoding='utf-8', index_col=0)


order_centroids = km.cluster_centers_.argsort()[:, ::-1]

terms = vectorizer.get_feature_names()
clusters = {}
for i in range(k):
#     print("Cluster %d:" % i)
    words = []
    for ind in order_centroids[i, :10]:
        words.append(terms[ind])
#         print(' %s' % terms[ind])
    clusters[i] = words
#     print()
try_jeff = km.cluster_centers_**2 / np.sum(km.cluster_centers_,axis=0)
order_centroids = try_jeff.argsort()[:, ::-1]

terms = vectorizer.get_feature_names()
clusters = {}
for i in range(k):
#     print("Cluster %d:" % i)
    words = []
    for ind in order_centroids[i, :10]:
        words.append(terms[ind])
#         print(' %s' % terms[ind])
    clusters[i] = words
#     print()
lists['all_isbns'] = lists['comb_isbn10'].astype(str) + ' | ' + lists['comb_isbn13'].astype(str)

# lists

lists_with_clusters = pd.merge(lists, books_with_clusters, how = 'left', on = 'all_isbns')


lists_with_clusters = lists_with_clusters.sort_values('list_date')

years = [str(y) for y in range(2008, 2017)]
ratios_by_cluster = {}
for c in xrange(k):
    ratios = []
#     print c
    for y in years:
#         print d
        df = lists_with_clusters[lists_with_clusters.list_date.str.contains(y)]
        c_count = df[df['cluster_label'] == c].shape[0]
#         print df[df['cluster_label'] == c]
#         print c_count
        total = df.shape[0]
#         print total
        ratio = float(c_count)/float(total)
#         print ratio
        ratios.append(ratio)
    ratios_by_cluster[c] = ratios
