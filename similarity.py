'''
Created on Oct 7, 2015

'''
import os
import re
import math

# read text file and store data in an array of objects (conversation [])
# conversation = []
# dirs = os.walk('./')
# for root, dirs, files in dirs:
#     for thefile in files:
#         filetype = thefile.split('.')
#         if filetype[1] == 'txt':
#             with open(root + thefile, 'rb') as openfile:
#                 for line in openfile.readlines():
#                     if line == '\n': continue
#                     line = line.rstrip('\n') #remove '/n' at the end 
#                     parts = line.split(': ')
#                     row = {'Sender': parts[0], 'Text': parts[1]}
#                     conversation.append(row)

# ## Similarity metrics

def idf(t,dockey, turnbyturntokens):
    idfcache = {}
    D = turnbyturntokens[dockey]

    if dockey in idfcache:
        if t in idfcache[dockey]:
            return idfcache[dockey][t]
        else:
            theidf = doidf(t,D)
            idfcache[dockey][t] = theidf
            return theidf
    else:
        theidf = doidf(t,D)
        idfcache[dockey] = {}
        idfcache[dockey][t] = theidf
        return theidf

def doidf(t,D):
    N = len(D)
    term_in_docs = 1 + len([i for d in D for i in d.values() if t in i and i[t] > 0])
#     print N, term_in_docs, float(N)/term_in_docs
    return math.log(float(N)/term_in_docs)


def windowweights(x):
    y = -float(1)/4*x+1
    if y > 0: return y
    else: return 0

def tokenize(text):
    tokens = re.split(r'(\w+|\$[\d\.]+|\S+)', text) 
    tokens = [t.lower() for t in tokens if t != ' ' and t != '' and t != ',' and t != '.' and t != '?']
    return tokens
# tokenize("Yeah! but? you :) have to take into. consideration the new generation ")

def cossimilarity(a,b):
    numerator = sum([a[i]*b[i] for i in a])
    denleft = math.sqrt(sum([a[i]**2 for i in a]))
    denright = math.sqrt(sum([b[i]**2 for i in b]))
    denominator = denleft * denright
    
    if denominator == 0:
        similarity = 0
    else:
        similarity = numerator/denominator
    return similarity


def build_turnbyturntokens(conversation):

    allsimilarities = {} # full conversation similarities keyed on pair
    turnbyturntokens = {} # token counts keyed by pair then turn (list) then participant (dict)
    #                    {pair: [{u1: {'the': 2, ':)': 1}, u2: {'the': 2, ':)': 1}}, {u1: {'the': 2, ':)': 1}, u2: {'the': 2, ':)': 1}}]}

    # convnum = 0 # there'll be an outer loop later. for testing, just one at a time
    # conv = conversations[convnum]

    convlen = len(conversation) # length in lines, not turns
    convtokencounts = {} # container for token counts accumulated over the full conversation, keyed by user

    similarities = [] # updated *cumulative* similarity after each turn
    
    turntokencounts = [] # container for token counts from *each* turn
    turn = 1
    pair = ''

    # initialize senders A and B, and their respective count dicts
    for l,line in enumerate(conversation):
        sender = line['Sender']
        if l == 0:
            a = sender
            convtokencounts[a] = {}
            b = ''
            if pair == '':
                if 'pair' in line: pair = line['pair']
#                     else:
#                         pair = idsconditions[line['ParticipantID']]['pairnum']
        elif b == '' and sender != a:
            b = sender
            convtokencounts[b] = {}
            break
    
    if b == '':
        if a == 'SU6DK904V': b = 'WP1M0X6J4'
        elif a == 'WP1M0X6J4': b = 'SU6DK904V'
        convtokencounts[b] = {}

