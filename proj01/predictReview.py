#!/usr/bin/python

import re
import nltk
import pprint
import preprocessCorpus
import ngram
import time

def parseForPrediction(filename, destination):
    f = open (filename)
    f.readline()
    predictions = f.read()
    predictions = re.sub('\n|^', '\n <r> <s> ', predictions)
    f.close()
     # using Punkt sentence segmentation tool -- http://www.nltk.org/api/nltk.tokenize.html
    sent_tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')

    sents = sent_tokenizer.tokenize(predictions)
   
    with open(destination, 'w') as data:
        for c in sents:
            # adds sentence start and end marker
             # write to file
            data.write(c+' <s> ')
    raw_predict = None
    with open (destination) as p:
        raw_predict = p.read()
        # adds spaces around punctuation
        # <r> - denotes start and end of a review
        # removes the truthful & positive values, xml if any, weird punctuation like ... or . . .
        raw_predict = re.sub('(</?(TEXT|DOC)>\n)|((\.+\s){2,})', '', raw_predict)
        raw_predict = re.sub('([,!?();:"-&/$])', r' \1 ', raw_predict)
        raw_predict = re.sub('(\.{1,})',r' \1 ', raw_predict)
        raw_predict = re.sub('--', ' -- ', raw_predict)
    with open(destination, 'w') as write:
        write.write(raw_predict)

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
    parseForPrediction('HotelReviews/reviews.test', 'predictions.test')
    replace_text = None
    with open('predictions.test') as f:
        replace_text = f.read()
    lst = replace_text.split('<r> <s> ')
    final_predictions = open('final_predictions.test', 'w')

    tru_unigram = ngram.ngram('true.train', 1, ngram.Smooth.GOOD_TURING, True)
    fal_unigram = ngram.ngram('false.train', 1, ngram.Smooth.GOOD_TURING, True)
    tru_bigram = ngram.ngram('true.train', 3, ngram.Smooth.GOOD_TURING, True)       
    fal_bigram = ngram.ngram('false.train', 3, ngram.Smooth.GOOD_TURING, True)
    start = time.time()
    for i in range(1, len(lst)):
        c = lst[i].strip()
        if c[0:11] == '?  ,  ?  , ':
            with open('result_pred.test', 'w') as result:
                result.write('<s> ' + c[11:])
            result.close()
            start = time.time()
            tru_uni_pp = tru_unigram.perplexity('result_pred.test')
            fal_uni_pp = fal_unigram.perplexity('result_pred.test')
            tru_bi_pp = tru_bigram.perplexity('result_pred.test')
            fal_bi_pp = fal_bigram.perplexity('result_pred.test')
            print time.time() - start
            smallest_num = min(tru_bi_pp, tru_uni_pp, fal_bi_pp, fal_uni_pp)
            if smallest_num == tru_uni_pp or smallest_num == tru_bi_pp:
                final_predictions.write('<s> 1 , ? , ' + c[11:] + "\n")
            else:
                final_predictions.write('<s> 0 , ? , ' + c[11:] + "\n")
    final_predictions.close()
    print str(time.time() - start)

def saveFiles():
    preprocessCorpus.saveFiles()
    parseForPrediction('HotelReviews/reviews.train', 'parsed_predictions.train')

saveFiles()
diffReviews('parsed_predictions.train', '.train')
predictReview()
