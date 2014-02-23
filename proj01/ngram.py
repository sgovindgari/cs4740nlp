#!/usr/bin/env python

# Began by individually creating a unigram and bigram model class,
#   but decided the redundancy was too much so moved onto n-gram
# For random sentence generation we chose to use backoff
#   (reverting to n-1 gram or n-2 gram, etc. as necessary)

import re, random, time
from collections import OrderedDict
import itertools # for cross product of 2 lists?
import math
from copy import copy

# enum definition (used for Smooth and Direction)
def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)

Smooth = enum('NONE', 'GOOD_TURING', 'ADD_ONE')
Direction = enum('RL', 'LR')

# Generalized n-gram model - O(nN) or something
class ngram():
    # defaults: unigram, no smoothing, left-to-right
    def __init__(self, sourceFile, n = 1, smooth = Smooth.NONE, useUnk = False, direction = Direction.LR):
        with open(sourceFile) as corpus:
            self.corpus = re.split('\s+', corpus.read().lower())

            # extension: right-to-left ngram: simply reverse the corpus
            # note: reversed again in function randomSentence
            if direction == Direction.RL:
                self.corpus.reverse()

        self.n = n
        self.smooth = smooth
        self.goodTuringLimit = 12
        self.direction = direction

        # This stores dictionaries for recording counts of the p previous words followed by a word
        # i.e. for a bigram model it stores the unigram counts and bigram counts
        # Each dictionary then holds an entry (another dict) for each tuple of previous words
        # i.e. for unigram there is only one entry: [((), [(the,5),(a,6),(cat,2),...])]
        # for bigram there would be [('the',[('cat', 3),('dog', 4),...]),('a',[(cow, 2),(horse, 1),...]),...]
        # Summary: self.counts is a list of dicts of dicts where each entry in the list is a model
        self.counts = [dict() for _ in range(self.n)]
        self.ngramFreqs = [dict() for _ in range(self.n)] # populated later during smoothing
        self.probs = [dict() for _ in range(self.n)]

        # generate unks after if we reverse!!!
        if useUnk:
            self.seenWords = set()
            for i in range(len(self.corpus)):
                word = self.corpus[i]
                if word not in self.seenWords and word != '<s>':
                    self.corpus[i] = '<unk>'
                self.seenWords.add(word)

        # unordered unique words (for use in smoothing) (after unk replacement)
        self.uniques = list(set(self.corpus))
        self.uniqueCount = len(self.uniques) # V

        self._initializeNgram()
        self._populateNgramFreqs() # not really necessary if no smoothing...
        # smoothingFunction takes in i and nv (nv is count?)
        self.smoothingFunction = self._smoothing()
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

    # returns a function?? self.ngramFreqs
    def _smoothing(self):
        if self.smooth == Smooth.NONE:
            iden = lambda i,nv: nv
            return iden

        # General approach, for <unk> simply add an entry to each row for each i-gram table
        # Give it a count of 1, for words that did not show up for that row, but do show up in the
        # vocabulary, add to each row with a value of 1 and add 1 to each entry
        if self.smooth == Smooth.ADD_ONE:
            addonefun = lambda i,nv: 1 + nv
            # fix. what if entry not found? and update denom

            # fill entire table with 0s if no entry.
            # add 1 to all entries in table.
            # denominator (total = self._sumDict(ngram[row])) is taken care of
            # for i in range(self.n):
            #     ngram = self.counts[i]
            #     for row in ngram:
            #         for entry in ngram[row]:
            #             # add 1 to every entry
            #             entry += 1
            return addonefun # INCORRECT
        elif self.smooth == Smooth.GOOD_TURING:
            # NOTE: we will do Good-Turing smoothing up to self.goodTuringLimit (12).
            # We can also implement simple Good-Turing smoothing:
            #   replace empirical N_k with best-fit power law
            #   once count counts get unreliable

            # function taking in ngram val (i), count nv, returns new cstar count
            def goodTuringFunction(i,nv):
                if nv < self.goodTuringLimit:
                    cstar = (nv + 1.0) * self.ngramFreqs[i][nv+1] / self.ngramFreqs[i][nv]
                    return cstar
                else:
                    return nv

            return goodTuringFunction

    # countNGrams returns a dictionary of int to int to self.ngramFreqs
    # 2 -> 35 means there are 35 ngrams that appear 2 times
    # self.ngramFreqs[i] --> N_i = number of ngrams appearing i times
    def _populateNgramFreqs(self):
        # build self.ngramFreqs
        for i in range(self.n):
            ngram = self.counts[i]
            for row in ngram:
                for entry in ngram[row]:
                    ngramCount = ngram[row][entry]
                    # print i, entry, ngramCount
                    if ngramCount in self.ngramFreqs[i]:
                        self.ngramFreqs[i][ngramCount] += 1
                    else:
                        self.ngramFreqs[i][ngramCount] = 1
            # below: how many ngrams have 0 counts
            sumrow = self._sumDict(self.ngramFreqs[i])
            # if 6 unique words, unique trigram count is 6^3 - sumrow
            self.ngramFreqs[i][0] = pow(self.uniqueCount,i+1) - sumrow
            # let's put an index that sums up the row (without 0 counts)
            self.ngramFreqs[i][-1] = sumrow + self.ngramFreqs[i][0]

    def _generateProbabilities(self):
        self.unigramProbs = OrderedDict()
        unigramCounts = self.counts[0][()]
        total = 0.0
        self.cache = dict()
        for entry in unigramCounts:
            self.unigramProbs[entry] = self.smoothingFunction(0,unigramCounts[entry])
            total += self.unigramProbs[entry]
        for entry in self.unigramProbs:
            self.unigramProbs[entry] = self.unigramProbs[entry]/total

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
            prev = ['<s>']
        # The words generated thus far are stored in res
        res = ['<s>']
        # Generate words until a sentence segmentor is created
        while True:
            word = ''
            row = self._getProbabilityRow(prev)
            word = self.generateWord(row)
            prev.append(word)
            res.append(word)
            # Maintain only as many previous words as the model allows
            if len(prev) >= self.n:
                prev.pop(0)
            if word == '<s>':
                break

        # extension: right-to-left ngram: simply reverse the corpus
        if self.direction == Direction.RL:
            res.reverse()
        return ' '.join(res)

    #Lazily calculates probability rows only when requested. Only the unigram is calculated and stored.
    def _getProbabilityRow(self, prev):
        n = len(prev)
        p = copy(prev)
        for i in range(len(p)):
            if p[i] not in self.unigramProbs:
                p[i] = '<unk>'
        tp = tuple(p)
        if tp == ():
            return self.unigramProbs
        elif tp in self.cache:
            return self.cache[tp]
        elif tp in self.counts[n]:
            #calculate row
            row = OrderedDict()
            countsRow = self.counts[n][tp]
            total = 0.0
            for entry in self.unigramProbs:
                if entry in countsRow:
                    row[entry] = self.smoothingFunction(n,countsRow[entry])
                else:
                    row[entry] = self.smoothingFunction(n,0)
                total += row[entry]
            for entry in row:
                row[entry] = row[entry] / total
            #Max size of cache
            if len(self.cache) < 1000:
                self.cache[tp] = row
            return row
        #Backoff to n-1 gram
        else:
            return None

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
        row = self._getProbabilityRow(prev)
        if row:
            if word in row:
                return row[word]
            elif '<unk>' in row:
                return row['<unk>']
            else:
                return self.getProbability(word, prev[1:])
        else:
            return self.getProbability(word, prev[1:])

    # Use backoff for missing tables
    def perplexity(self, test):
        test_corpus = None
        with open(test) as corp:
            test_corpus = re.split('\s+', corp.read().lower())
        if self.direction == Direction.RL:
                test_corpus.reverse()
        pp = 0
        prev = test_corpus[0:self.n-1]
        start = time.time()
        for i in xrange(self.n-1, len(test_corpus)):
            word = test_corpus[i]
            pp += math.log(1/self.getProbability(word, prev))
            prev.append(word)
            if len(prev) >= self.n:
                prev.pop(0)
            if i % 1000 == 0:
                #print time.time() - start
                start = time.time()
        pp *= (1.0/len(test_corpus))
        pp = math.exp(pp)
        return pp

def sentenceGeneration():
    bug = ngram('bible.train', 1)
    bbg = ngram('bible.train', 2)
    rug = ngram('raw_reviews.train', 1)
    rbg = ngram('raw_reviews.train', 2)
    fbug = open('fbug','w')
    fbbg = open('fbbg','w')
    frbg = open('frbg','w')
    frug = open('frug','w')
    for i in range(5):
        fbug.write("\\texttt{" + bug.randomSentence() + "}\\npar\n")
        fbbg.write("\\texttt{" + bbg.randomSentence() + "}\\npar\n")
        frug.write("\\texttt{" + rug.randomSentence() + "}\\npar\n")
        frbg.write("\\texttt{" + rbg.randomSentence() + "}\\npar\n")
    fbug.close()
    fbbg.close()
    frug.close()
    frbg.close()

a = ngram('raw_reviews.train',3,Smooth.GOOD_TURING,False,Direction.RL)
print a.randomSentence()
print a.randomSentence()
print a.randomSentence()
print a.randomSentence()
# print a.perplexity('bible.test')
# del a
