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
        # This stores dictionaries for recording counts of the p previous words followed by a word
        # i.e. for a bigram model it stores the unigram counts and bigram counts
        # Each dictionary then holds an entry (another dict) for each tuple of previous words
        # i.e. for unigram there is only one entry: [((), [(the,5),(a,6),(cat,2),...])]
        # for bigram there would be [('the',[('cat', 3),('dog', 4),...]),('a',[(cow, 2),(horse, 1),...]),...]
        # Summary: self.counts is a list of dicts of dicts where each entry in the list is a model
        self.counts = [dict()]*n
        # self.corpus = ['a', 'b', 'a', 'c']
        self.n = n
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

        # Generate probabilities
        self.probs = [dict()]*n
        for i in range(n):
            ngram = self.counts[i]
            for row in ngram:
                total = self._sumDict(ngram[row])
                self.probs[i][row] = OrderedDict()
                for entry in ngram[row]:
                    self.probs[i][row][entry] = ngram[row][entry] / float(total)

    def _sumDict(self, d):
        total = 0
        for k, v in d.iteritems():
            total += v
        return total

    def randomSentence(self):
        prev = list()
        if self.n != 1:
            prev = ['<s>']
        res = list()
        while True:
            word = ''
            gram = self.probs[len(prev)]
            if tuple(prev) in gram:
                word = self.generateWord(gram[tuple(prev)])
                prev.append(word)
                res.append(word)
                if len(prev) >= self.n:
                    prev.pop(0)
            else:
                prev.pop(0)
            if word == '<s>':
                break
        print ' '.join(res)

    def generateWord(self, row):
        p = random.random()
        for word in row:
            p -= row[word]
            if p < 0:
                return word

# TODO: How do we generate the first word in a bigram model. Do we use
# the probability of a period followed by a word, or the probability of <s> followed by a word or the unigram probability?