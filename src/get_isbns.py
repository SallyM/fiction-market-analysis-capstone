def get_isbns_asins(books):
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
