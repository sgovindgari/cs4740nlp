#!/usr/bin/env python
# may require package install

import utilities, pprint, math

# xml parser!
from lxml import etree

dictionarySource    = 'dictionary.xml'
dictionaryProcessed = 'dictionary_processed.xml'

class DictionaryWSD():
    def __init__(self, sourceXMLDict=dictionaryProcessed):
        self.XMLSource = sourceXMLDict
        self.xml = etree.parse(self.XMLSource)

    def m(self):
        return 1


# MAIN
# preprocess dictionary XML:
#   remove all '"' characters in examples
#   sense id: '1&&2' -> '1aa2'
utilities.fixDoubles(dictionarySource, dictionaryProcessed)

dwsd = DictionaryWSD(dictionaryProcessed)
print dwsd.m()
