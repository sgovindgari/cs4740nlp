import re
import nltk

# Parses king james
# Tried parsing using XML parsers but input doesn't seem to be valid XML
# Returns a string of tokens separated by whitespace
def parseBible():
    f = open('bible_corpus/kjbible.train')
    bible = f.read()
    # Removes XML and psalm/verse numbers
    # then replaces start of string and double new lines with the sentence segmentation marker <s>.
    # finally adds spaces around all punctuation
    bible = re.sub('([.,!?();:])', r' \1 ', \
                    re.sub('(</?(TEXT|DOC)>\n)|([0-9]+:[0-9]+\s)', '', bible))
    bible = bible.strip()
    return bible

def parseReviews():
    pass


def saveFiles():
    with open('bible.train','w') as bible:
        bible.write(parseBible())

saveFiles()