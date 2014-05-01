import hmm
from nltk.tag.hmm import * 
import parseReviews

def probdist(values, samples):
	d = {}
	for value, item in zip(values, samples):
		d[item] = value
	return DictionaryProbDist(d)

def parseTraining(filename):
	with open(filename) as f:
		a = parseReviews.getReviewList(filename)
		dic = parseReviews.wordSentimentMapBasic(a)
		return list(dic.keys())


def sentiment_model(filename, n):
	symbols = parseTraining("data/training_data.txt")
	states = ['-1','0','1']
	a = hmm.HMM(filename, n)
	transitions = a.transition_probabilities
	output = a.output_probabilities
	pi = array([0.5, 0.2, 0.3], float64)
	pi = probdist(pi, states)
	model = HiddenMarkovModelTagger(symbols=symbols, states=states, 
		transitions=transitions, output=output, priors = pi)
	return model, states

def runHMM():
	# should be in the form of symbol, tag
	model, states = sentiment_model("data/basic_features_train.txt", 4)
	test = ["I bought this unit hoping to archive my old personal VHS tapes."]
	print model.tag(test)

runHMM()