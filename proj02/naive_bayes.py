#!/usr/bin/env python

import utilities, pprint, math, pickle

class NaiveBayes():
    def __init__(self, trainingSet):
        self.senseCounts = dict()
        self.wordCounts = dict()
        self.featureCounts = dict()
        self.featureLists = dict()
        #Generating necessary counts
        for example in trainingSet:
            word = example[0]
            sense = example[1]
            features = example[2]
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

    def classify(self, testSet, softscore=False,alpha=1):
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
                    prob = sc/float(wc)
                    # Only go through the features we have from training, ignore features that arise in test example
                    # that don't appear in any training example as they will all have the same effect (sort of) on the probability
                    for key in self.featureLists[word]:
                        #feature is non-null/0 in this example 
                        if key in features:
                            value = features[key]
                            #Does this sense of the word have this feature as non-null/0
                            if key in self.featureCounts[(word,sense)]:
                                #Are there any of the value in this test example in our training examples
                                if value in self.featureCounts[(word,sense)][key]:
                                    prob *= ((self.featureCounts[(word,sense)][key][value] + alpha) / float(sc+alpha*len(self.featureLists[word])))
                                #if not, use add one smoothing to avoid zero probability
                                else:
                                    prob *= (alpha/(sc+alpha*len(self.featureLists[word])))
                            #If it doesn't then using add 1 smoothing compute probability
                            else:
                                prob *= (alpha/(sc+alpha*len(self.featureLists[word])))
                        # feature is 0/null in example
                        else:
                            #if the feature has non-null/0 value in any of our test example
                            if key in self.featureCounts[(word,sense)]:
                                prob *= ((sc-sum(self.featureCounts[(word,sense)][key].values())+alpha) / float(sc+alpha*len(self.featureLists[word])))
                            #The feature is null for all train examples
                            else:
                                prob *= 1.0
                    probs.append((sense,prob))
                if (softscore):
                	# separate out the senses and the probabilities into 2 lists
                	senses = list(zip(*probs)[0])
                	prob_numbers = list(zip(*probs)[1])

                	# normalize probabilities
                	prob_sum = sum(prob_numbers)
                	prob_numbers = [x/float(prob_sum) for x in prob_numbers]

                	probs = zip(senses, prob_numbers)
                res = utilities.argmax(probs)
                correct = correct if res != example[1] else correct+1
                predictions.append(res)
            else:
                predictions.append(-1)
        print correct/float(len(predictions))
        return predictions


pp = pprint.PrettyPrinter(indent=4)
nb = NaiveBayes(utilities.constructSet(source='training_stop.data',windowSize=-1))
print nb.classify(utilities.constructSet(source='validation_stop.data',windowSize=-1),alpha=1)
