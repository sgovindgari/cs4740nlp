#!/usr/bin/env python

import utilities # custom cleaning functions

trainingData = 'data/training_data.txt'
testData     = 'data/test_data_no_true_labels.txt'

def strToSentiment(str, defaultToZero = False):
    if defaultToZero: return 0
    if str == 'pos': return 1
    if str == 'neu': return 0
    if str == 'neg': return -1
    else: return 0 # is this going to be our procedure?

# collects reviews in the datafile into a list.
# param defaultToZero is False by default, True for test data
# returns review: (name, line list)
#         line: ([pos 1|neu 0|neg -1], cleanedSentence)
def getReviewList(datafile, defaultToZero = False):
    reviews = [] # collect reviews in a list
    # review components
    name,lines = None, list()
    with open(datafile) as f:
        for line in f:
            line = tuple(line.strip().split('\t'))
            if len(line) == 1 and line[0] != '':
                # if line has no tab character, start of a new review.
                name = line[0]
            elif len(line) == 1 and line[0] == '':
                # end of review. collect results, append
                reviews.append((name, lines))
                name,lines = None, list()
            else: # len(line) == 2
                # remove stopwords, lemmatize, other cleans...
                sentiment = strToSentiment(line[0], defaultToZero)
                sentence = utilities.cleanString(line[1])
                lines.append((sentiment, sentence))
    return reviews

reviewList = getReviewList(trainingData, defaultToZero = False)
print reviewList
print len(reviewList)
