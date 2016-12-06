import os
import json
import time

#
# with open("data/book_reviews.json", 'r') as input_file:
#     if not os.path.isfile('data/join_reviews_test.json'):
#         output_file = open('data/join_reviews_test.json', mode='w+')
#     else:
#         output_file = open('data/join_reviews_test.json', mode='a')
#     for i, line in enumerate(input_file):
#         for isbn in isbns:
#             if isbn in line:
#                 output_file.write(line.encode('utf-8'))
#         if i % 100000 == 0:
#             print '{} lines checked successfully!'.format(i)
#     output_file.close()




with open("data/book_reviews.json", 'r') as input_file:
    reviews = (json.loads(line) for line in input_file)
    i = 0
    j = 0
    with open('data/isbns.txt', 'r') as isbns:
        list_of_isbns = [l.strip() for l in isbns]
    for line in reviews:
        i += 1
        if line['asin'] in list_of_isbns:
            j += 1
            if not os.path.isfile('data/join_reviews.json'):
                with open('data/join_reviews.json', mode='w') as output_file:
                    output_file.write(json.dumps(line, indent = 2))
            else:
                with open('data/join_reviews.json', mode='a') as output_file:
                    output_file.write(json.dumps(line, indent = 2))
        if i % 100000 == 0:
            print '{} lines checked. {} lines written.'.format(i, j)
