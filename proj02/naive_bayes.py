#!/usr/bin/env python

import utilities, pprint,math

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
                    self.featureLists[word] = dict()
                self.featureLists[word][key] = key
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

    def classify(self, testSet):
        predictions = []

        #TODO: Smooth - using add 1 for now I guess
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
                        prob /= (sc+1)
                        #feature appears in test example
                        if key in features:
                            value = features[key]
                            if key in self.featureCounts[(word,sense)] and value in self.featureCounts[(word,sense)][key]:
                                prob *= (self.featureCounts[(word,sense)][key][value] + 1)
                        #Punishes training data for having features that DONT appear in the test example
                        else:
                            if key in self.featureCounts[(word,sense)]:
                                prob *= (sc-sum(self.featureCounts[(word,sense)][key].values())+1)
                            else:
                                prob *= (sc+1)
                    probs.append((sense,prob))
                res = utilities.argmax(probs)
                correct = correct if res != example[1] else correct+1
                predictions.append(res)
            else:
                predictions.append(-1)
        print correct/float(len(predictions))
        return predictions


# pp = pprint.PrettyPrinter(indent=4)
# pp.pprint(utilities.constructSet(windowSize=2,loc="temp.pickle")[:5])
nb = NaiveBayes(utilities.constructSet(windowSize=0, source='training_clean.data'))
print nb.classify(utilities.constructSet(source='validation_clean.data',windowSize=0))

