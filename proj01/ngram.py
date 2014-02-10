import re

class unigram():
    #Reads a text file in and converts it into an array
    def __init__(self, sourceFile):
        with open(sourceFile) as corpus:
            self.corpus = re.split('\s+', corpus.read())
        self.counts = dict()


class bigram():
    #Reads a text file in and converts it into an array
    def __init__(self, sourceFile):
        with open(sourceFile) as corpus:
            self.corpus = re.split('\s+', corpus)

