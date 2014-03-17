#!/usr/bin/env python

import utilities, pprint, math, pickle, time, numpy

class NaiveBayes():
    def __init__(self, trainingSet, maxExamples=-1):
        self.senseCounts = dict()
        self.wordCounts = dict()
        self.featureCounts = dict()
        self.featureLists = dict()
        #Generating necessary counts
        for example in trainingSet:
            word = example[0]
            sense = example[1]
            features = example[2]

            if (maxExamples == -1) or (word not in self.wordCounts) or (sense not in self.senseCounts[word]) or (maxExamples != -1 and maxExamples > self.senseCounts[word][sense]):
                if word in self.wordCounts:
                    self.wordCounts[word] += 1
                else:
                    self.wordCounts[word] = 1
                if word in self.senseCounts:
                    if sense in self.senseCounts[word]:
                        self.senseCounts[word][sense] += 1
                    else:
                        self.senseCounts[word][sense] = 1
                else:
                    self.senseCounts[word] = dict()
                    self.senseCounts[word][sense] = 1
                for key,value in features.items():
                    if word not in self.featureLists:
                        self.featureLists[word] = set()
                    self.featureLists[word].add(key)
                    if (word, sense) in self.featureCounts:
                        if key in self.featureCounts[(word,sense)]:
                            if value in self.featureCounts[(word,sense)][key]:
                                self.featureCounts[(word,sense)][key][value] += 1
                            else:
                                self.featureCounts[(word,sense)][key][value] = 1
                        else:
                            self.featureCounts[(word,sense)][key] = dict()
                            self.featureCounts[(word,sense)][key][value] = 1
                    else:
                        self.featureCounts[(word,sense)] = dict()
                        self.featureCounts[(word,sense)][key] = dict()
                        self.featureCounts[(word,sense)][key][value] = 1
        # print utilities.argmax(self.wordCounts.items())
        # print self.wordCounts['share']
        # print numpy.median(self.wordCounts.values())

    def classify(self,testSet,alpha=1,softscore=False,kaggle=False,biasTowardsCommon=True):
        predictions = []

        actual = []
        correct = 0
        for example in testSet:
            word = example[0]
            actual.append(example[1])
            features = example[2]
            probs = []
            if word in self.wordCounts:
                wc = self.wordCounts[word]
                for sense in self.senseCounts[word]:
                    sc = self.senseCounts[word][sense]
                    prob = 0.0
                    if biasTowardsCommon:
                        prob = math.log(sc/float(wc))
                    # Only go through the features we have from training, ignore features that arise in test example
                    # that don't appear in any training example as they will all have the same effect (sort of) on the probability
                    if word in self.featureLists:
                        for key in self.featureLists[word]:
                            #feature is non-null/0 in this example 
                            fp = 0.0
                            if key in features:
                                value = features[key]
                                #Does this sense of the word have this feature as non-null/0
                                if key in self.featureCounts[(word,sense)]:
                                    #Are there any of the value in this test example in our training examples
                                    if value in self.featureCounts[(word,sense)][key]:
                                        fp = math.log((self.featureCounts[(word,sense)][key][value] + alpha) / float(sc+alpha*len(self.featureLists[word])))
                                    #if not, use add one smoothing to avoid zero probability
                                    else:
                                        fp = math.log(alpha/float(sc+alpha*len(self.featureLists[word])))
                                #If it doesn't then using add 1 smoothing compute probability
                                else:
                                    fp = math.log(alpha/float(sc+alpha*len(self.featureLists[word])))
                            # feature is 0/null in example
                            else:
                                #if the feature has non-null/0 value in any of our test example
                                if key in self.featureCounts[(word,sense)]:
                                    fp = math.log((sc-sum(self.featureCounts[(word,sense)][key].values())+alpha) / float(sc+alpha*len(self.featureLists[word])))
                                #The feature is null for all train examples
                                else:
                                    fp = math.log((sc + alpha) / float(sc+alpha*len(self.featureLists[word])))
                            #print key + ": " + str(fp)
                            prob += fp
                    probs.append((sense,prob))
                res = None
                if softscore:
                # separate out the senses and the probabilities into 2 lists
                    senses = list(zip(*probs)[0])
                    prob_numbers = list(zip(*probs)[1])
                    #Adjust probabilities by maximum log to avoid underflow if possible when normalizing. 
                    m_log = max(prob_numbers)
                    prob_numbers = [math.e**(x-m_log) for x in prob_numbers]
                    # normalize probabilities
                    prob_sum = sum(prob_numbers)
                    prob_numbers = [x/prob_sum for x in prob_numbers]
                    probs = zip(senses, prob_numbers)
                    res = utilities.argmax(probs)
                    probs = dict(probs)
                    if example[1] in probs:
                        correct += probs[example[1]]
                else:
                    res = utilities.argmax(probs)
                    correct = correct if res != example[1] else correct+1
                predictions.append(res)
            else:
                predictions.append(-1)
        accuracy = correct/float(len(predictions))
        if kaggle:
            with open('kaggle_results','w') as f:
                for prediction in predictions:
                    f.write(str(prediction) + "\n")

        return (accuracy,zip(actual,predictions))


