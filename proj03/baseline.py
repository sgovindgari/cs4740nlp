import parseReviews, math, itertools, operator


#Baseline model
class Baseline():

    def __init__(self, source, alpha = 1):
        self.alpha = alpha
        self.word_counts = dict()
        self.sentiment_counts = {1 : 0, 0 : 0, -1 : 0}
        self.parse_training(source)
        self.generate_probabilities()
        self.generate_sentiment_probabilities()

    def parse_training(self, source):
        data = parseReviews.getReviewList(source, defaultToZero = False)
        for review in data:
            for entry in review[1]:
                self.update_counts(entry)

    def update_counts(self, entry):
        sentiment = entry[0]
        self.sentiment_counts[sentiment] += 1
        words = entry[1].split(' ')
        for word in words:
            if word in self.word_counts:
                self.word_counts[word][sentiment] += 1
            else:
                self.word_counts[word] = dict()
                self.word_counts[word][0] = self.alpha
                self.word_counts[word][1] = self.alpha
                self.word_counts[word][-1] = self.alpha
                self.word_counts[word][sentiment] += 1

    def generate_probabilities(self):
        self.word_probabilities = dict()
        for word in self.word_counts:
            total = float(sum(self.word_counts[word].values()))
            self.word_probabilities[word] = dict()
            for sentiment in self.sentiment_counts:
                self.word_probabilities[word][sentiment] = self.word_counts[word][sentiment] / total


    def generate_sentiment_probabilities(self):
        self.sentiment_probabilities = dict()
        total = float(sum(self.sentiment_counts.values()))
        for sentiment in self.sentiment_counts:
            self.sentiment_probabilities[sentiment] = self.sentiment_counts[sentiment] / total

    def classify(self, source, kaggle = False):
        data = parseReviews.getReviewList(source, defaultToZero = False)
        predictions = []
        for review in data:
            tags = []
            for entry in review[1]:
                probs = dict()
                for sentiment in self.sentiment_probabilities:
                    probs[sentiment] = math.log(self.sentiment_probabilities[sentiment])
                for word in entry[1]:
                    if word in self.word_probabilities:
                        for p in self.word_probabilities[word]:
                            probs[p] += math.log(self.word_probabilities[word][p])
                print probs
                print max(probs.iteritems(), key=operator.itemgetter(1))
                tags.append(max(probs.iteritems(), key=operator.itemgetter(1))[0])
            # print tags
            predictions.append(tags)
        if kaggle:
            with open('kaggle_baseline','w') as f:
                for seq in predictions:
                    for tag in seq:
                        f.write(str(tag) + '\n')
        return predictions



b = Baseline('data/training_data.txt', alpha = 0.1)
b.classify('data/test_data_no_true_labels.txt')