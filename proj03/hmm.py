#TODO: Smoothing
import itertools, pprint, operator, math
from copy import copy


class HMM():
    def __init__(self, source, n, alpha = 1, beta = 1):
        # source is a file  where each document is separated by a new line and each line is a feature vector and label
        self.n = n
        self.alpha = alpha
        self.beta = beta
        self.training_data = self.parse_file(source)
        self.construct_model()

    #Takes the source and parses it into a list of lists
    def parse_file(self, source):
        content = ''
        with open(source) as f:
            content = f.read()
        docs = content.split('\n\n')
        doc_list = []
        for doc in docs:
            sentences = doc.split('\n')
            sentence_list = []
            for i in range(1,len(sentences)):
                res = sentences[i].split(' ')
                vector = []
                for attr in range(1,len(res)):
                    vector.append(tuple(res[attr].split(':')))
                sentence_list.append((int(res[0]),vector))
            doc_list.append(sentence_list)
        return doc_list

    def construct_model(self):
        #Generate Counts
        self.output_counts = dict()
        self.transition_counts = dict()
        self.states = set(['0','1','-1','start'])
        self.states.add('start')

        for doc in self.training_data:
            prev = ['start']
            for sentence in doc:
                state = str(sentence[0])
                vector = sentence[1]
                sentence_key = tuple(vector)
                prev_key = tuple(prev)
                for state2 in self.states:
                    if state2 in self.output_counts:
                        if sentence_key in self.output_counts[state]:
                            pass
                        else:
                            self.output_counts[state2][sentence_key] = self.alpha ##add 1 smoothing
                    else:
                        self.output_counts[state2] = dict()
                        self.output_counts[state2][sentence_key] = self.alpha ##add 1 smoothing
                    if prev_key in self.transition_counts:
                        if state2 in self.transition_counts[prev_key]:
                            pass
                        else:
                            self.transition_counts[prev_key][state2] = self.beta
                    else:
                        self.transition_counts[prev_key] = dict()
                        self.transition_counts[prev_key][state2] = self.beta
                    if state2 == state:
                        self.output_counts[state][sentence_key] += 1
                        self.transition_counts[prev_key][state] += 1
                self.states.add(state)
                prev.append(str(sentence[0]))
                if len(prev) >= self.n:
                    prev.pop(0)
        for state in self.states:
            if state != 'start':
                self.output_counts[state]['<unk>'] = self.alpha
        #Generate probabilities
        self.output_probabilities = dict()
        self.transition_probabilities = dict()

        for row_key in self.output_counts:
            self.output_probabilities[row_key] = self.probability_from_row(self.output_counts[row_key])
        for row_key in self.transition_counts:
            self.transition_probabilities[row_key] = self.probability_from_row(self.transition_counts[row_key])

    def probability_from_row(self, row):
        total = float(sum(row.values()))
        new_row = dict()
        for entry in row:
            new_row[entry] = row[entry] / total
        return new_row

    #source is a file with the same format 
    def classify(self, source, kaggle = None):
        #dictionary of dictionaries
        test_data = self.parse_file(source)
        predictions = []
        for doc in test_data:
            tags = self.viterbi(doc)
            predictions.append(tags)
        if kaggle != None:
            with open(kaggle,'w') as f:
                f.write('Id,answer\n')
                i = 0
                for seq in predictions:
                    for tag in seq:
                        i += 1
                        f.write(str(i) + ',' + str(tag) + '\n')
        return predictions

    #doc is a list of observations to tag
    def viterbi(self, doc):
        table = [dict() for _ in doc]

        #initialize table
        new_column = dict()
        for i in range(1,self.n):
            for perm in itertools.product(self.states,repeat = i):
                for column in table:
                    column[perm] = (0,None)
        prev = ['start']

        pp = pprint.PrettyPrinter(indent=4)
        #populate base case
        for state in self.states:
            if state == 'start':
                continue
            trans = 0
            if state in self.transition_probabilities[tuple(prev)]:
                trans = self.transition_probabilities[tuple(prev)][state]
            output = self.output_probabilities[state]['<unk>']
            if tuple(doc[0][1]) in self.output_probabilities[state]:
                output = self.output_probabilities[state][tuple(doc[0][1])]
            if self.n == 2:
                table[0][tuple([state])] = ((math.log(trans) + math.log(output)), tuple(prev))
            else:
                table[0][('start',state)] = ((math.log(trans) + math.log(output)), tuple(prev))
        #fill the rest of table
        for i in range(1,len(doc)):
            # print i
            for state in self.states:
                lst = []
                if state == 'start':
                    continue
                for prev in table[0]:
                    trans = 0
                    if prev in self.transition_probabilities and state in self.transition_probabilities[prev]:
                        trans = self.transition_probabilities[prev][state]
                    output = self.output_probabilities[state]['<unk>']
                    if tuple(doc[i][1]) in self.output_probabilities[state]:
                        output = self.output_probabilities[state][tuple(doc[i][1])]
                    if table[i-1][prev][0] != 0.0:
                        lst.append(((table[i-1][prev][0] + math.log(trans) + math.log(output)), prev))
                (prob, prev) = max(lst)
                trace = prev
                prev = list(prev)
                prev.append(state)
                if len(prev) >= self.n:
                    prev.pop(0)
                table[i][tuple(prev)] = (prob,trace)

        #trace the table to get the result
        start = max((v,table[len(table)-1][v]) for v in table[len(table)-1] if table[len(table)-1][v][0] < 0)
        trace = []
        trace.append(list(start[0])[len(start[0])-1])
        lookup = start[1][1]
        # pp.pprint(table)
        for i in range(len(table)-2,-1,-1):
            entry = table[i][lookup]
            trace.append(list(lookup)[len(lookup)-1])
            lookup = entry[1]
        trace = list(reversed(trace))
        print trace
        # print trace
        return trace        

a = HMM('data/basic_features_train.txt', 4)
a.classify('data/basic_features_test.txt', 'kaggle_hmm_test.csv')
