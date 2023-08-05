Overview
========

A sample python lib generate the gibberish feature

Usage
=====
```
import pydomaingibfeature
if __name__ == '__main__':
    #f = pydomaingibfeature.PyDomainGibFeature({'npart': 3, 
    #        'mfiles': ['ch2.pki','ch3.pki','ch4.pki','en2.pki','en3.pki','en4.pki',]})
    f = pydomaingibfeature.PyDomainGibFeature({})
    while True:
        iput = raw_input().strip()
        print f.range()
        print f.feature(iput)
```

