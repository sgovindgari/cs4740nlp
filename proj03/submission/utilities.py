#To run must download stopwords and wordnet using nltk.download()
# for stopping and stemming!
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer

import re, string

lemma = WordNetLemmatizer()

#Cleans a list of words - removes stopwords, lemmatizes any other words
def clean(words):
    return [lemma.lemmatize(word) for word in words if word != '' and (word not in stopwords.words('english'))]

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
# input string, output string with lemmatizing, removed stopwords
def cleanString(strn):
    # rm parens
    strn = strn.replace("(","").replace(")","")
    # put spaces between each word/punct.
    strn = re.sub('([,!?();:"-&/$])', r' \1 ', strn)
    strn = re.sub('(\.{1,})',r' \1 ', strn)
    # list of words, lowercase, remove some punctuation
    strn = strn.strip().lower()
    strlist = strn.split(' ')
    strlistclean = clean(strlist) # caution: may be empty! (exist.v definition "be")
    # use cleaned string except when cleaned result is empty
    try: cleanstr = reduce(lambda a,b:a+' '+b, strlistclean)
    except: cleanstr = reduce(lambda a,b:a+' '+b, strlist)
    return cleanstr
