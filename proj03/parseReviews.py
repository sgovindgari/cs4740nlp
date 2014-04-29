#!/usr/bin/env python

from itertools import izip
import utilities # custom cleaning functions
from sentiwordnet import SentiWordNetCorpusReader, SentiSynset

swn = SentiWordNetCorpusReader('SentiWordNet_3.0.0_20130122.txt')

trainingData = 'data/training_data.txt'
testData     = 'data/test_data_no_true_labels.txt'

def strToSentiment(string, defaultToZero = False):
    if defaultToZero: return 0
    if string == 'pos': return 1
    if string == 'neu': return 0
    if string == 'neg': return -1
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

# returns a dictionary that maps every word in the reviews to
# a word sentiment: -1, 0, 1
def wordSentimentMapBasic(reviews):
    sentMap = {}
    for review in reviews:
        for line in review[1]:
            sent = line[0]
            wordList = line[1].split()
            for word in wordList:
                counts = sentMap.get(word, [0,0,0])
                if sent == -1:
                    counts[0] += 1
                if sent == 0:
                    counts[1] += 1
                if sent == 1:
                    counts[2] += 1
                sentMap[word] = counts
    for (word, sentCount) in sentMap.iteritems():
        sentMap[word] = sentArgmax(sentCount[0], sentCount[1], sentCount[2])
    return sentMap

# writes out the reviews as features to the file destination
# if bucket_size != 0, then bucket the results
def writeOutReviewFeatures(reviews, sentMap, destination, bucket_size = 0):
    with open(destination, 'w') as d:
        for review in reviews:
            name = review[0]
            d.write(name + "\n")
            for line in review[1]:
                sentence_label = line[0]
                wordList = line[1].split()
                sentList = []
                for word in wordList:
                    if word in sentMap:
                        sentList.append(sentMap[word])
                features = [0.,0.,0.]
                for sent in sentList:
                    if sent == -1:
                        features[0] += 1
                    if sent == 0:
                        features[1] += 1
                    if sent == 1:
                        features[2] += 1
                totalCount = sum(features)
                if (totalCount != 0):
                    features = [x/totalCount for x in features]
                if (bucket_size != 0):
                    features = [int(x/bucket_size) for x in features]
                d.write(str(sentence_label)+" ")
                for i in range(len(features)):
                    space = ' '
                    if i == len(features) - 1:
                        space = ''
                    d.write(str(i)+":"+str(features[i])+space)
                d.write("\n")
            d.write("\n")

def writeOutSentiWordNetFeatures(reviews, destination, binary=True, bucket_size = 0):
    with open(destination, 'w') as d:
        for review in reviews:
            name = review[0]
            d.write(name + "\n")
            for line in review[1]:
                sentence_label = line[0]
                wordList = line[1].split()
                sentList = []
                for word in wordList:
                    sent = getSentiWordNetScores(word)
                    if binary:
                        sent = sentArgmax(sent[0], sent[1], sent[2])
                    sentList.append(sent)
                features = [0., 0., 0.]
                for sent in sentList:
                    if binary:
                        if sent == -1:
                            features[0] += 1
                        if sent == 0:
                            features[1] += 1
                        if sent == 1:
                            features[2] += 1
                    else:
                        features[0] += sent[0]
                        features[1] += sent[1]
                        features[2] += sent[2]
                totalCount = sum(features)
                if (totalCount != 0):
                    features = [x/totalCount for x in features]
                if (bucket_size != 0):
                    features = [int(x/bucket_size) for x in features]
                d.write(str(sentence_label)+" ")
                for i in range(len(features)):
                    space = ' '
                    if i == len(features) - 1:
                        space = ''
                    d.write(str(i)+":"+str(features[i])+space)
                d.write("\n")
            d.write("\n")

def getSentiWordNetScores(word):
    synsets = swn.senti_synsets(word)
    neg = neu = pos = 0
    if (len(synsets) == 0):
        return (neg, neu, pos)

    for synset in synsets:
        neg += synset.neg_score
        neu += synset.obj_score
        pos += synset.pos_score

    return (neg, neu, pos)

#File formatting for Mallet - TODO
def writeForMallet(filename, featurefile, destination):
    with open(destination, 'w') as d:
        with open(filename) as f, open(featurefile) as  fe:
                for x, y in izip(f, fe):
                    x = x.strip()
                    y = y.strip()
                    print("{0}\t{1}".format(x, y))                  

def sentArgmax(negScore, neuScore, posScore):
    if (negScore > neuScore and negScore > posScore):
        sent = -1
    elif (posScore > negScore and posScore > neuScore):
        sent = 1
    else:
        sent = 0
    return sent

trainReviews = getReviewList(trainingData, defaultToZero = False)
testReviews = getReviewList(testData, defaultToZero = True)
sentMap = wordSentimentMapBasic(trainReviews)

# #print reviews
writeOutReviewFeatures(trainReviews, sentMap, "data/basic_features_discard_unseen_train.txt")
writeOutReviewFeatures(testReviews, sentMap, "data/basic_features_discard_unseen_test.txt")
for i in [0.01, 0.05, 0.1, 0.2]:
    writeOutReviewFeatures(trainReviews, sentMap, "data/basic_features_discard_unseen_bucket" + str(i) + "_train.txt", bucket_size=i)
    writeOutReviewFeatures(testReviews, sentMap, "data/basic_features_discard_unseen_bucket" + str(i) + "_test.txt", bucket_size=i)
    writeOutSentiWordNetFeatures(trainReviews, "data/sentiWordNet_features_binary_bucket" + str(i) + "_train.txt", binary=True, bucket_size = i)
    writeOutSentiWordNetFeatures(testReviews, "data/sentiWordNet_features_binary_bucket" + str(i) + "_test.txt", binary=True, bucket_size = i)
    writeOutSentiWordNetFeatures(trainReviews, "data/sentiWordNet_features_score_bucket" + str(i) + "_train.txt", binary=False, bucket_size = i)
    writeOutSentiWordNetFeatures(testReviews, "data/sentiWordNet_features_score_bucket" + str(i) + "_test.txt", binary=False, bucket_size = i)

