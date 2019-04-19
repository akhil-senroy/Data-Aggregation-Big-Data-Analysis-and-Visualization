#!/usr/bin/env python
import sys

topics=["music", "guitar", "piano", "singer", "orchestra","violin","songs"]

data=[]

word = None
coword = None

for line in sys.stdin:
    
    #remove leading and trailing white spaces
    line= line.strip()
    #populating an array of words from each line
    for word in line.split():
        data.append(word)

for i in range(len(data)):
    if(data[i] in topics):
        word = data[i]
        if(data[i+1] in topics):
            coword = data[i+1]
            if(word!=coword2):
                print('%s|%s\t %s'%(word,coword,1))
