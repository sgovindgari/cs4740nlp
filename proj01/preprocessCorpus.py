#!/usr/bin/python

import re
import nltk # http://www.nltk.org/install.html
            # in python interpreter: nltk.download() to get punkt
import pprint
import ngram

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
def parseReviews(fileName, destination):
    f = open(fileName)
    # ignores the first line
    f.readline()
    # gets all text from training data
    hotel_reviews = f.read()

    # using Punkt sentence segmentation tool -- http://www.nltk.org/api/nltk.tokenize.html
    sent_tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')

    sents = sent_tokenizer.tokenize(hotel_reviews)
   
    data = open(destination, 'w')
    for c in sents:
        # adds sentence start and end marker
         # write to file
        data.write(c+'<s> ')
    data.close()

    p = open (destination)
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

def parseForPrediction(filename, destination):
    f = open (filename)
    f.readline()
    predictions = f.read()
    predictions = re.sub('\n|^', '<r> <s> ', predictions)
     # using Punkt sentence segmentation tool -- http://www.nltk.org/api/nltk.tokenize.html
    sent_tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')

    sents = sent_tokenizer.tokenize(predictions)
   
    data = open(destination, 'w')

    for c in sents:
        # adds sentence start and end marker
         # write to file
        data.write(c+'<s> ')
    data.close()

    p = open (destination)
    raw_predict = p.read()
    # adds spaces around punctuation
    # <r> - denotes start and end of a review
    # removes the truthful & positive values, xml if any, weird punctuation like ... or . . .
    raw_predict = re.sub('(</?(TEXT|DOC)>\n)|((\.+\s){2,})', '', raw_predict)
    raw_predict = re.sub('([,!?();:"-&/$])', r' \1 ', raw_predict)
    raw_predict = re.sub('(\.{1,})',r' \1 ', raw_predict)
    raw_predict = re.sub('--', ' -- ', raw_predict)
    return raw_predict

def diffReviews(filename, extension):
    f = open(filename)
    tru = f.read()

    tru_reviews = open('true' + extension, 'w')
    fal_reviews = open('false' + extension, 'w')
    
    # using validation data as well
    true_pos_list = tru.split('<r> <s> ')
    for i in range(1, len(true_pos_list)):
        c = true_pos_list[i]
        # true and positive
        if c[0:8] == '1 , 1 , ':
            tru_reviews.write('<s> ' + c[8:])
        elif c[0:8] == '0 , 0 , ':
            fal_reviews.write('<s> ' + c[8:])
        elif c[0:8] == '0 , 1 , ':
            fal_reviews.write('<s> ' + c[8:])
        elif c[0:8] == '1 , 0 , ':
            tru_reviews.write('<s> ' + c[8:])
    tru_reviews.close()
    fal_reviews.close()

def predictReview():
    with open('predictions.test', 'w') as raw_predict:
        raw_predict.write(parseForPrediction('HotelReviews/reviews.test', 'predictions.test'))
        f = open('predictions.test')
        replace_text = f.read()
        lst = replace_text.split('<r> <s> ')
        result = open('result_pred.test', 'w')
        final_predictions = open('final_predictions.test', 'w')
        for i in range(1, len(lst)):
            c = lst[i].strip()

            if c[0:11] == '?  ,  ?  , ':
                result.write('<s> ' + c[11:])
                tru_uningram = ngram.ngram('true.train', 1)
                tru_bigram = ngram.ngram('true.train', 2)
                fal_unigram = ngram.ngram('true.train', 1)
                fal_bigram = ngram.ngram('false.train', 2)

                tru_uni_pp = tru_uningram.perplexity('result_pred.test')
                fal_uni_pp = fal_unigram.perplexity('result_pred.test')
                tru_bi_pp = tru_bigram.perplexity('result_pred.test')
                fal_bi_pp = fal_bigram.perplexity('result_pred.test')

                smallest_num = min(tru_bi_pp, tru_uni_pp, fal_bi_pp, fal_uni_pp)
                if smallest_num == tru_uni_pp or smallest_num == tru_bi_pp:
                    final_predictions.write('<s> 1 , ? , ' + c[11:])
                else:
                    final_predictions.write('<s> 0 , ? , ' + c[11:])
        final_predictions.close()


def saveFiles():
    with open('bible.train','w') as bible:
        bible.write(parseBible('bible_corpus/kjbible.train'))
    with open ('raw_reviews.train', 'w') as edit:
        edit.write(parseReviews('HotelReviews/reviews.train', 'raw_reviews.train'))
    with open ('raw_reviews.test', 'w') as edit:
        edit.write(parseReviews('HotelReviews/reviews.test', 'raw_reviews.test'))
    with open ('bible.test', 'w') as edit:
        edit.write(parseBible('bible_corpus/kjbible.test'))
    with open ('parsed_predictions.train', 'w') as raw_predict:
        raw_predict.write(parseForPrediction('HotelReviews/reviews.train', 'parsed_predictions.train'))


saveFiles()
diffReviews('parsed_predictions.train', '.train')
predictReview()
