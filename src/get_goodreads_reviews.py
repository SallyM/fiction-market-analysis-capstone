import requests, json, time
import os
from random import random
from bs4 import BeautifulSoup


def get_reviews_all(isbns):
    for i, isbn in enumerate(isbns):
        data = one_goodreads_api_call(isbn)
        write_results_to_file(data, 'data/goodreads_reviews.json')
        if i > 1 and i % 500 == 0:
            print '{} requests made.'.format(i)
            time.sleep(120 + random()*10)
        else:
            time.sleep(2 + random()*2)

def one_goodreads_api_call(isbn):
    data = {}
    gr_url = 'https://www.goodreads.com/book/isbn/{}?format=json&users_id={}'.format(isbn, goodreads_key)
    cont = requests.get(gr_url)
    soup = BeautifulSoup(cont.content, 'html.parser')
    descr = soup.find(id="description")
    if descr != None:
        descr = descr.text.split('\n')
        descr = [row for row in descr if len(row) > 0][-1]
    else:
        descr = None

    reviews = soup.find(id='bookReviews')

    # reviews include comments to each review
    if reviews != None:
        reviews = reviews.text.encode('utf-8').split('\n...more\n\n\n')
        reviews = [review.split('\n')[-1] for review in reviews]
    else:
        reviews = None
    data['isbn'] = isbn
    data['description'] = descr
    data['reviews'] = reviews
    return data

def write_results_to_file(entry, filename):
    a = []
    # if not os.path.isfile(filename):
    #     with open(filename, mode='w') as f:
    #         f.write(json.dumps(entry, indent=2))
    # else:
    #     with open(filename, mode='a') as f:
    #         f.write(json.dumps(entry, indent=2))

    if not os.path.isfile(filename):
        a.append(entry)
        with open(filename, mode='w') as f:
            f.write(json.dumps(a, indent=2))
    else:
        with open(filename) as f:
            cont = json.load(f)

        cont.append(entry)
        with open(filename, mode='w') as f:
            f.write(json.dumps(cont, indent=2))

if __name__ == '__main__':
    with open('data/all_books_isbn13.txt', 'r') as f:
        isbns = [l.strip() for l in f]
    goodreads_key = os.environ['GOODREADS_API_KEY']
    goodreads_secret = os.environ['GOODREADS_SECRET']
    get_reviews_all(isbns)
