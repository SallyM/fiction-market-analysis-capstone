import os
import json
import time

with open('data/isbns.txt', 'r') as i:
    isbns = []
    for line in i:
        isbns.append(str(i))

with open("data/book_reviews.json", 'r') as input_file:
    if not os.path.isfile('data/join_reviews_test.json'):
        output_file = open('data/join_reviews_test.json', mode='w+')
    else:
        output_file = open('data/join_reviews_test.json', mode='a')
    for i, line in enumerate(input_file):
        for isbn in isbns:
            if isbn in line:
                output_file.write(line.encode('utf-8'))
        if i % 100000 == 0:
            print '{} lines checked successfully!'.format(i)
    output_file.close()
