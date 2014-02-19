#!/usr/bin/python

import re
import nltk # http://www.nltk.org/install.html
            # in python interpreter: nltk.download() to get punkt
import pprint

# Parses king james
# Tried parsing using XML parsers but input doesn't seem to be valid XML
# Returns a string of tokens separated by whitespace
def parseBible(fileName):
    f = open(fileName)
    bible = f.read()
    # Removes XML and psalm/verse numbers
    # then replaces start of string and double new lines with the sentence segmentation marker <s>.
    # finally adds spaces around all punctuation
    bible = re.sub('(</?(TEXT|DOC)>\n)', '', bible)
    bible = re.sub('([0-9]+:[0-9]+)',' <s> ', bible)
    bible = re.sub('([.,!?();:"-&/$])', r' \1 ', bible)
    bible = bible.strip()
    return bible

# need to download - punkt
# Parses the Hotel reviews from Amazon
# Format IsTruthful, IsPositive, Text - for now ignoring the truthful and positive values
def parseReviews(fileName):
    f = open(fileName)
    # ignores the first line
    f.readline()
    # gets all text from training data
    hotel_reviews = f.read()

    # using Punkt sentence segmentation tool -- http://www.nltk.org/api/nltk.tokenize.html
    sent_tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')

    sents = sent_tokenizer.tokenize(hotel_reviews)
   
    data = open('raw_reviews.train', 'w')
    for c in sents:
        # adds sentence start and end marker
         # write to file
        data.write(c+'<s> ')
    data.close()

    p = open ('raw_reviews.train')
    edit = p.read()
    # adds spaces around punctuation
    # <r> - denotes start and end of a review
    # removes the truthful & positive values, xml if any, weird punctuation like ... or . . .

    edit = re.sub('(</?(TEXT|DOC)>\n)|([0-9]+,[0-9],)|((\.+\s){2,})', '', edit)
    edit = re.sub('\n|^', ' <s> ', edit)
    edit = re.sub('([,!?();:"-&/$])', r' \1 ', edit)
    edit = re.sub('(\.{1,})',r' \1 ', edit)
    edit = re.sub('--', ' -- ', edit)
    return edit


def saveFiles():
    with open('bible.train','w') as bible:
        bible.write(parseBible('bible_corpus/kjbible.train'))
    with open ('raw_reviews.train', 'w') as edit:
        edit.write(parseReviews('HotelReviews/reviews.train'))
    with open ('raw_reviews.train', 'w') as edit:
        edit.write(parseReviews('HotelReviews/reviews.train'))
    with open ('raw_reviews.test', 'w') as edit:
        edit.write(parseReviews('HotelReviews/reviews.test'))
    with open ('bible.test', 'w') as edit:
        edit.write(parseReviews('bible_corpus/kjbible.test'))


saveFiles()
