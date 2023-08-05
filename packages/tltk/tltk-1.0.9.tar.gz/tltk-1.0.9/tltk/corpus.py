#!/usr/bin/python
# -*- coding: utf-8 -*-
#########################################################
## Thai Language Toolkit : version  1.0.9
## Chulalongkorn University
## written by Wirote Aroonmanakun
## Implemented :
##      loadTNC(), load3gram(Filename), unigram(w1), bigram(w1,w2), trigram(w1,w2,w3)
##      collocates(w,SPAN,STAT,DIR,LIMIT, MINFQ) = [wa,wb,wc]
##      similarlity(w1,w2) 
#########################################################

import re
import os
import math
from collections import defaultdict
from operator import itemgetter
import gensim
#import gensim, logging
#logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


def TNC_load():
    global TriCount
    global BiCount
    global BiCount2
    global UniCount
    global TotalWord
    
    TriCount = defaultdict(int)
    BiCount = defaultdict(int)
    UniCount = defaultdict(int)
    BiCount2 = defaultdict(int)
    TotalWord = 0

    path = os.path.abspath(__file__)
    ATA_PATH = os.path.dirname(path)
    try: 
        InFile = open(ATA_PATH + '/TNC.3g','r',encoding='utf8')
    except IOError:
        InFile = open('TNC.3g','r',encoding='utf8')        
#    Filename = ATA_PATH + '/TNC.3g'
#    InFile = open(Filename,'r',encoding='utf8')
    for line in InFile:
        line.rstrip()
        (w1,w2,w3,fq) = line.split('\t')
        freq = int(fq)
        TriCount[(w1,w2,w3)] = freq
        BiCount[(w1,w2)] += freq
        UniCount[w1] += freq
        BiCount2[(w1,w3)] += freq
        TotalWord += freq
    return(1)

#### load a trigram file
def trigram_load(Filename):
    global TriCount
    global BiCount
    global BiCount2
    global UniCount
    global TotalWord
    
    TriCount = defaultdict(int)
    BiCount = defaultdict(int)
    UniCount = defaultdict(int)
    BiCount2 = defaultdict(int)
    TotalWord = 0

    InFile = open(Filename,'r',encoding='utf8')
    for line in InFile:
        line.rstrip()
        (w1,w2,w3,fq) = line.split('\t')
        freq = int(fq)
        TriCount[(w1,w2,w3)] = freq
        BiCount[(w1,w2)] += freq
        UniCount[w1] += freq
        BiCount2[(w1,w3)] += freq
        TotalWord += freq
    return(1)
    

#### return bigram in per million 
def unigram(w1):
    global UniCount
    global TotalWord
    
    if w1 in UniCount:
        return(float(UniCount[w1] * 1000000 / TotalWord))
    else:
        return(0)

#### return bigram in per million 
def bigram(w1,w2):
    global BiCount
    global TotalWord
    
    if (w1,w2) in BiCount:
        return(float(BiCount[(w1,w2)] * 1000000 / TotalWord))
    else:
        return(0)
    
#### return trigram in per million 
def trigram(w1,w2,w3):
    global TriCount
    global TotalWord
    
    if (w1,w2,w3) in TriCount:
        return(float(TriCount[(w1,w2,w3)] * 1000000 / TotalWord))
    else:
        return(0)

##################################################        
##### Find Collocate of w1,  stat = {mi, chi2, freq}  direction = {left, right, both}  span = {1,2}
#### return dictionary colloc{ (w1,w2) : value }
def collocates(w,stat="chi2",direct="both",span=2,limit=10,minfq=1):
    global BiCount
    global BiCount2
    global TotalWord
    
    colloc = defaultdict(float)
    colloc.clear()
    
    if stat != 'mi' and stat != 'chi2':
        stat = 'freq' 
    if span != 2:
        span = 1 
    if direct != 'left' and direct != 'right':
        direct = 'both'
        
    if span == 1:    
        if direct == 'right' or direct == 'both':
            for w2 in [ key[1] for key in BiCount.keys() if key[0] == w]:
                if BiCount[(w,w2)] >= minfq:
                    colloc[(w,w2)] = compute_colloc(stat,w,w2)
        if direct == 'left' or direct == 'both':
            for w1 in [ key[0] for key in BiCount.keys() if key[1] == w]:
                if BiCount[(w1,w)] >= minfq:
                    colloc[(w1,w)] = compute_colloc(stat,w1,w)
    elif span == 2:
        if direct == 'right' or direct == 'both':
            for w2 in [ key[1] for key in BiCount.keys() if key[0] == w]:
                if BiCount[(w,w2)] >= minfq:
                    colloc[(w,w2)] = compute_colloc(stat,w,w2)
        if direct == 'left' or direct == 'both':
            for w1 in [ key[0] for key in BiCount.keys() if key[1] == w]:
                if BiCount[(w1,w)] >= minfq:
                    colloc[(w1,w)] = compute_colloc(stat,w1,w)
        if direct == 'right' or direct == 'both':
            for w2 in [ key[1] for key in BiCount2.keys() if key[0] == w]:
                if BiCount2[(w,w2)] >= minfq:
                    colloc[(w,w2)] = compute_colloc2(stat,w,w2)
        if direct == 'left' or direct == 'both':
            for w1 in [ key[0] for key in BiCount2.keys() if key[1] == w]:
                if BiCount2[(w1,w)] >= minfq:
                    colloc[(w1,w)] = compute_colloc2(stat,w1,w)
                
    return(sorted(colloc.items(), key=itemgetter(1), reverse=True)[:limit])
    
