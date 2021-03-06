#!/usr/bin/env python
# may require package install

import utilities, pprint, math, time

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
    def Lesk(self, word, pos, pre_words, post_words,softScoring=False,alpha=0.5):
        scores = dict()
        # what to do if word doesnt exist?
        # TODO - need a way to store different pos of a word and retrieve them accordingly
        list_of_senses = []
        if word in self.dict:
            wordpos, list_of_senses = self.dict[word]
        else: # we don't know pos, senses, or definition. should not happen from test data
            lst_tup = dict()
            i = 1
            for synset in wn.synsets(word): # may be empty!
                # clean definition - check this
                lst_tup.update({i : (utilities.cleanString(synset.definition), [], [])})
                i += 1
            self.dict.update({word: (synset.pos, lst_tup)})
            list_of_senses = self.dict[word][1]

        #print list_of_senses
        for sense in list_of_senses: # sense is int. length list_of_senses is approx 5
            #print "Senses:\n", sense, list_of_senses[sense]
            overlap = self.computeOverlap(word, pos, list_of_senses[sense], pre_words, post_words)
            #print "overlap for sense", sense, ":", overlap
            #print "!!!!", sense, "Overlap:", overlap
            scores[sense] = overlap+alpha
        #print "Best Sense is: ", best_sense
        if softScoring:
            values = []
            total = sum(scores.values())
            for key in scores:
                scores[key] = scores[key] / float(total)
        return scores, alpha

    # returns the number of words in common between two sets
    # signature = set of words in the gloss and examples of sense
    def computeOverlap(self, target, pos, (defn,examples,wordnetints), pre_words, post_words):
        # relevant words = words with same pos
        context_overlap = 0
        def_overlap = 0
        consecutive_overlap = 0

        def_words = defn.split(' ')
        # put all examples into the definition too. # CHANGE. no.
        for example in examples:
            if example.find(target) != -1:
                lst = example.split(target)
                example = lst[0] + lst[1]
                def_words.extend(example.split(' '))
        # put wordnet int senses into defn
        for wnint in wordnetints:
            wnstring = target + "." + pos + "."
            if wnint < 10: wnstring += "0" + str(wnint)
            else: wnstring += str(wnint)
            try:
                wndef = utilities.cleanString(wn.synset(wnstring).definition)
                def_words.extend(wndef.split(' '))
            except: pass
        #print target
        #print "  pre :", pre_words
        #print "  post:", post_words
        #print "  def :", def_words

        for pre_word in pre_words:
            wco, wo, wcono = self.getOverlaps(def_words, pre_word, pre_words)
            context_overlap += wco
            def_overlap += wo
            consecutive_overlap += wcono
        for post_word in post_words:
            wco, wo, wcono = self.getOverlaps(def_words, post_word, post_words)
            context_overlap += wco
            def_overlap += wo
            consecutive_overlap += wcono

        '''
        # figure out a better metric! use examples?!
        for word in def_words:
            for pre_word in pre_words:
                # here it is with caching
                if defn not in self.overlapCache:
                    self.overlapCache[defn] = dict()
                if word not in self.overlapCache[defn]:
                    self.overlapCache[defn][word] = dict()
                if pre_word not in self.overlapCache[defn][word]:
                    overlapval = self.checkSenseOverlap(word, pre_word, defn)
                    self.overlapCache[defn][word][pre_word] = overlapval
                    overlap += overlapval
                else:
                    overlap += self.overlapCache[defn][word][pre_word]
                # no caching:
                #overlap += self.checkSenseOverlap(word, pre_word, defn)
            for post_word in post_words:
                # here it is with caching
                if defn not in self.overlapCache:
                    self.overlapCache[defn] = dict()
                if word not in self.overlapCache[defn]:
                    self.overlapCache[defn][word] = dict()
                if post_word not in self.overlapCache[defn][word]:
                    overlapval = self.checkSenseOverlap(word, post_word, defn)
                    self.overlapCache[defn][word][post_word] = overlapval
                    overlap += overlapval
                else:
                    overlap += self.overlapCache[defn][word][post_word]
                # no caching:
                #overlap += self.checkSenseOverlap(word, post_word, defn)
        '''
        #print overlap
        #print context_overlap, def_overlap, consecutive_overlap
        total_overlap = 3*context_overlap + 5*def_overlap + 8*consecutive_overlap
        return total_overlap

    def getOverlaps(self, def_words, context_word, listwords):
        context_overlap = 0 # if context_word in def_words
        overlap = 0 # overlap of contextword def words and def_words
        consecOverlap = 0
        if context_word in def_words:
            context_overlap += 1
        if context_word in self.dict:
            (pos, subdict) = self.dict[context_word]
            for sense in subdict:
                (worddef, examples, wnints) = subdict[sense]
                lst = worddef.split(' ')
                consecOverlap += self.consecutiveOverlaps(def_words, lst)
                for wrd in lst:
                    if wrd.strip() in def_words:
                        overlap += 1
        else: # look up in wordnet
            for synset in wn.synsets(context_word):
                defin = utilities.cleanString(synset.definition).split(' ')
                consecOverlap += self.consecutiveOverlaps(def_words, defin)
                for wrd in defin:
                    if wrd.strip() in def_words:
                        overlap += 1
        return context_overlap, overlap, consecOverlap

    # returns the number of consecutive overlaps given two parsed sentences
    # sent1 is string list, sent2 is string list
    def consecutiveOverlaps(self, sent1, sent2):
        sent1 = ' '.join(sent1)
        con_overlap = 0
        for i in range(0, len(sent2)-1):
            consecutive = sent2[i] + ' ' + sent2[i+1]
            #print consecutive
            if sent1.find(consecutive) != -1:
                con_overlap += 1
        return con_overlap

    def printexample(self):
        print 'Example:\n', 'begin :', self.dict['begin']
        #print 'sense: \n', self.dict['begin'][1]
        #for sense in self.dict['begin'][1]:
            #print "Sense:\n", self.dict['begin'][1][sense]

