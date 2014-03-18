#!/usr/bin/env python
# may require package install

import utilities, pprint, math

# xml parser!
from lxml import etree
# do we care if wordnet is 3.0 rather than 2.1? Check Piazza!
from nltk.corpus import wordnet as wn

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

class DictionaryWSD():
    def __init__(self, sourceXMLDict=dictionaryProcessed):
        self.XMLSource = sourceXMLDict
        self.xml = etree.parse(self.XMLSource) # read the xml into memory
        # parseIntoDictionary, default with cleaning (lemmatize, rm stopwords)
        self.dict = parseIntoDictionary(self.xml, True) # here's our lookup!
        # table is a dict :
        #     contextword -> (senseID, numOverlapWords, numConsecOverlapWords)
        self.table = dict() # TODO populate
        # cache structure: signature[0] -> word -> pre_word -> int
        self.overlapCache = dict() # cache for overlap lookups

    # precondition: sentence should be lemmatized before
    #returns the best sense of a word
    def Lesk(self, word, pos, pre_words, post_words):
        best_sense = -1
        max_overlap = 0

        # what to do if word doesnt exist?
        # TODO - need a way to store different pos of a word and retrieve them accordingly
        list_of_senses = []
        if word in self.dict:
            list_of_senses = self.dict[word][1]
        else:
            lst_tup = dict()
            i = 1
            for synset in wn.synsets(word): # may be empty!
                # clean definition - check this
                lst_tup.update({i : (utilities.cleanString(synset.definition), [], [])})
                i += 1
            self.dict.update({word: (synset.pos, lst_tup)})
            list_of_senses = self.dict[word][1]

        #print list_of_senses
        for sense in list_of_senses: # length list_of_senses is approx 5
            #print "Senses:\n", sense, list_of_senses[sense]
            overlap = self.computeOverlap(word, list_of_senses[sense], pre_words, post_words)
            #print "!!!!", sense, "Overlap:", overlap
            if overlap > max_overlap:
                max_overlap = overlap
                best_sense = sense
        #print "Best Sense is: ", best_sense

        # if no best sense is returned default to the sense that is most frequently used - top sense
        if best_sense == -1:
            #print "No sense found using common sense"
            for sense in list_of_senses:
                best_sense = sense
                break
        return best_sense

    # returns the number of words in common between two sets
    # signature = set of words in the gloss and examples of sense
    def computeOverlap(self, target, signature, pre_words, post_words):
       # relevant words = words with same pos
       overlap = 0

       # for now splitting it as list form
       def_words = signature[0].split(' ')

       #print "  Pre words:", pre_words
       #print "  Post_words:", post_words
       #print "  Def words", def_words

       for word in def_words:
            for pre_word in pre_words:
                
                # here it is with caching
                if signature[0] not in self.overlapCache:
                    self.overlapCache[signature[0]] = dict()
                if word not in self.overlapCache[signature[0]]:
                    self.overlapCache[signature[0]][word] = dict()
                if pre_word not in self.overlapCache[signature[0]][word]:
                    overlapval = self.checkSenseOverlap(word, pre_word, signature[0])
                    self.overlapCache[signature[0]][word][pre_word] = overlapval
                    overlap += overlapval
                else:
                    overlap += self.overlapCache[signature[0]][word][pre_word]
                
                #overlap += self.checkSenseOverlap(word, pre_word, signature[0])
            for post_word in post_words:
                # here it is with caching
                if signature[0] not in self.overlapCache:
                    self.overlapCache[signature[0]] = dict()
                if word not in self.overlapCache[signature[0]]:
                    self.overlapCache[signature[0]][word] = dict()
                if post_word not in self.overlapCache[signature[0]][word]:
                    overlapval = self.checkSenseOverlap(word, post_word, signature[0])
                    self.overlapCache[signature[0]][word][post_word] = overlapval
                    overlap += overlapval
                else:
                    overlap += self.overlapCache[signature[0]][word][post_word]
                #overlap += self.checkSenseOverlap(word, post_word, signature[0])

       #print overlap
       return overlap

    # returns the number of consecutive overlaps given two parsed sentences
    def consecutiveOverlaps(self, sent1, sent2):
        #print "Consecutive overlaps\n"
        #print sent1
        #print sent2
        sent2 = sent2.split(' ')
        #print sent2
        con_overlap = 0
        for i in range(0, len(sent2)-1):
            consecutive = sent2[i] + ' ' + sent2[i+1]
            #print consecutive
            if sent1.find(consecutive) != -1:
                con_overlap += 1
        #print con_overlap
        return con_overlap


    def checkSenseOverlap(self, word, context_word, signature):
        # for each word in sentence get the definition
        # check overlaps between definitions
        overlap = 0
        con_overlap = 0
        context_overlap = 0

        if context_word == word:
            context_overlap += 1

        if context_word in self.dict:
            #print "Context word:", context_word
            get_def = self.dict[context_word][1]

            for sense in get_def:
                #print "In dictionary"
                con_overlap += self.consecutiveOverlaps(get_def[sense][0], signature)
                lst = get_def[sense][0].split(' ')
                for wrd in lst:
                    if wrd == word:
                        overlap += 1
        else: # do WordNet lookup
            #print "Lookin' up", context_word, "in Wordnet..."
            # may be empty! if so, automatically ignored
            for synset in wn.synsets(context_word):
                # clean definition
                defin = utilities.cleanString(synset.definition).split(' ')
                #print "Not in dictionary"
                con_overlap += self.consecutiveOverlaps(utilities.cleanString(synset.definition), signature)
                for wrd in defin:
                    if wrd == word:
                        overlap += 1

        # metric that rewards consecutive overlaps more than distant overlaps - We can have another metric with examples included
        overlap = 0.5*con_overlap + 0.4*overlap + 0.1*context_overlap
        return overlap

    def printexample(self):
        print 'Example:\n', 'begin :', self.dict['begin']
        #print 'sense: \n', self.dict['begin'][1]
        #for sense in self.dict['begin'][1]:
            #print "Sense:\n", self.dict['begin'][1][sense]


# MAIN
# preprocess dictionary XML:
#   remove one instance of double sense, fix all '"' characters in examples
utilities.fixDoubles(dictionarySource, dictionaryProcessed)

dwsd = DictionaryWSD(dictionaryProcessed)
#dwsd.printexample()
#dwsd.Lesk('begin', 'v', 'begin to attain freedom')
#dwsd.Lesk('pine', 'n', 'pine cone')

def processTestFile(filename, destination):
    with open(destination, 'w') as d:
        f = open(filename)
        d.write("Id, Prediction\n")
        i = 0
        for line in f:
            lst = line.split('|')
            #print lst
            word_pos = lst[0].strip().split('.')
            word = word_pos[0]
            pos = word_pos[1]
            gloss = lst[2].strip().split('%%')
            context = gloss[0] + gloss[1] + gloss[2]

            pre_words = gloss[0].strip().split(' ')
            pre_words = pre_words[-10:]

            post_words = gloss[2].strip().split(' ')
            post_words = post_words[-10:]

            print "Target: ", word
            #print "Context: ", context
            #print "POS: ", pos

            # algorithm bottleneck is HERE
            sense = dwsd.Lesk(word, pos, pre_words, post_words)
            i += 1
            d.write("" + str(i) + ", " + str(sense) + "\n")

        d.close()

processTestFile('test_clean.data', 'test_prediction.data')
