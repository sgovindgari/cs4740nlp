#!/usr/bin/python

import re
import nltk
import pprint
import preprocessCorpus
import ngram
import time
import gc

def parseForPrediction(filename, destination):
    f = open (filename)
    f.readline()
    predictions = f.read()
    predictions = re.sub('\n|^|\n\n', '\n <r> <s> ', predictions)
    f.close()
     # using Punkt sentence segmentation tool -- http://www.nltk.org/api/nltk.tokenize.html
    sent_tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')

    sents = sent_tokenizer.tokenize(predictions)
   
    with open(destination, 'w') as data:
        for c in sents:
            # adds sentence start and end marker
             # write to file
            data.write(c+ '<s> ')
    raw_predict = None
    with open (destination) as p:
        raw_predict = p.read()
        # adds spaces around punctuation
        # <r> - denotes start and end of a review
        # removes the truthful & positive values, xml if any, weird punctuation like ... or . . .
        raw_predict = re.sub('(</?(TEXT|DOC)>\n)|((\.+\s){2,})', '', raw_predict)
        raw_predict = re.sub('(,+[0-9]+,)', ' ', raw_predict);
        raw_predict = re.sub('([,?();:"-&/$])', r' \1 ', raw_predict)
        raw_predict = re.sub('(\.{1,}|\!{1,})',r' \1 ', raw_predict)
        raw_predict = re.sub('--', ' -- ', raw_predict)
    with open(destination, 'w') as write:
        write.write(raw_predict)

def diffReviews(filename):
    f = open(filename)
    
    tru = f.read()
    
    tru_reviews = open('true.train', 'w')
    fal_reviews = open('false.train', 'w')
    
    true_pos_list = tru.split('<r> ')

    for i in range(1, len(true_pos_list)):
        c = true_pos_list[i].strip()
        # true and positive
        if c[4] == '1':
            tru_reviews.write(c[0:3] + c[5: len(c)-3])
        elif c[4] == '0':
            fal_reviews.write(c[0:3] + c[5: len(c)-3])

    # write the sentence end marker at very end
    tru_reviews.write('<s>')
    fal_reviews.write('<s>')

    tru_reviews.close()
    fal_reviews.close()

def getModels():
    tru_unigram = ngram.ngram('true.train', 1, ngram.Smooth.GOOD_TURING, True)
    fal_unigram = ngram.ngram('false.train', 1, ngram.Smooth.GOOD_TURING, True)
    
    tru_uni_rl = ngram.ngram('true.train', 1, ngram.Smooth.GOOD_TURING, True, ngram.Direction.RL)
    fal_uni_rl = ngram.ngram('false.train', 1, ngram.Smooth.GOOD_TURING, True, ngram.Direction.RL)

    tru_bigram = ngram.ngram('true.train', 2, ngram.Smooth.GOOD_TURING, True)       
    fal_bigram = ngram.ngram('false.train', 2, ngram.Smooth.GOOD_TURING, True)

    tru_bi_rl = ngram.ngram('true.train', 2, ngram.Smooth.GOOD_TURING, True, ngram.Direction.RL)
    fal_bi_rl = ngram.ngram('false.train', 2, ngram.Smooth.GOOD_TURING, True, ngram.Direction.RL)

    #trial code
    tru_trigram = ngram.ngram('true.train', 3, ngram.Smooth.GOOD_TURING, True)
    fal_trigram = ngram.ngram('false.train', 3, ngram.Smooth.GOOD_TURING, True)

    tru_tri_rl = ngram.ngram('true.train', 3, ngram.Smooth.GOOD_TURING, True, ngram.Direction.RL)
    fal_tri_rl = ngram.ngram('false.train', 3, ngram.Smooth.GOOD_TURING, True, ngram.Direction.RL)

    tru_quadgram = ngram.ngram('true.train', 4, ngram.Smooth.GOOD_TURING, True)
    fal_quadgram = ngram.ngram('false.train', 4, ngram.Smooth.GOOD_TURING, True)

    return [tru_unigram, fal_unigram, tru_bigram, fal_bigram, tru_trigram, fal_trigram, tru_quadgram, fal_quadgram
    , tru_uni_rl, fal_uni_rl, tru_bi_rl, fal_bi_rl, tru_tri_rl, fal_tri_rl]

