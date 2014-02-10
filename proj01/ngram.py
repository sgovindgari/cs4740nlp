import re, random, time
from collections import OrderedDict

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

# Generalized n-gram model - O(nN) or something
class ngram():
    def __init__(self, sourceFile, n = 1):
        with open(sourceFile) as corpus:
            self.corpus = re.split('\s+', corpus.read())
        self.counts = [dict()]*n
        for i in range(len(self.corpus)):
            word = self.corpus[i]
            prevs = list()
            for j in range(n):
                if i-j >= 0:
                    # Get the previous words
                    if(j > 0):
                        prevs.append(self.corpus[i-j])
                    lookup = tuple(reversed(prevs))
                    if lookup in self.counts[j]:
                        if word in self.counts[j][lookup]:
                            self.counts[j][lookup][word] += 1
                        else: 
                            self.counts[j][lookup][word] = 1
                    else:
                        self.counts[j][lookup] = dict()
                        self.counts[j][lookup][word] = 1

# TODO: How do we generate the first word in a bigram model. Do we use
# the probability of a period followed by a word, or the probability of <s> followed by a word or the unigram probability?