#         print 'pair: ' + pair + ', sender: ' + sender

    # print pair, a, b

    # for l,line in enumerate(conv):
    #     sender = line['Sender']
    #     if l == 0:
    #         a = sender
    #         convtokencounts[a] = {}
    #         b = ''
    #         if 'pair' in line: pair = line['pair']
    #         else:
    #             pair = idsconditions[line['ParticipantID']]['pairnum']
    #     elif b == '' and sender != a:
    #         b = sender
    #         convtokencounts[b] = {}
    #         break
    
    turntokencountsbyuser = {} # the dict that makes up a list item in turnbyturntokens. just have to init here for first turn.
    turntokencountsbyuser[a] = {}
    turntokencountsbyuser[b] = {}
    for l,line in enumerate(conversation):
        sender = line['Sender']
        if sender == a:
            othersender = b
        else:
            othersender = a

        # print sender, othersender
        localtokencounts = convtokencounts[sender] # in retrospect, i guess this works because it's mutable? immutable? one of those.
        text = line['Text']
        tokens = tokenize(text)
        for t in tokens:
            # cumulative
            if t in localtokencounts:
                localtokencounts[t] += 1
            else:
                localtokencounts[t] = 1
            if t not in convtokencounts[othersender]:
                convtokencounts[othersender][t] = 0

            # by turn
            if t in turntokencountsbyuser[sender]:
                turntokencountsbyuser[sender][t] += 1
            else:
                turntokencountsbyuser[sender][t] = 1
            if t not in turntokencountsbyuser[othersender]:
                turntokencountsbyuser[othersender][t] = 0

        if l+1 < len(conversation):
            if conversation[l+1]['Sender'] != sender: # if the next line has a different sender, it's the end of a turn
                similarities.append(cossimilarity(convtokencounts[a], convtokencounts[b]))
                
                # set things up for the next turn
                turn += 1
                turntokencounts.append(turntokencountsbyuser) # doing this then overwriting turntokencountsbyuser might be a problem. might have to deep copy
                turntokencountsbyuser = {}
                turntokencountsbyuser[a] = {}
                turntokencountsbyuser[b] = {}
        else: # last line
            similarities.append(cossimilarity(convtokencounts[a], convtokencounts[b]))
            turntokencounts.append(turntokencountsbyuser)

    allsimilarities[pair] = similarities
    turnbyturntokens[pair] = turntokencounts
    return turnbyturntokens

def computetbtsimilarities(turnbyturntokens, windowfn, termscalefn):
    turnbyturnsimilarities = {}
    for pair in turnbyturntokens:
        # tbtpair = turnbyturntokens[2] # [{'Gesorl': {'hi': 1}, 'Mebian': {'hi': 0}}]
        tbtpair = turnbyturntokens[pair]

        windowedtokens = {} # something like convtokencounts, but which recomputes for every turn. will add each result to a list
        windowedsimilarities = [] # this is the list that similarity scores will go in

        # init A and B like before. they're usernames.
        a = tbtpair[0].keys()[0]
        b = tbtpair[0].keys()[1]
        windowedtokens[a] = {}
        windowedtokens[b] = {}

        for turnnum,turn in enumerate(tbtpair):
            # start here, add weighted counts of tokens to windowedtokens, then decrement turn and do it again for previous turns with other weights
            for tback in range(turnnum+1): # number of turns back. we'll be using this to subtract.
                if windowfn(tback) == 0: break # no need to go past the end of the window
                for token in tbtpair[turnnum-tback][a]: #tokens used by A
                    # if token in emoticons:
                    termweight = termscalefn(token, pair, turnbyturntokens)
                    if token in windowedtokens[a]:
                        windowedtokens[a][token] += windowfn(tback) * termweight * tbtpair[turnnum-tback][a][token]
                    else:
                        windowedtokens[a][token] = windowfn(tback) * termweight * tbtpair[turnnum-tback][a][token]
                
                for token in tbtpair[turnnum-tback][b]: #tokens used by B
                    # if token in emoticons:
                    termweight = termscalefn(token, pair, turnbyturntokens)
                    if token in windowedtokens[b]:
                        # this used to have termscalefn(tbtpair[turnnum-tback][b][token], tbtpair). I think that's a bug.
                        windowedtokens[b][token] += windowfn(tback) * termweight * tbtpair[turnnum-tback][b][token]
                    else:
                        windowedtokens[b][token] = windowfn(tback) * termweight * tbtpair[turnnum-tback][b][token]
            windowedsimilarities.append(cossimilarity(windowedtokens[a], windowedtokens[b]))
            # clear it out after each turn
    #         print windowedtokens
            windowedtokens[a] = {}
            windowedtokens[b] = {}
        turnbyturnsimilarities[pair] = windowedsimilarities
    #return turnbyturnsimilarities
    return windowedsimilarities