def processTestFile(dwsd, filename, destination, window=5, softScoring=False):
    tobreak = False
    prevword = ""
    with open(destination, 'w') as d:
        f = open(filename)
        d.write("Id,Prediction\n")
        acc = 0.0
        i = 0
        start_time = time.time()
        for line in f:
            lst = line.split('|')

            word_pos = lst[0].strip().split('.')
            word = word_pos[0]
            pos = word_pos[1]
            gloss = lst[2].strip().split('%%')
            context = gloss[0] + gloss[1] + gloss[2]

            # pick up a number of pre- and post- words defined by int window
            pre_words = gloss[0].strip().split(' ')
            pre_words = pre_words[-window:]
            post_words = gloss[2].strip().split(' ')
            post_words = post_words[:window]

            if prevword != word:
                prevword = word
                print "Target: ", word, "at line", i, "of 3918 for test", time.time() - start_time

            #print "Context: ", context
            #print "POS: ", pos

            # algorithm bottleneck is HERE
            scores, alpha = dwsd.Lesk(word, pos, pre_words, post_words,softScoring)
            sense = utilities.argmax(zip(scores.keys(),scores.values()))
            if max(scores.values()) == alpha: # we got no overlap!
                print sense, "original score but no overlap."
                print zip(scores.keys(),scores.values())
                sense = 1 # we should guess this by default.
                #tobreak = True
            trueSense = int(lst[1].strip())
            if softScoring:
                #print scores
                if trueSense in scores:
                    #print scores[trueSense]
                    acc += scores[trueSense]
            else:
                if sense == trueSense:
                    acc += 1
            i += 1
            d.write("" + str(i) + "," + str(sense) + "\n")
            if tobreak:
                break # REMOVE AFTER DONE WITH

        d.close()
    return acc / float(i)

# MAIN
# preprocess dictionary XML:
#   remove one instance of double sense, fix all '"' characters in examples
utilities.fixDoubles(dictionarySource, dictionaryProcessed)

dwsd = DictionaryWSD(dictionaryProcessed)
#dwsd.printexample()
#dwsd.Lesk('begin', 'v', 'begin to attain freedom')
#dwsd.Lesk('pine', 'n', 'pine cone')

#processTestFile(dwsd, 'test_clean1.csv', 'dictionary_test_prediction.csv', window=8)
print processTestFile(dwsd, 'validation_clean.data', 'csvs/test_p_win10-3-5-8-yex-ywi.data', window=10)
#processTestFile(dwsd, 'test_clean1.csv', 'dictionary_test_prediction.csv', window=8)
#print processTestFile(dwsd, 'validation_clean.data', 'blah.data', window=5, softScoring=True)

#10
#nexnwi .32904
#yexnwi .35798
#nexywi .44587
#ywxywi .43301
