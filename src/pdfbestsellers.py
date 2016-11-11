from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from cStringIO import StringIO
import requests, pymongo, json, time
from datetime import datetime, timedelta
import pdfminer
import os
from random import random
from collections import defaultdict

def convert_pdf_to_txt(path):
    '''
    Code for extracting text content from pdf, obtained from Stack Overflow:
    http://stackoverflow.com/questions/26494211/extracting-text-from-a-pdf-file-using-pdfminer-in-python
    '''
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'

    #Changed defaults to preserve as much table structure as possible
    laparams = LAParams(line_overlap=0,
                 char_margin=500,
                 line_margin=1,
                 word_margin=1,
                 boxes_flow=1,
                 detect_vertical=False,
                 all_texts=False)
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    fp = file(path, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""

    # Keeping only the first page
    maxpages = 1
    caching = True
    pagenos=set()

    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True):
        interpreter.process_page(page)

    text = retstr.getvalue()

    fp.close()
    device.close()
    retstr.close()
    return text

def download_lists():
    '''
    Downloads bestseller list pdfs by date from Hawes Publishing and saves to specified location
    '''
    lst_dates = list_dates()
    for date in lst_dates:
        year = date.year
        url = 'http://www.hawes.com/{}/{}.pdf'.format(str(year), date.strftime('%Y-%m-%d'))
        doc = requests.get(url)
        filename = 'data/pdf_bestsellers/{}.pdf'.format(date.strftime('%Y-%m-%d'))
        with open(filename, 'wb') as f:
            f.write(doc.content)

def list_dates():
    '''
    Creates list of dates from Jan 1, 1950 until June 6 2008.
    Actual lists are from 2 weeks prior to each publication date.
    '''
    beginning_date = datetime(1950, 1, 1)
    numdays = (datetime(2008, 6, 8) - beginning_date).days
    dates = [beginning_date]
    for d in xrange(7, numdays + 7, 7):
        cur_date = (beginning_date + timedelta(days = d))
        dates.append(cur_date)
    return dates

def parse_one_file(path):
    content = convert_pdf_to_txt(path)
    content = content.strip().split('\n')
    content = [row.strip() for row in content]
    entry = {}
    list_date = datetime.strftime(datetime.strptime((content[2]).replace(',',''), '%B %d %Y'), '%Y-%m-%d')
    # Actual book data starts at row index 16
    book_rows = [row for row in content[16:] if len(row) > 0]
    books = {}
    for row in book_rows:
        row = row.split('  ')
        title = row[1].split(', by ')[0]
        author = row[1].split(', by ')[1].strip('.')
        rank_this_wk = row[0]
        rank_last_wk = row[-2]
        num_wks_on_list = row[-1]
        books[title] = {'author':author,
                        'rank_this_wk':rank_this_wk,
                        'rank_last_wk':rank_last_wk,
                        'num_wks_on_list':num_wks_on_list,
                        'isbn10':None,
                        'isbn13':None}
    entry[list_date] = books
    return entry

def get_filenames():
    dates = list_dates()
    filenames = []
    for date in dates:
        filename = 'data/pdf_bestsellers/{}.pdf'.format(date.strftime('%Y-%m-%d'))
        filenames.append(filename)
    return filenames

def write_results_to_file(entry, filename):
    a = []
    if not os.path.isfile(filename):
        a.append(entry)
        with open(filename, mode='w') as f:
            f.write(json.dumps(entry, indent=2))
    else:
        with open(filename) as f:
            feeds = json.load(f)

        feeds.update(entry)
        with open(filename, mode='w') as f:
            f.write(json.dumps(feeds, indent=2))

def parse_all_files(filenames):
    for f in filenames:
        entry = parse_one_file(f)
        write_results_to_file(entry, 'data/parsed_pdf_lists.json')
