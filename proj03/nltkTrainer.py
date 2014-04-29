from nltk.probability import ELEProbDist, FreqDist
from nltk import NaiveBayesClassifier
from collections import defaultdict
import parseReviews
 
# Baseline 
# This module uses ELEProbability distribution for each label with NaiveBayesClassifer

train_samples = {
    'I hate you and you are a bad person': 'neg',
    'I love you and you are a good person': 'pos',
    'I fail at everything and I want to kill people' : 'neg',
    'I win at everything and I want to love people' : 'pos',
    'sad are things are heppening. fml' : 'neg',
    'good are things are heppening. gbu' : 'pos',
    'I am so poor' : 'neg',
    'I am so rich' : 'pos',
    'I hate you mommy ! You are my terrible person' : 'neg',
    'I love you mommy ! You are my amazing person' : 'pos',
    'I want to kill butterflies since they make me sad' : 'neg',
    'I want to chase butterflies since they make me happy' : 'pos',
    'I want to hurt bunnies' : 'neg',
    'I want to hug bunnies' : 'pos',
    'You make me frown' : 'neg',
    'You make me smile' : 'pos',
}
 
test_samples = [
  'You are a terrible person and everything you do is bad',
  'I love you all and you make me happy',
  'I frown whenever I see you in a poor state of mind',
  'Finally getting rich from my ideas. They make me smile.',
  'My mommy is poor',
  'I love butterflies. Yay for happy',
  'Everything is fail today and I hate stuff',
]
 
#Feature extractor - returns a dictionary that will tell us if any of our words
#in the input of the feature extractor are found in the word list
def gen_bow(text):
    words = text.split()
    bow = {}
    for word in words:
        bow[word.lower()] = True
    return bow
 
 #unigram model
def get_labeled_features(samples):
    word_freqs = {}
    for text, label in samples.items():
        tokens = text.split()
        for token in tokens:
            if token not in word_freqs:
                word_freqs[token] = {'pos': 0, 'neg': 0, 'neu':0}
            word_freqs[token][label] += 1
    return word_freqs
 
def get_label_probdist(labeled_features):
    label_fd = FreqDist()
    for item,counts in labeled_features.items():
        for label in ['neg','pos', 'neu']:
            if counts[label] > 0:
                label_fd.inc(label)
    label_probdist = ELEProbDist(label_fd)
    return label_probdist
 
#Getting frequencies of words 
def get_feature_probdist(labeled_features, samples):
    feature_freqdist = defaultdict(FreqDist)
    feature_values = defaultdict(set)
    num_samples = len(samples) / 2
    for token, counts in labeled_features.items():
        for label in ['neg','pos','neu']:
            feature_freqdist[label, token].inc(True, count=counts[label])
            feature_freqdist[label, token].inc(None, num_samples - counts[label])
            feature_values[token].add(None)
            feature_values[token].add(True)
    #for item in feature_freqdist.items():
        #print item[0],item[1]
    feature_probdist = {}
    for ((label, fname), freqdist) in feature_freqdist.items():
        probdist = ELEProbDist(freqdist, bins=len(feature_values[fname]))
        feature_probdist[label,fname] = probdist
    return feature_probdist
 
def ToSentiment(num):
    if num == 1:
        return "pos"
    elif num == 0:
        return "neu"
    elif num == -1:
        return "neg"

def get_train_data(filename, destination):
    #with open(destination, 'w') as d:
    with open(filename) as f:
        result = dict()
        lst = parseReviews.getReviewList(filename)
        for i in lst:
            linelst = i[1]
            for j in linelst:
                result[j[1].strip()] = ToSentiment(j[0])
                    #d.write(j[1].strip() + " : " + ToSentiment(j[0]) + "\n")
            #d.close()
        return result

def get_test_data(filename, destination):
    with open(destination, 'w') as d:
        with open(filename) as f:
            result = []
            lst = parseReviews.getReviewList(filename)
            for i in lst:
                linelst = i[1]
                for j in linelst:
                    result.append(j[1].strip())
            d.write("Id,answer"+"\n")
            i = 0
            for sample in result:
                d.write(str(i) +"," + str(parseReviews.strToSentiment(classifier.classify(gen_bow(sample)))) + "\n")
                i = i +1
            d.close()
            return result

d = get_train_data("data/training_data.txt", "data/nltkTrainer_train.txt")

labeled_features = get_labeled_features(d)
 
label_probdist = get_label_probdist(labeled_features)
 
feature_probdist = get_feature_probdist(labeled_features, d)
 
classifier = NaiveBayesClassifier(label_probdist, feature_probdist)

test_data = get_test_data("data/test_data_no_true_labels.txt", "data/nltkTrainer_test.txt")
 
for sample in test_samples:
    print "%s | %s" % (sample, classifier.classify(gen_bow(sample)))
 
classifier.show_most_informative_features(n=30)