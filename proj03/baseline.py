
#Baseline model
class Baseline():

    def __init__(self, source):
        self.word_counts = dict()
        self.parse_training(source)

    def parse_training(self, source):
        data = ''
        with open(source) as f:
            data = f.read()
        docs = data.split('\n\n')
        sentences = []
        for doc in docs:
            sentences = doc.split('\n')
            for sentence in sentences:
                words = sentence.split(' ')
