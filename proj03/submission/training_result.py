#!/usr/bin/env python

print "executing..."

import parseReviews

print "executing..."

def get_train_data(filename, destination):
    with open(destination, 'w') as d:
        with open(filename) as f:
            result = dict()
            print 'inside script'
            lst = parseReviews.getReviewList(filename)
            d.write('Id,Answer' + '\n')
            print 'writing to file'
            for i in lst:
                linelst = i[1]
                k = 0
                for j in linelst:
                    result[j[1].strip()] = j[0]
                    d.write(str(k)+ "," + str(j[0]) + "\n")
                    k = k+1
            d.close()
            return result

def accuracy(expected, actual):
    with open(expected):
        with open(actual):
            

print "wil call get_train_data"

get_train_data('data/training_data.txt', 'data/training_results.csv')