# pp = pprint.PrettyPrinter(indent=4)
# #print nb.featureLists
#max before/after = 120


#Every word has the same pos! This feature is useless! :(
def testPos():
    with open('pos.csv','w') as f:
        nb = NaiveBayes(utilities.constructSet(source='training_clean.data',windowSize=0,useCooccurrence=False,useColocation=False,usePos=True))
        res = nb.classify(utilities.constructSet(source='validation_clean.data',windowSize=0,useCooccurrence=False,useColocation=False,usePos=True),biasTowardsCommon=False)
        f.write(str(res[0]))

def testCoOccurrence(maxSize=120,stepSize=1):
    with open('coo.csv','a') as f:
        for i in range(1,maxSize+1,stepSize):
            start = time.time()
            nb = NaiveBayes(utilities.constructSet(source='training_clean.data',windowSize=i,useCooccurrence=True,useColocation=False,usePos=False))
            res = nb.classify(utilities.constructSet(source='validation_clean.data',windowSize=i,useCooccurrence=True,useColocation=False,usePos=False),biasTowardsCommon=False)
            f.write(str(i) + "," + str(res[0]) + "\n")
            f.flush()
            print str(i) + ": " + str(time.time()-start)

def testCoLocation(minSize=1,maxSize=83,stepSize=1):
    with open('col.csv','a') as f:
        for i in range(minSize,maxSize+1,stepSize):
            start = time.time()
            nb = NaiveBayes(utilities.constructSet(source='training_clean.data',windowSize=i,useCooccurrence=False,useColocation=True,usePos=False))
            res = nb.classify(utilities.constructSet(source='validation_clean.data',windowSize=i,useCooccurrence=False,useColocation=True,usePos=False),biasTowardsCommon=False)
            f.write(str(i) + "," + str(res[0]) + "\n")
            f.flush()
            print res[0]
            print str(i) + ": " + str(time.time()-start)

def testTrainingSize(minExamples=1,maxExamples=2536,stepSize=1,destination='trainsize.csv'):
    with open(destination,'a') as f:
        for i in range(minExamples,maxExamples+1,stepSize):
            start = time.time()
            nb = NaiveBayes(utilities.constructSet(source='training_clean.data',windowSize=10,useCooccurrence=True,useColocation=False,usePos=False),maxExamples=i)
            res = nb.classify(utilities.constructSet(source='validation_clean.data',windowSize=10,useCooccurrence=True,useColocation=False,usePos=False),biasTowardsCommon=True,softscore=True)
            f.write(str(i) + "," + str(res[0]) + "\n")
            f.flush()
            print res[0]
            print str(i) + ": " + str(time.time()-start)

def softScoring(minSize=1, maxSize=120, stepSize=1):
    with open('soft-score-comp.csv','a') as f:
        for i in range(minSize, maxSize+1, stepSize):
            start = time.time()
            nb_coo = NaiveBayes(utilities.constructSet(source='training_clean.data', windowSize=i, useCooccurrence=True, useColocation=False, usePos=False))
            res_coo = nb_coo.classify(utilities.constructSet(source='validation_clean.data', windowSize=i, useCooccurrence=True, useColocation=False, usePos=False), softscore=True, biasTowardsCommon=False)
            nb_col = NaiveBayes(utilities.constructSet(source='training_clean.data', windowSize=i, useCooccurrence=False, useColocation=True, usePos=False))
            res_col = nb_col.classify(utilities.constructSet(source='validation_clean.data', windowSize=i, useCooccurrence=False, useColocation=True, usePos=False), softscore=True, biasTowardsCommon=False)
            nb_both = NaiveBayes(utilities.constructSet(source='training_clean.data', windowSize=i, useCooccurrence=True, useColocation=True, usePos=False))
            res_both = nb_both.classify(utilities.constructSet(source='validation_clean.data', windowSize=i, useCooccurrence=True, useColocation=True, usePos=False), softscore=True, biasTowardsCommon=False)
            f.write(str(i) + "," + str(res_coo[0]) + "," + str(res_col[0]) + "," + str(res_both[0]) + "\n")
            f.flush()
            print str(i) + ": " + str(time.time()-start)

#testTrainingSize(2550,2550,1)
#softScoring(1, 10, 1)
softScoring(1, 10, 1)
# testTrainingSize(1,150,5,'trainsize_soft.csv')

