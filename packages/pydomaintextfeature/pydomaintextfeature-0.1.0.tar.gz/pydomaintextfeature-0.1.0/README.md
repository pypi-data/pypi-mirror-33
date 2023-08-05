Overview
========
This lib generate text feature sparse vector for a given domain

Usage
=====
```
import pydomaintextfeature 
if __name__ == '__main__':
    while True:
        iput = raw_input()
        f = Ppydomaintextfeature.yDomainTextFeature({'ngram':3})
        print f.range()
        print f.feature(iput)
```

