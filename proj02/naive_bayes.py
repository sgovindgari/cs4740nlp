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
                    if (key,value) in self.featureCounts[(word,sense)]:
                        self.featureCounts[(word,sense)][(key,value)] += 1
                    else:
                        self.featureCounts[(word,sense)][(key,value)] = 1
                else:
                    self.featureCounts[(word,sense)] = dict()
                    self.featureCounts[(word,sense)][(key,value)] = 1

    def classify(self, testSet):
        predictions = []

        #Fetch necessary features
        #TODO: This is complete but it struggles with the fact that it doesn't go over all features and also what if a featureCount is zero!?
        #TODO: Feature counts don't hold counts for all features...
        #TODO: Smooth - using add 1 for now I guess
        #TODO: HALP
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
                    prob = math.log(sc) - math.log(wc)
                    for key in self.featureLists[word]:
                        prob -= math.log(sc+1)
                        if key in features:
                            value = features[key]
                            if (key,value) in self.featureCounts[(word,sense)]:
                                prob += math.log(self.featureCounts[(word,sense)][(key,value)] + 1)
                        #Punishes training data for having words that DONT appear in the test example
                        else:
                            #using 1 only works for boolean
                            if (key,1) in self.featureCounts[(word,sense)]:
                                prob += math.log(sc - self.featureCounts[(word,sense)][(key,1)] + 1)
                            else:
                                prob += math.log(sc+1)
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
nb = NaiveBayes(utilities.constructSet(windowSize=2))
print nb.classify(utilities.constructSet(source='validation_clean.data',windowSize=2))

