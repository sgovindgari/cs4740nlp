#!/usr/bin/env python

# Began by individually creating a unigram and bigram model class,
#   but decided the redundancy was too much so moved onto n-gram
# For random sentence generation we chose to use backoff
#   (reverting to n-1 gram or n-2 gram, etc. as necessary)

import re, random, time
from collections import OrderedDict

# enum definition (used for Smooth and Direction)
def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)

Smooth = enum('NONE', 'GOOD_TURING', 'ADD_ONE')
Direction = enum('RL', 'LR')

'''
# obsolete unigram class
class unigram():
    #Reads a text file in and converts it into an array
    def __init__(self, sourceFile, n = 1):
        with open(sourceFile) as corpus:
            self.corpus = re.split('\s+', corpus.read())
        self.counts = OrderedDict()
        self.probs = OrderedDict()
        self.total = 0
        self.bigram_counts = OrderedDict()
        for i in range(len(self.corpus)):
            self.total += 1
            entry = self.corpus[i]
            if entry in self.counts:
                self.counts[entry] += 1
            else:
                self.counts[entry] = 1
        #Can calculate probability here if we want
        for word in self.counts:
            self.probs[word] = self.counts[word]/float(self.total)

    #Very naive, takes O(V)
    def randomWord(self):
        p = random.random()
        for word in self.probs:
            p -= self.probs[word]
            if p < 0:
                return word
'''

# Generalized n-gram model - O(nN) or something
class ngram():
    # defaults: unigram, no smoothing, left-to-right
    def __init__(self, sourceFile, n = 1, smooth = Smooth.NONE, direction = Direction.LR):
        with open(sourceFile) as corpus:
            self.corpus = re.split('\s+', corpus.read().lower())

            # extension: right-to-left ngram: simply reverse the corpus
            # note: reversed again in function randomSentence
            if direction == Direction.RL:
                self.corpus.reverse()

        # testing only
        self.corpus = self.corpus[:46]

        self.n = n
        self.smooth = smooth
        self.direction = direction

        # This stores dictionaries for recording counts of the p previous words followed by a word
        # i.e. for a bigram model it stores the unigram counts and bigram counts
        # Each dictionary then holds an entry (another dict) for each tuple of previous words
        # i.e. for unigram there is only one entry: [((), [(the,5),(a,6),(cat,2),...])]
        # for bigram there would be [('the',[('cat', 3),('dog', 4),...]),('a',[(cow, 2),(horse, 1),...]),...]
        # Summary: self.counts is a list of dicts of dicts where each entry in the list is a model
        self.counts = [{} for _ in range(self.n)]
        self._initializeNgram()
        self._smoothing()
        self._generateProbabilities()

    def _initializeNgram(self):
        for i in range(len(self.corpus)):
            word = self.corpus[i]
            prevs = list()
            # construct all ngrams at once
            for j in range(self.n):
                # if i-j, handle first words (when i < n), don't look too far back
                if i-j >= 0:
                    # Add another word to the previous words
                    if(j > 0):
                        prevs.append(self.corpus[i-j])
                    # Must convert to tuple to hash into dictionary,
                    # reverse list to keep words in the correct order
                    lookup = tuple(reversed(prevs))
                    if lookup in self.counts[j]:
                        if word in self.counts[j][lookup]:
                            self.counts[j][lookup][word] += 1
                        else:
                            self.counts[j][lookup][word] = 1
                    else:
                        self.counts[j][lookup] = dict()
                        self.counts[j][lookup][word] = 1

    def _smoothing(self):
        # TODO: Do smoothing
        if self.smooth == Smooth.NONE:
            pass
        # General approach, for <unk> simply add an entry to each row for each i-gram table
        # Give it a count of 1, for words that did not show up for that row, but do show up in the
        # vocabulary, add to each row with a value of 1 and add 1 to each entry
        elif self.smooth == Smooth.ADD_ONE:
            # fill entire table with 0s if no entry.
            # add 1 to all entries in table.
            # denominator (total = self._sumDict(ngram[row])) is taken care of
            # for i in range(self.n):
            #     ngram = self.counts[i]
            #     for row in ngram:
            #         for entry in ngram[row]:
            #             # add 1 to every entry
            #             entry += 1
            pass
        elif self.smooth == Smooth.GOOD_TURING:
            pass

    def _generateProbabilities(self):
        # self.probs stores the probability tables (dicts of dicts) for each i-gram, for i = 1...n
        self.probs = [{} for _ in range(self.n)]
        for i in range(self.n):
            ngram = self.counts[i]
            for row in ngram:
                total = self._sumDict(ngram[row])
                self.probs[i][row] = OrderedDict()
                for entry in ngram[row]:
                    self.probs[i][row][entry] = ngram[row][entry] / float(total)

    # Sum the values of the dictionary and returns the total
    def _sumDict(self, d):
        total = 0
        for k, v in d.iteritems():
            total += v
        return total

    # Generates a random sentence using this model
    def randomSentence(self):
        # Prev stores the previously generated words to consider
        prev = list()
        if self.n != 1:
            #Should we start with <s>? or nothing? or something else...
            prev = ['<s>']
        # The words generated thus far are stored in res
        res = ['<s>']
        # Generate words until a sentence segmentor is created
        while True:
            word = ''
            gram = self.probs[len(prev)]
            if tuple(prev) in gram:
                word = self.generateWord(gram[tuple(prev)])
                prev.append(word)
                res.append(word)
                # Maintain only as many previous words as the model allows
                if len(prev) >= self.n:
                    prev.pop(0)
            # if the entry doesn't exist, try using the previous t-1 words instead
            else:
                prev.pop(0)
            if word == '<s>':
                break

        # extension: right-to-left ngram: simply reverse the corpus
        if self.direction == Direction.RL:
            res.reverse()
        print ' '.join(res)
        return ' '.join(res)

    # Given a dictionary of (words, probability) generate a random word drawn from this distribution
    def generateWord(self, row):
        p = random.random()
        for word in row:
            p -= row[word]
            if p < 0:
                return word

    # Takes a word and a list of previous words and returns the probability of that word
    def getProbability(self, word, prev):
        tp = tuple(prev)
        if tp in self.probs[len(prev)]:
            if word in self.probs[len(prev)][tp]:
                return self.probs[len(prev)][tp][word]
            return self.probs[len(prev)][tp]['<unk>']
        #TODO: Uh oh, what do we do if we haven't seen the previous words, must account for in smoothing somehow?
        return 0


