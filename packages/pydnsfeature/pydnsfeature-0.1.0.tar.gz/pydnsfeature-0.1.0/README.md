Overview
========
This lib generate dns feature for machine learning

Usage
=====
```
import pydnsfeature
if __name__ == '__main__':
    f = pydnsfeature.PyDnsFeature()
    while True:
        iput = raw_input()
        info = f.feature(iput)
        print info
```

