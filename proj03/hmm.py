#
class HMM():
    def __init__(self, source, n):
        # source is a file  where each document is separated by a new line and each line is a feature vector and label
        self.n = n
        self.source = source
        self.parse_training()
        self.construct_model()


    #Takes the source and parses it into a list of lists
    def parse_training(self):
        content = ''
        with open(self.source) as f:
            content = f.read()
        docs = content.split('\n\n')
        doc_list = []
        for doc in docs:
            sentences = doc.split('\n')
            sentence_list = []
            for sentence in sentences:
                #TODO: Parse each sentence
                res = sentence.split(',')
                sentence_list.append((int(res[0]),res[1]))
            doc_list.append(sentence_list)
        self.training_data = doc_list

    def construct_model(self):
        self.output_counts = dict()
        self.transition_counts = dict()
        self.states = set()
        self.states.add('start')
        for doc in self.training_data:
            prev = ['start']
            for sentence in doc:
                #add counts and such
                #etc.
                state = str(sentence[0])
                vector = sentence[1]
                sentence_key = tuple(vector)
                prev_key = tuple(prev)
                if prev_key in self.transition_counts:
                    if state in self.transition_counts[prev_key]:
                        self.transition_counts[prev_key][state] += 1
                    else:
                        self.transition_counts[prev_key][state] = 1
                else:
                    self.transition_counts[prev_key] = dict()
                    self.transition_counts[prev_key][state] = 1
                if state in self.output_counts:
                    if sentence_key in self.output_counts[state]:
                        self.output_counts[state][sentence_key] += 1
                    else:
                        self.output_counts[state][sentence_key] = 1
                else:
                    self.output_counts[state] = dict()
                    self.output_counts[state][sentence_key] = 1
                self.states.add(state)
                prev.append(str(sentence[0]))
                if len(prev) > self.n:
                    prev.pop(0)
        print self.output_counts



    #observed is a list of observed variables to tag
    def viterbi(self, observations):
        #dictionary of dictionaries
        table = []
        

a = HMM('test.data', 1)