def predictReview(models, end_index, match_pattern, source, final_destination, kaggle):
    replace_text = None
    with open(source) as f:
        replace_text = f.read()
    lst = replace_text.split('<r> <s> ')
    final_predictions = open(final_destination, 'w')
    if (kaggle):
        final_predictions.write("Id,Label\n")
    # start = time.time()

    for i in range(1, len(lst)):
        c = lst[i].strip()

        if c[0:end_index] == match_pattern:
            with open('result_pred.test', 'w') as result:
                result.write('<s> ' + c[end_index:])
            result.close()
            #start = time.time()
            print i
            tru_uni_pp = models[0].perplexity('result_pred.test')
            fal_uni_pp = models[1].perplexity('result_pred.test')
            tru_bi_pp = models[2].perplexity('result_pred.test')
            fal_bi_pp = models[3].perplexity('result_pred.test')
            tru_tri_pp = models[4].perplexity('result_pred.test')
            fal_tri_pp = models[5].perplexity('result_pred.test')
            tru_quad_pp = models[6].perplexity('result_pred.test')
            fal_quad_pp = models[7].perplexity('result_pred.test')
            tru_uni_rl_pp = models[8].perplexity('result_pred.test')
            fal_uni_rl_pp = models[9].perplexity('result_pred.test')
            tru_bi_rl_pp = models[10].perplexity('result_pred.test')
            fal_bi_rl_pp = models[11].perplexity('result_pred.test')
            tru_tri_rl_pp = models[12].perplexity('result_pred.test')
            fal_tri_rl_pp = models[13].perplexity('result_pred.test')
            gc.collect()

            #print time.time() - start
            smallest_num = min(tru_bi_pp, tru_uni_pp, fal_bi_pp, fal_uni_pp, tru_quad_pp, fal_quad_pp,
                tru_uni_rl_pp, tru_bi_rl_pp, tru_tri_rl_pp, fal_tri_rl_pp, fal_uni_rl_pp, fal_bi_rl_pp, tru_tri_pp, fal_tri_pp)
            if smallest_num == tru_uni_pp or smallest_num == tru_bi_pp or smallest_num == tru_uni_rl_pp or smallest_num == tru_tri_pp or smallest_num == tru_bi_rl_pp or smallest_num == tru_tri_rl_pp or smallest_num == tru_quad_pp:
                if (kaggle):
                    final_predictions.write(str(i-1)+ ',1' + "\n")
                else:
                    final_predictions.write('<s> 1 , ' + c[end_index:] + "\n")
            else:
                if (kaggle):
                    final_predictions.write(str(i-1) + ',0' + "\n")
                else:
                    final_predictions.write('<s> 0 , ' + c[end_index:] + "\n")
    final_predictions.close()
   # print str(time.time() - start)

def saveFiles():
    preprocessCorpus.saveFiles()
    parseForPrediction('HotelReviews/reviews.train', 'parsed_predictions.train')
    #parseForPrediction('HotelReviews/reviews.valid', 'parsed_predictions.valid')
    parseForPrediction('HotelReviews/reviews.test', 'parsed_predictions.test')
    parseForPrediction('Kaggle_test.txt', 'parsed_kaggle.txt')

'''
gc.enable()
start = time.time()
saveFiles()
print time.time() - start
diffReviews('parsed_predictions.train')
print time.time() - start
lst_models = getModels()
print time.time() - start
gc.collect()
#predictReview(lst_models, 11, '?  ,  ?  , ', 'parsed_predictions.test', 'final_predictions.test', False)
predictReview(lst_models, 5, '?  , ', 'parsed_kaggle.txt', 'kaggle_predictions.txt', True)
'''