# Construction time test
def ngram_model_test(source, maxN = 4):
    for i in range(1,maxN+1):
        start = time.time()
        a = ngram(source, i)
        print str(i)+'-gram: ' + str(time.time() - start)
        a.randomSentence()

def sentenceGeneration():
    bug = ngram('bible.train', 1)
    bbg = ngram('bible.train', 2)
    rug = ngram('raw_reviews.train', 1)
    rbg = ngram('raw_reviews.train', 2)
    fbug = open('fbug','w')
    fbbg = open('fbbg','w')
    frbg = open('frbg','w')
    frug = open('frug','w')
    for i in range(10):
        fbug.write(bug.randomSentence() + "\n\n")
        fbbg.write(bbg.randomSentence() + "\n\n")
        frug.write(rug.randomSentence() + "\n\n")
        frbg.write(rbg.randomSentence() + "\n\n")
    fbug.close()
    fbbg.close()
    frug.close()
    frbg.close()

# MAIN
# temp for testing
# a = ngram('bible.train', 3)

def perplexity(train, test, n = 1, smoothing = Smooth.NONE):
    ng = ngram(train, n, smoothing)
    test_corpus = None
    with open(test) as corp:
        test_corpus = re.split('\s+', corp.read().lower())
    pp = 1
    prev = []
    for word in test_corpus:
        print ng.getProbability(word, prev)
        pp *= (1/ng.getProbability(word, prev))
        prev.append(word)
        if len(prev) >= n:
            prev.pop(0)
    res = pp**(1.0/len(test_corpus))
    return res