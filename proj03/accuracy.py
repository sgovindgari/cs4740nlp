#!/usr/bin/env python

import sys

numTotal = 2612

answerFile = 'data/training_results.csv'

if len(sys.argv) != 2:
    print "./accuracy.py [traincsvfile]"
    sys.exit(0)

with open(answerFile) as ans:
    acontent = ans.read()
    asplits = acontent.split('\n')
    asplits = asplits[1:-1]
    with open(sys.argv[1]) as f:
        content = f.read()
        splits = content.split('\n')
        splits = splits[1:-1] # get rid of header, empty last line
        if len(asplits) != len(splits): # assert they're same size
            print "WHAT!!!!!!!!!!!!!"
            print len(asplits)
            print len(splits)
            sys.exit(0)
        agree = 0

        for lidx in range(0,len(splits)):
            idx,res = tuple(splits[lidx].split(','))
            aidx,ares = tuple(asplits[lidx].split(','))
            if int(res) == int(ares):
                agree += 1
        print sys.argv[1], agree, numTotal, float(agree)/numTotal
