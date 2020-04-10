# -*- coding: utf-8 -*-
# Copyright: (C) 2018-2020 Lovac42
# Support: https://github.com/lovac42/HoochiePapa
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html


## Performance Config ####################################

# Performance impact cost O(n)
# Uses quick shuffle if limit is exceeded.
DECK_LIST_SHUFFLE_LIMIT = 256

##########################################################

import random
import anki.sched
from aqt import mw
from anki.utils import ids2str
from aqt.utils import showText
from anki.hooks import wrap

from .sort import CUSTOM_SORT
from .lib.com.lovac42.anki.version import ANKI20



#Turn this on if you are having problems.
def debugInfo(msg):
    # print(msg) #console
    # showText(msg) #Windows
    return


#From: anki.schedv2.py
#Mod:  Various, see logs
def fillNew(self, _old):
    if self._newQueue:
        return True
    if not self.newCount:
        return False
    # Below section is invoked everytime the reviewer is reset (edits, adds, etc)

    if self.col.decks.get(self.col.decks.selected(),False)['dyn']:
        return _old(self)

    qc = self.col.conf
    if not qc.get("hoochiePapa", False):
        return _old(self)
    debugInfo('using hoochiePapa')

    did=self.col.decks.selected()
    lim=self._deckNewLimit(did)
    if lim:
        sortLevel=qc.get("hoochiePapaSort", 0)
        assert sortLevel < len(CUSTOM_SORT)
        sortBy=CUSTOM_SORT[sortLevel][1]

        lim=min(self.queueLimit,lim)
        self._newQueue=getNewQueuePerSubDeck(self,sortBy,lim)
        if self._newQueue:
            if sortLevel:
                self._newQueue.reverse() #preserve order
            else:
                r = random.Random()
                # r.seed(self.today) #same seed in case user edits card.
                r.shuffle(self._newQueue)
            return True

    if self.newCount:
        # if we didn't get a card but the count is non-zero,
        # we need to check again for any cards that were
        # removed from the queue but not buried
        self._resetNew()
        return self._fillNew()


#Custom queue builder for New-Queue
def getNewQueuePerSubDeck(sched, sortBy, penetration):
    mulArr=[]
    LEN=len(sched._newDids)
    if LEN>DECK_LIST_SHUFFLE_LIMIT: #segments
        sched._newDids=cutDecks(sched._newDids,4) #0based
    else: #shuffle deck ids
        r=random.Random()
        r.shuffle(sched._newDids)

    pen=max(5,penetration//LEN) #if div by large val
    size=0
    for did in sched._newDids:
        lim=sched._deckNewLimit(did)
        if not lim: continue
        lim=min(pen,lim)

        arr=sched.col.db.list("""
select id from cards where
did = ? and queue = 0
%s,ord limit ?"""%sortBy, did, lim)
        arr.reverse()
        mulArr.append(arr)
        size+=len(arr)
        if size>=penetration: break

    return mergeQueues(mulArr,size)


def mergeQueues(mulArr, size):
    newQueue=[]
    while len(newQueue)<size:
        for arr in mulArr:
            if arr:
                newQueue.append(arr.pop())
    return newQueue


#Like cutting cards, this is a quick and dirty way to randomize the deck ids
def cutDecks(queue,cnt=0):
    total=len(queue)
    p=random.randint(30,70) # %
    cut=total*p//100
    if cnt:
        q=cutDecks(queue[cut:],cnt-1)
        return q+cutDecks(queue[:cut],cnt-1)
    return queue[cut:]+queue[:cut]


anki.sched.Scheduler._fillNew = wrap(anki.sched.Scheduler._fillNew, fillNew, 'around')
if not ANKI20:
    import anki.schedv2
    anki.schedv2.Scheduler._fillNew = wrap(anki.schedv2.Scheduler._fillNew, fillNew, 'around')
