import sys
import os
import pydomaintextfeature.DomainPostFix as Postfix
import pyngramgen



class PyDomainTextFeature: 
    """
    """
    def __init__(self, dic): 
        self.ngram = dic.get('ngram', 2)
    
    def norm_dict(self): 
        d = {}
        d[0] = (0.0, 1.0)
        d[1] = (0.0, 1.0)
        d[2] = (0.0, 30)
        d[3] = (0.0, 10)
        for i in xrange(4, 5 + len(Postfix.domain_postfix) + (26 ** self.ngram)):
            d[i] = (0.0, 1.0)
        return d

    def neednorm(self): 
        return False

    def range(self): 
        return 4 + (len(Postfix.domain_postfix) + 1) + (26 ** self.ngram)

    def feature(self, dm):
        seg = [len(x) for x in dm.split('.')]
        llen = float(sum(seg))
        post_fix = '.' + dm.split('.')[-1]
        fea = [ 
        (0, float(len([x for x in dm if x.isdigit()]))/llen),
        (1, float(len([x for x in dm if x.isalpha()]))/llen),
        (2, max(seg)),
        (3, min(seg)),
        ]
        if post_fix in Postfix.domain_postfix: 
            fea.append((5+Postfix.domain_postfix[post_fix],1))
        else:
            fea.append((4, 1))
        base = 4 + (len(Postfix.domain_postfix) + 1)

        sgram = set([i[1] for i in pyngramgen.PyNgramGen(self.ngram, 'abcdefghijklmnopqrstuvwxyz').generator(dm)])
        for i in sgram:
            fea.append((base + i, 1))
        return sorted(fea,cmp=lambda x,y:cmp(x[0], y[0]))

if __name__ == '__main__': 
    while True: 
        iput = raw_input()
        f = PyDomainTextFeature({'ngram':3})
        print f.range()
        print f.feature(iput)
