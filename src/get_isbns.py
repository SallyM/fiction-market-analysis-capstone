import os
import time
import json
from bs4 import BeautifulSoup
import requests

def get_isbns_asins_goodreads(books):
    '''
    INPUT: list of books(author+title)
    OUTPUT: dictionary (book: {isbn10, isbn13, asin})
    '''
    scraped = {}
    for book in books:
        isbn10 = None
        isbn13 = None
        asin = None
        t = '+'.join(str(book).split('**')[1].split())
        a = '+'.join(str(book).split('**')[0].split())

        gr_isbn_url = 'https://www.goodreads.com/book/title.xml?author={}&key={}&title={}'.format(a, goodreads_key, t)
        gr_content = requests.get(gr_isbn_url)
        soup = BeautifulSoup(gr_content.content, "html.parser")
        try:
            isbn10 = soup.find('isbn').contents[0]
            isbn13 = soup.find('isbn13').contents[0]
            asin = soup.find('kindle_asin').contents[0]
        except AttributeError:
            continue
        except UnicodeEncodeError:
            continue
        scraped[book] = {'isbn10':isbn10, 'isbn13':isbn13, 'asin':asin}
        time.sleep(1 + random()*2)

    with open('data/books_with_isbns.json', mode='w') as f:
        f.write(json.dumps(scraped, indent=2))

def get_isbns_google(books):
    isbns = {}
    books_not_found = []
    for book in books:
        t = '+'.join(book.split('**')[1].replace("'", '').split())
        a = '+'.join(book.split('**')[0].replace('.', '').split())
        ggl_url = "https://www.google.com/search?q={}+{}+isbn&oq={}+{}+isbn&aqs=chrome.\
                    .69i57.11282j0j8&sourceid=chrome&ie=UTF-8".format(t, a, t, a)
        ggl_cont = requests.get(ggl_url)
        soup = BeautifulSoup(ggl_cont.content, 'html.parser')
        try:
            isbn = soup.findAll("span", {"class": "_G0d"})[0].text
            if len(isbn) == 13:
                isbns[book] = {'isbn10' : None,
                               'isbn13' : isbn}
            elif len(isbn) == 10:
                isbns[book] = {'isbn10' : isbn,
                               'isbn13' : None}
            else:
                isbns[book] = {'isbn10' : None,
                               'isbn13' : None}
        except IndexError:
            books_not_found.append(book)
            isbns[book] = {'isbn10' : None,
                           'isbn13' : None}
        time.sleep(1 + random()*3)
    return isbns, books_not_found
