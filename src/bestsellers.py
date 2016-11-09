import pandas as pd
import requests, pymongo, json, time
import os
from datetime import datetime, timedelta
from random import random

NYT_api_key = os.environ['NYT_API_KEY']

def call_api_once(date, list_name):
    '''
    INPUT: date of list, name of list, both strings
    OUTPUT: dictionary with key = date, val = parsed book meta data
    '''
    entry = {}
    url = 'http://api.nytimes.com/svc/books/v2/lists/{}/{}.json&api-key={}'.format(date, list_name, NYT_api_key)
    cont = requests.get(url)
    content_data = pd.read_json(cont.content)
    results = content_data['results']
    list_date = results[0]['bestsellers_date']
    parsed_results = get_book_meta(results)
    entry[list_date] = parsed_results
    return entry

def get_book_meta(bsl_df):
    '''
    INPUT: dataframe of json result of API call
    OUTPUT: dictionary of book meta data
    '''
    # Go thru all results and extract titles and meta data
    parsed = {}
    for idx, _ in enumerate(bsl_df):
        meta = {}
        title = bsl_df[idx]['book_details'][0]['title']
        author = bsl_df[idx]['book_details'][0]['author']
        meta['author'] = author
        isbn10 = bsl_df[idx]['book_details'][0]['primary_isbn10']
        meta['isbn10'] = isbn10
        isbn13 = bsl_df[idx]['book_details'][0]['primary_isbn13']
        meta['isbn13'] = isbn13
        num_wks_on_list = bsl_df[idx]['weeks_on_list']
        meta['num_wks_on_list'] = num_wks_on_list
        rank_this_wk = bsl_df[idx]['rank']
        meta['rank_this_wk'] = rank_this_wk
        rank_last_wk = bsl_df[idx]['rank_last_week']
        meta['rank_last_wk'] = rank_last_wk
        parsed[title] = meta
    return parsed

def write_results_to_file(entry, filename):
    a = []
    if not os.path.isfile(filename):
        a.append(entry)
        with open(filename, mode='w') as f:
            f.write(json.dumps(entry, indent=2))
    else:
        with open(filename) as feedsjson:
            feeds = json.load(feedsjson)

        feeds.update(entry)
        with open(filename, mode='w') as f:
            f.write(json.dumps(feeds, indent=2))

def print_only_dates():
    # Print-only (mass-market paperback, trade-paperback, hardcovers) lists dates from 6/8/2008 to 2/6/2011
    beginning_date = datetime(2008, 6, 8)
    numdays = (datetime(2011, 2, 6) - beginning_date).days
    dates = [beginning_date.strftime('%Y-%m-%d')]
    for d in xrange(7, numdays + 7, 7):
        cur_date = (beginning_date + timedelta(days = d)).strftime('%Y-%m-%d')
        dates.append(cur_date)
    return dates

def get_print_only_lists():
    '''
    Goes thru all dates before NYT started including ebooks in lists and calls API on each date
    OUTPUT: list of dictionaries in json file
    '''
    dates = print_only_dates()
    for date in dates:
        hardcover_entry = call_api_once(date, list_name = 'hardcover-fiction')
        write_results_to_file(hardcover_entry, 'data/print_only_lists.json')
        time.sleep(5 + random() * 10)
        trade_paper_entry = call_api_once(date, list_name = 'trade-fiction-paperback')
        write_results_to_file(hardcover_entry, 'data/print_only_lists.json')
        time.sleep(5 + random() * 10)
        mass_paper_entry = call_api_once(date, list_name = 'mass-market-paperback')
        write_results_to_file(hardcover_entry, 'data/print_only_lists.json')
        time.sleep(5 + random() * 10)

def combined_list_dates():
    # combined list dates from 2/13/2011 to present
    beginning_date = datetime(2011, 2, 13)
    numdays = (datetime(2016, 11, 13) - beginning_date).days
    dates = [beginning_date.strftime('%Y-%m-%d')]
    for d in xrange(7, numdays + 7, 7):
        cur_date = (beginning_date + timedelta(days = d)).strftime('%Y-%m-%d')
        dates.append(cur_date)
    return dates

def get_combined_lists():
    dates = combined_list_dates()
    for date in dates:
        entry = call_api_once(date, list_name = 'combined-print-and-e-book-fiction')
        write_results_to_file(entry, 'data/combined_lists.json')
        time.sleep(5 + random() * 10)