#    return(colloc)

##########################################
# Compute Collocation Strength between w1,w2  use bigram distance 2  [w1 - x - w2]
# stat = chi2 | mi | freq
##########################################
def compute_colloc2(stat,w1,w2):
    global BiCount2
    global UniCount
    global TotalWord

    bict = BiCount2[(w1,w2)]
    ctw1 = UniCount[w1]
    ctw2 = UniCount[w2]
    total = TotalWord
    
    if bict < 1 or ctw1 < 1 or ctw2 < 1:
        bict +=1
        ctw1 +=1
        ctw2 +=1 
        total +=2
    
###########################
##  Mutual Information
###########################
    if stat == "mi":
        mi = float(bict * total) / float((ctw1 * ctw2))
        value = math.log(mi,2)
#########################
### Compute Chisquare
##########################
    if stat == "chi2":
        value=0
        O11 = bict
        O21 = ctw2 - bict
        O12 = ctw1 - bict
        O22 = total - ctw1 - ctw2 +  bict
        value = float(total * (O11*O22 - O12 * O21)**2) / float((O11+O12)*(O11+O21)*(O12+O22)*(O21+O22))
#########################
### Compute Frequency (per million)
##########################
    if stat == 'freq':
        value = float(bict * 1000000 / total)
        
    return(value)


##########################################
# Compute Collocation Strength between w1,w2  use bigram distance 1  [w1 - w2]
# stat = chi2 | mi | ll
##########################################
def compute_colloc(stat,w1,w2):
    global BiCount
    global UniCount
    global TotalWord


    bict = BiCount[(w1,w2)]
    ctw1 = UniCount[w1]
    ctw2 = UniCount[w2]
    total = TotalWord
    

    if bict < 1 or ctw1 < 1 or ctw2 < 1:
        bict +=1
        ctw1 +=1
        ctw2 +=1 
        total +=2
    
###########################
##  Mutual Information
###########################
    if stat == "mi":
        mi = float(bict * total) / float((ctw1 * ctw2))
        value = math.log(mi,2)
#########################
### Compute Chisquare
##########################
    if stat == "chi2":
        value=0
        O11 = bict
        O21 = ctw2 - bict
        O12 = ctw1 - bict
        O22 = total - ctw1 - ctw2 +  bict
        value = float(total * (O11*O22 - O12 * O21)**2) / float((O11+O12)*(O11+O21)*(O12+O22)*(O21+O22))
#########################
### Compute Frequency (per million)
##########################
    if stat == 'freq':
        value = float(bict * 1000000 / total)
        
    return(value)

#######################################################################
### word2vec model created from TNC 3.0
def w2v_load():
    global w2v_model

    path = os.path.abspath(__file__)
    ATA_PATH = os.path.dirname(path)
    try:
        w2v_model = gensim.models.Word2Vec.load(ATA_PATH +'/' +"TNCc5model.bin")
    except IOError:
        w2v_model = gensim.models.Word2Vec.load("TNCc5model.bin")
    return(1)

def w2v_exist(w):
    global w2v_model
#    try:
#      w2v_model
#    except NameError:
#      w2v_load()
    if w in list(w2v_model.wv.vocab):
        return(True)
    else:
        return(False)
    
def similarity(w1,w2):
    global w2v_model
    degree = ''
    vocabs = list(w2v_model.wv.vocab)
    if w1 in vocabs and w2 in vocabs:
        degree = w2v_model.similarity(w1,w2)
    return(degree)

def similar_words(w1,n=10,cutoff=0.,score="n"):
    global w2v_model                
    if w1 in list(w2v_model.wv.vocab):
        out = w2v_model.most_similar(w1)
        result = []
        ct = 0
        for (w,p) in out:
            if p > cutoff and ct < n:
                if score == 'n':
                    result.append(w)
                else:
                    result.append((w,p))
                ct += 1
    return(result)

def outofgroup(wrdlst):
    global w2v_model
    wrdlst1 = []
    try:
      w2v_model
    except NameError:
      w2v_load()
    vocabs = list(w2v_model.wv.vocab)
    for w in wrdlst:
        if w in vocabs:
            wrdlst1.append(w)
    out = w2v_model.doesnt_match(wrdlst1)
    return(out)


############ END OF GENERAL MODULES ##########################################################################


