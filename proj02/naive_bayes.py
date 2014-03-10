import utilities, pprint

class NaiveBayes():
    def __init__(self, trainingSet):
        self.senseCounts = dict()
        self.wordCounts = dict()
        self.featureCounts = dict()
        self.featureList = []
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
        for example in testSet:
            word = example[0]
            features = example[2]
            probs = []
            if word in self.wordCounts:
                wc = self.wordCounts[word]
                for sense in self.senseCounts[word]:
                    sc = self.senseCounts[word][sense]
                    prob = sc / float(wc)
                    for key,value in features.items():
                        if (key,value) in self.featureCounts[(word,sense)]:
                            prob *= (self.featureCounts[(word,sense)][(key,value)] / sc)
                        else:
                            prob *= 0
                    probs.append((sense,prob))
                predictions.append(utilities.argmax(probs))
            else:
                predictions.append(-1)
        return predictions


# pp = pprint.PrettyPrinter(indent=4)
# pp.pprint(utilities.constructSet(windowSize=2,loc="temp.pickle")[:5])
nb = NaiveBayes(utilities.constructSet(windowSize=10))
print nb.classify(utilities.constructSet(source='test_clean.data'))

