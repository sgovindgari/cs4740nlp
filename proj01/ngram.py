#!/usr/bin/env python

# Began by individually creating a unigram and bigram model class,
#   but decided the redundancy was too much so moved onto n-gram
# For random sentence generation we chose to use backoff
#   (reverting to n-1 gram or n-2 gram, etc. as necessary)

import re, random, time
from collections import OrderedDict
import itertools # for cross product of 2 lists?

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
        #self.corpus = self.corpus[:12029]
        #print self.corpus
        #self.corpus = ['<s>', 'the', 'cat', 'the', 'cat', 'the', 'cat', \
        #    'a', 'dog', 'the', 'dog', '.']

        self.n = n
        self.smooth = smooth
        self.goodTuringLimit = 12
        self.direction = direction

        # unordered unique words (for use in smoothing)
        self.uniques = list(set(self.corpus))
        self.uniqueCount = len(self.uniques) # V
        self.ngramFreqs = [dict() for _ in range(self.n)] # populated later during smoothing

        # This stores dictionaries for recording counts of the p previous words followed by a word
        # i.e. for a bigram model it stores the unigram counts and bigram counts
        # Each dictionary then holds an entry (another dict) for each tuple of previous words
        # i.e. for unigram there is only one entry: [((), [(the,5),(a,6),(cat,2),...])]
        # for bigram there would be [('the',[('cat', 3),('dog', 4),...]),('a',[(cow, 2),(horse, 1),...]),...]
        # Summary: self.counts is a list of dicts of dicts where each entry in the list is a model
        self.counts = [dict() for _ in range(self.n)]
        self._initializeNgram()
        self._populateNgramFreqs() # not really necessary if no smoothing...
        # smoothingFunction takes in i and nv (nv is count?)
        smoothingFunction = self._smoothing()
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
        # TODO: Do smoothing
        if self.smooth == Smooth.NONE:
            iden = lambda i,nv: nv
            return iden

        # the following is NOT AN OPTION: TOO MUCH MEM
        # tuples = list(itertools.product(*[self.uniques for _ in range(self.n - 1)]))

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

            # i, nv are args
            # print 2, self.ngramFreqs[2][-1]
            # print 2, 0, self.ngramFreqs[2][0]
            # print 2, 1, self.ngramFreqs[2][1]
            # print 2, 2, self.ngramFreqs[2][2]
            # print 'e', 0, self.ngramFreqs[2][1]
            # print 'e', 1, (1 + 1.0) * self.ngramFreqs[2][1+1] / self.ngramFreqs[2][1]
            # print 'e', 2, (2 + 1.0) * self.ngramFreqs[2][2+1] / self.ngramFreqs[2][2]
            # print 'e', 3, (3 + 1.0) * self.ngramFreqs[2][3+1] / self.ngramFreqs[2][3]
            # print 'e', 4, (4 + 1.0) * self.ngramFreqs[2][4+1] / self.ngramFreqs[2][4]
            # print 'e', 5, (5 + 1.0) * self.ngramFreqs[2][5+1] / self.ngramFreqs[2][5]
            # print 'e', 6, (6 + 1.0) * self.ngramFreqs[2][6+1] / self.ngramFreqs[2][6]
            # print 'e', 7, (7 + 1.0) * self.ngramFreqs[2][7+1] / self.ngramFreqs[2][7]
            # print 'e', 8, (8 + 1.0) * self.ngramFreqs[2][8+1] / self.ngramFreqs[2][8]
            # print 'e', 9, (9 + 1.0) * self.ngramFreqs[2][9+1] / self.ngramFreqs[2][9]
            # print 'e', 10, (10 + 1.0) * self.ngramFreqs[2][10+1] / self.ngramFreqs[2][10]
            # print 'e', 11, (11 + 1.0) * self.ngramFreqs[2][11+1] / self.ngramFreqs[2][11]
            # print 'e', 12, (12 + 1.0) * self.ngramFreqs[2][12+1] / self.ngramFreqs[2][12]

            # function taking in ngram val (i), count nv, returns new cstar count
            def goodTuringFunction(i,nv):
                if nv == 0:
                    cstar = self.ngramFreqs[i][nv+1]
                    print i,nv,cstar, self.ngramFreqs[i][nv]
                    return cstar
                elif nv < 12:
                    cstar = (nv + 1.0) * self.ngramFreqs[i][nv+1] / self.ngramFreqs[i][nv]
                    print i,nv,cstar, self.ngramFreqs[i][nv]
                    return cstar

            return goodTuringFunction

            #for i in range(self.n):
            #    for nv in range(self.goodTuringLimit): # 12 at the moment
            #        if nv == 0:
            #            cstar = self.ngramFreqs[i][nv+1] # cstar = N_1
            #            gtCounts[i][nv] = 1.0 * cstar
            #        else:
            #            cstar = (nv + 1.0) * self.ngramFreqs[i][nv+1] / self.ngramFreqs[i][nv]
            #            gtCounts[i][nv] = 1.0 * cstar
                #     if nv == 0:
                #         cstar = self.ngramFreqs[i]
                #         print i, nv
                #         print self.ngramFreqs[i][nv]

            # step through self.counts (each n-gram)
            # for i in range(self.n):
            #     ngram = self.counts[i]
            #     print ngram

            #print self.uniqueCount
            #print pow(self.uniqueCount,self.n)

            #currentTuple = ()
            #for i in range(self.n):
            #    for uidx in range(len(self.uniques)):
            #        currentTuple.append(self.uniques)
            #        print currentTuple

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
            self.ngramFreqs[i][-1] = sumrow

    def _generateProbabilities(self):
        #exit ()
        # self.probs stores the probability tables (dicts of dicts) for each i-gram, for i = 1...n
        self.probs = [{} for _ in range(self.n)]
        for i in range(self.n):
            ngram = self.counts[i]
            for row in ngram:
                total = self._sumDict(ngram[row])
                self.probs[i][row] = OrderedDict()
                for entry in ngram[row]:
                    self.probs[i][row][entry] = ngram[row][entry] / float(total)
                    if self.smooth == Smooth.GOOD_TURING:
                        print self.probs[i][row][entry]

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
    for i in range(5):
        fbug.write("\\texttt{" + bug.randomSentence() + "}\\npar\n")
        fbbg.write("\\texttt{" + bbg.randomSentence() + "}\\npar\n")
        frug.write("\\texttt{" + rug.randomSentence() + "}\\npar\n")
        frbg.write("\\texttt{" + rbg.randomSentence() + "}\\npar\n")
    fbug.close()
    fbbg.close()
    frug.close()
    frbg.close()

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

# MAIN
# temp for testing
a = ngram('bible.train', 3, Smooth.GOOD_TURING)
#sentenceGeneration()
