#!/usr/bin/python

import re
import nltk # http://www.nltk.org/install.html
            # in python interpreter: nltk.download() to get punkt
import pprint

# Parses king james
# Tried parsing using XML parsers but input doesn't seem to be valid XML
# Returns a string of tokens separated by whitespace
def parseBible():
    f = open('bible_corpus/kjbible.train')
    bible = f.read()
    # Removes XML and psalm/verse numbers
    # then replaces start of string and double new lines with the sentence segmentation marker <s>.
    # finally adds spaces around all punctuation
    bible = re.sub('([.,!?();:])', r' \1 ', \
                re.sub('\n\n|^', '<s> ', \
                    re.sub('(</?(TEXT|DOC)>\n)|([0-9]+:[0-9]+\s)', '', bible)))
    bible = bible.strip()
    return bible

# need to download - punkt
# Parses the Hotel reviews from Amazon
# Format IsTruthful, IsPositive, Text - for now ignoring the truthful and positive values
def parseReviews():
    f = open('HotelReviews/reviews.train')
    # ignores the first line
    f.readline()
    # gets all text from training data
    hotel_reviews = f.read()

    # using Punkt sentence segmentation tool -- http://www.nltk.org/api/nltk.tokenize.html
    sent_tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')

    sents = sent_tokenizer.tokenize(hotel_reviews)
    # write to file
    data = open('raw_reviews.train', 'w')
    for c in sents:
        # adds sentence start and end marker
        data.write(c+'<s> ')
    data.close()

    p = open ('raw_reviews.train')
    edit = p.read()
    # adds spaces around punctuation
    # <r> - denotes start and end of a review
    # removes the truthful & positive values, xml if any, weird punctuation like ... or . . .
    edit = re.sub('([.,!?();:"-&/$])', r' \1 ', \
                        re.sub('\n|^', '<r> <s> ', \
                            re.sub('(</?(TEXT|DOC)>\n)|([0-9]+,[0-9],)|(\.{2,})|((\.+\s){2,})', '', edit)))
    return edit


def saveFiles():
    with open('bible.train','w') as bible:
        with open ('raw_reviews.train', 'w') as edit:
            bible.write(parseBible())
            edit.write(parseReviews())

saveFiles()
