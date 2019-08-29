#!/usr/bin/env python
import sys

topics=["music","piano","guitar","violin","orchestra","sing","song","play","jazz","blues"]

for line in sys.stdin:
    #--- split the line into words ---
    words = line.strip().split()

    for i in range(len(words)-1):
        if words[i] in topics:
            print('%s|%s\t%s' % (words[i],words[i+1], "1"))
           
