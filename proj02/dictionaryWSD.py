#!/usr/bin/env python
# may require package install

import utilities, pprint, math

# xml parser!
from lxml import etree

# read original dictionary.xml, fix errors, write to dictionary_processed.xml
# provided dictionary file is meant only for the target words
dictionarySource    = 'dictionary.xml'
dictionaryProcessed = 'dictionary_processed.xml'

# takes an xml tree generated from etree.parse,
#   converts it into a nice dictionary!
def parseIntoDictionary(xml, clean=True):
    # dictionary of word to tuple
    # dict :  word -> ('part-of-sp', subdict)
    # where subdict : senseid -> ('def', ['exampleslist'], [wordnet ints])
    dictionary = dict()
    root = xml.getroot() # <dictmap>
    for lexelt in root: # looks like there are exactly 100
        #lexelt.attrib['item'] is something like 'begin.v' or 'network.n'
        word,pos = tuple(lexelt.attrib['item'].split('.'))
        senses = dict()
        for sense in lexelt: # accumulate senses dictionary for word
            attr = sense.attrib
            sid = int(attr['id']) # 1, 2, 3, etc
            # wordnet is a list of ints. handle the empty case:
            try: wordnet = map(int, attr['wordnet'].split(',')) # [2,3,4]
            except: wordnet = []
            gloss = attr['gloss'].strip() # definition
            examples = attr['examples'].split(' | ') # ['hi','world']
            if clean: # then gloss and each example get cleaned!
                gloss = utilities.cleanString(gloss)
                for i in range(len(examples)):
                	examples[i] = utilities.cleanString(examples[i])
            senses[sid] = (gloss, examples, wordnet)
        dictionary[word] = (pos, senses)
    return dictionary

# TODO: strip out stop words and do stemming!!
class DictionaryWSD():
    def __init__(self, sourceXMLDict=dictionaryProcessed):
        self.XMLSource = sourceXMLDict
        self.xml = etree.parse(self.XMLSource) # read the xml into memory
        # parseIntoDictionary, default with cleaning (lemmatize, rm stopwords)
        self.dict = parseIntoDictionary(self.xml, True) # here's our lookup!
        # table is a dict :
        #     contextword -> (senseID, numOverlapWords, numConsecOverlapWords)
        self.table = dict() # TODO populate

    # precondition: sentence should be lemmatized before
    #returns the best sense of a word
    def Lesk(self, word, pos, sentence):
        best_sense = -1
        max_overlap = 0
        # of words in a sentence
        # assuming sentence is parsed already 
        # TODO- discuss the state of sentence - is it parsed or not? 
        context = sentence.split(' ')
        # what to do if word doesnt exist?
        # TODO - need a way to store different pos of a word and retrieve them accordingly
        list_of_senses = self.dict[word][1]
        for sense in list_of_senses:
            overlap = self.computeOverlap(word, list_of_senses[sense], context)
            if overlap > max_overlap:
                    max_overlap = overlap
                    best_sense = sense
        
        print best_sense
        return best_sense

    # returns the number of words in common between two sets
    # signature = set of words in the gloss and examples of sense
    def computeOverlap(self, target, signature, context, window=10):
       # relevant words = words with same pos
       overlap = 0
       position = context.index(target)
       window_pre = position-window
       window_post = position+1+window
       if window_pre < 0:
            window_pre = 0
       if window_post > len(context):
            window_post = len(context)
       pre_words = context[window_pre:position]
       post_words = context[position+1:window_post]

       # for now splitting it as list form
       def_words = signature[0].split(' ')
       dictionary = parseIntoDictionary(context)
       print "Pre words:\n", pre_words
       print "Post_words:\n", post_words
       print "Def words\n", def_words

       for word in def_words:
            for pre_word in pre_words:
                overlap = self.checkSenseOverlap(word, pre_word)
            for post_word in post_words:
                overlap = self.checkSenseOverlap(word, post_word)

       #print overlap
       return overlap

    def checkSenseOverlap(self, word, context_word, dictionary):
        # for each word in sentence get the definition
        # check overlaps between definitions
        overlap = 0
        print "Context word:\n", context_word
        get_def = dictionary[context_word][1]
        for sense in get_def: 
            # build a list of words containing meaning - Deal with when the word is not in wordNET
            lst = get_def[sense][0].split(' ')
            for wrd in lst:
                if wrd == word:
                    overlap = overlap+1
        return overlap

    def printexample(self):
        print 'Example:\n', 'begin :', self.dict['begin']
        #print 'sense: \n', self.dict['begin'][1]
        for sense in self.dict['begin'][1]:
            print "Sense:\n", self.dict['begin'][1][sense]

# MAIN
# preprocess dictionary XML:
#   remove one instance of double sense, fix all '"' characters in examples
utilities.fixDoubles(dictionarySource, dictionaryProcessed)

dwsd = DictionaryWSD(dictionaryProcessed)
dwsd.printexample()
dwsd.Lesk('begin', 'v', 'begin attain freedom')
