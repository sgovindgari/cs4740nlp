import re,pickle,pprint,numpy

#To run must download stopwords and wordnet using nltk.download()
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
from nltk import pos_tag, word_tokenize
from operator import *

# for dictionary XML
import re, string

lemma = WordNetLemmatizer()

functions = dict()
functions['boolean'] = lambda word,i,count: 1
functions['simple'] = lambda word,i,count: count + 1
functions['linear'] = lambda word,i,count: count + 1.0/(i+1)

#Cleans a list of words - removes stopwords and punctuation, lemmatizes any other words
def clean(words):
    return [lemma.lemmatize(word) for word in words if (re.match('.*\w+.*',word) != None) and (word not in stopwords.words('english'))]

#For cleaning the data files - remove stopwords, punctuation and 
def cleanFile(source, destination):
    with open(source) as s:
        with open(destination,'w') as d:
            r = re.compile('\||%%')
            j = 0
            for line in s:
                j += 1
                [word,meaning,prev,actual,after] = r.split(line)
                #Turn prev and after into a list of words and only include those that are within the window
                prev = ' '.join(clean(prev.strip().lower().split(' ')))
                after = ' '.join(clean(after.strip().lower().split(' ')))
                d.write(word + "|" + meaning + "|" + prev + "%%" + actual + "%%" + after + "\n")
                if j % 1000 == 0:
                    print j

# for simply cleaning a string. no preconditions; string may be in original form.
# input string, output string with lemmatizing, removed stopwords, punct
def cleanString(strn):
    # list of words, lowercase, remove all punctuation
    # NOTE: this treats "they'll" as "theyll"
    #strlist = strn.strip().lower().split(' ') # this does not remove punctuation
    strlist = strn.strip().lower().translate(None, string.punctuation).split(' ')
    strlistclean = clean(strlist) # caution: may be empty! (exist.v definition "be")
    # use cleaned string except when cleaned result is empty
    try: cleanstr = reduce(lambda a,b:a+' '+b, strlistclean)
    except: cleanstr = reduce(lambda a,b:a+' '+b, strlist)
    return cleanstr

#windowSize is how many on each side to consider
#separate - consider the word "dog" coming after the word as a different feature from the word "dog" before the word
#countFunction - different weighted functions
#loc - location to save pickled examples to
def constructSet(source='training_clean.data',windowSize=-1,usePos=True,useColocation=True,useCooccurrence=True,countFunction=functions['boolean'],loc=None):
    maxAfter = []
    maxPrev = []
    data = ''
    r = re.compile('\||%%')
    res = []
    with open(source) as f:
        for line in f:
            #Don't care about how the word is actually appearing
            [word,sense,prev,_,after] = r.split(line)
            #Split POS from the word
            [word,pos] = word.split('.')
            #Turn prev and after into a list of words and only include those that are within the window
            prev = prev.strip().lower().split(' ')
            prev.reverse()
            after = after.strip().lower().split(' ')
            maxAfter.append(len(after))
            maxPrev.append(len(prev))
            if windowSize != -1:
                prev = prev[:windowSize]
                after = after[:windowSize]
            features = dict()
            if usePos:
                features['POS'] = pos.strip()
            length = windowSize if windowSize != -1 else max(len(prev),len(after))
            for i in range(length):
                if i < len(prev):
                    if useCooccurrence:
                        #Compute co-occurrence features for previous window
                        prevEntry = prev[i]
                        if prevEntry in features:
                            features[prevEntry] = countFunction(prev[i],i,features[prevEntry])
                        else: 
                            features[prevEntry] = countFunction(prev[i],i,0)
                    if useColocation:
                        #Compute co-locational features
                        features[('prev',i+1)] = prev[i]
                        text = word_tokenize(prev[i])
                        tag = pos_tag(text)
                        if len(tag) != 0:
                            features[('prev-pos',i+1)] = tag[0][1]
                if i < len(after):
                    if useCooccurrence:
                        #Compute co-occurence features for after window
                        afterEntry = after[i]
                        if afterEntry in features:
                            features[afterEntry] = countFunction(after[i],i,features[afterEntry])
                        else: 
                            features[afterEntry] = countFunction(after[i],i,0)
                    if useColocation:
                        #Compute co-locational features
                        features[('after',i+1)] = after[i]
                        text = word_tokenize(after[i])
                        tag = pos_tag(text)
                        if len(tag) != 0:
                            features[('after-pos',i+1)] = tag[0][1]
            example = (word.strip(),int(sense.strip()),features)
            res.append(example)
    #Save the training examples object
    if loc != None:
        pickle.dump(res,open(loc,'w'))

    #Generate statistics about the data
    # print "Previous::: mean: " + str(numpy.mean(maxPrev)) + " median: " + str(numpy.median(maxPrev)) + " max: " + str(max(maxPrev))
    # print "After::: mean: " + str(numpy.mean(maxAfter)) + " median: " + str(numpy.median(maxAfter)) + " max: " + str(max(maxAfter))
    return res

def argmax(pairs):
    return max(pairs, key=itemgetter(1))[0]

# preprocess dictionary XML: remove all '"' characters in examples
# arguments:
#   dictionaryFileloc is a string to the file to parse
#   outputFileloc is the location to write the preprocessed output.
def fixDoubles(dictionaryFileloc, outputFileloc):
    with open(dictionaryFileloc) as f:
        dictContent = f.read()
        for i in range(20): # min 12 (trial and error)
            dictContent = re.sub( \
                'examples="(.*)"(.*)" />', \
                r'examples="\1\2" />', \
                dictContent)
        # handle 1 specific case of two senses: remove it and fix num count
        dictContent = re.sub('<lexelt item="drug.n" num="3">', \
            '<lexelt item="drug.n" num="2">', dictContent)
        dictContent = re.sub('<sense id="1&&2".* />\n', '', dictContent)
        with open(outputFileloc,'w') as outputFile:
            outputFile.write(dictContent)
