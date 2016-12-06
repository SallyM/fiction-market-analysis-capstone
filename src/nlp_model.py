import pandas as pd
import numpy as np
import nltk
import json
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import string
from nltk.stem.wordnet import WordNetLemmatizer
from sklearn.decomposition import NMF, LatentDirichletAllocation
import os
import time
import requests
from random import random
from datetime import datetime, timedelta


stop_words = ['book', 'read', 'reading', 'fiction', 'novel', 'story', 'chapter', 'page', 'author', 'character',
              'kindle', 'paperback', 'copy', 'reader', 'com', 'http', 'blogspot', 'jacquelinesreads', 'amazon', 'more',
              'facebook', 'twitter', 'blog', 'amzn', 'review', '...', "''", '""', '``', "'", '"', 'books', '--',
              "n't", "'s", "'m"]

stop_words.extend(list(string.punctuation))
stop_words.extend(set(stopwords.words('english')))

lemmatizer = WordNetLemmatizer()

tfidf_tokens = TfidfVectorizer(encoding=u'utf-8', decode_error=u'strict', strip_accents='ascii', lowercase=True,
                             preprocessor=None, tokenizer=word_tokenize, analyzer=u'word', stop_words=stop_words,
                             ngram_range=(1, 1), max_df=1.0, min_df=1, max_features=5000,
                             use_idf=True, smooth_idf=True, binary=False)

cv_tokens = CountVectorizer(input=u'content', encoding=u'utf-8', decode_error=u'strict', strip_accents='ascii',
                     lowercase=True, preprocessor=None, tokenizer=word_tokenize, stop_words=stop_words,
                     ngram_range=(1, 2), analyzer=u'word', max_df=1.0, min_df=20, max_features=5000)

lda = LatentDirichletAllocation(n_topics=5, max_iter=50, learning_method='online', learning_offset=1., random_state=123)
# nmf = NMF(n_components = 100, alpha = 1, random_state = 123, max_iter=50)


def get_top_words(model, feature_names, n_top_words):
    topics = []
    for topic_idx, topic in enumerate(model.components_):
        topics.append(" ".join([feature_names[i]
                        for i in topic.argsort()[:-n_top_words - 1:-1]]))
    return topics


def process_one_book(book):
    try:
        docs_df = extracted_reviews[extracted_reviews.all_isbns == book]
#         print docs_df
        docs_df2 = have_descriptions[have_descriptions.all_isbns == book]
#         print docs_df2
        docs_df = docs_df.rename(columns = lambda x: x.replace('reviews', 'text'))
        docs_df2 = docs_df2.rename(columns = lambda x: x.replace('description', 'text'))
        re_indexed_docs_df = pd.concat((docs_df, docs_df2), axis = 0, ignore_index=True)
        re_indexed_docs_df = re_indexed_docs_df['text'].to_frame()
#         print re_indexed_docs_df.head()
#         time.sleep(555)
#         re_indexed_docs_df = re_indexed_docs_df.reset_index(drop = True)
#         print re_indexed_docs_df.head()
        docs = re_indexed_docs_df['text'].values.tolist()
#         print docs
        tokenized = [word_tokenize(doc) for doc in docs]
#         print tokenized
#         tagged = [nltk.pos_tag(tokens) for tokens in tokenized]
        lemmed = [' '.join([lemmatizer.lemmatize(tokenized[i][j]) for j, _ in enumerate(tokenized[i])]) for i, _ in enumerate(tokenized)]
#         print lemmed
        countvectors = cv_tokens.fit_transform(lemmed)
        lda_model = lda.fit(countvectors)
#         tfidfvectors = tfidf.fit_transform(lemmed)
#         tfidfvectors = tfidf_tokens.fit_transform(lemmed)
#         nmf_model = nmf.fit(tfidfvectors)

#         tfidf_feature_names = tfidf.get_feature_names()
        cv_feature_names = cv_tokens.get_feature_names()

#         model = lda.fit(countvectors)
#         cv_feature_names = cvLemmed.get_feature_names()
        book_topics = get_top_words(lda_model, cv_feature_names, 20)
#         book_topics.extend(get_top_words(lda_model, cv_feature_names, 20))
#         print 'Book {} processed!'.format(book)
        return book_topics
    except IndexError:
        print book, 'Not enough text'
    except ValueError:
        print book, 'Not enough text'

def process_all_books(books):
    topics_by_book = {}
    for i, book in enumerate(books):
        book_topics = process_one_book(book)
        topics_by_book[book] = book_topics
        if i % 100 == 0:
            print '{} books processed!'.format(i)
    return topics_by_book

if __name__ == '__main__':
    have_descriptions = pd.read_csv('data/extracted_descriptions_by_book.tsv', delimiter = '\t', index_col=0, encoding='utf-8')
    extracted_reviews = pd.read_csv('data/extracted_reviews_by_book.tsv', delimiter = '\t', index_col=0, encoding='utf-8')
    books = extracted_reviews.all_isbns.unique().tolist()
    topics = process_all_books(books)
    with open('test/topics.json', 'w') as f:
        json.dump(topics, f)
