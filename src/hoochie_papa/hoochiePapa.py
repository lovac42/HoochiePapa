# -*- coding: utf-8 -*-
# Copyright: (C) 2018-2020 Lovac42
# Support: https://github.com/lovac42/HoochiePapa
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html



CUSTOM_SORT = {
  0:["None (Shuffled)", "order by due"],

# == User Config =========================================

  1:["Due (asc)",            "order by due asc"],
  2:["Due (desc)",          "order by due desc"],
  3:["Creation Time (asc)",   "order by id asc"],
  4:["Creation Time (desc)", "order by id desc"],
  5:["Mod Time (asc)",       "order by mod asc"],
  6:["Mod Time (desc)",     "order by mod desc"],
  7:["Left (asc)",          "order by left asc"],
  8:["Left (desc)",        "order by left desc"],
  9:["Factor (asc)",      "order by factor asc"],
 10:["Factor (desc)",    "order by factor desc"]

# == End Config ==========================================

}


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

from anki import version
ANKI21 = version.startswith("2.1.")


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
if ANKI21:
    import anki.schedv2
    anki.schedv2.Scheduler._fillNew = wrap(anki.schedv2.Scheduler._fillNew, fillNew, 'around')


##################################################
#
#  GUI stuff, adds preference menu options
#
#################################################
import aqt
import aqt.preferences
from aqt.qt import *
from anki.lang import _


try:
    from PyQt4 import QtCore, QtGui as QtWidgets
except:
    from PyQt5 import QtCore, QtGui, QtWidgets


def setupUi(self, Preferences):
    try:
        grid=self.lrnStageGLayout
    except AttributeError:
        self.lrnStage=QtWidgets.QWidget()
        self.tabWidget.addTab(self.lrnStage, "Muffins")
        self.lrnStageGLayout=QtWidgets.QGridLayout()
        self.lrnStageVLayout=QtWidgets.QVBoxLayout(self.lrnStage)
        self.lrnStageVLayout.addLayout(self.lrnStageGLayout)
        spacerItem=QtWidgets.QSpacerItem(1, 1, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.lrnStageVLayout.addItem(spacerItem)

    r=self.lrnStageGLayout.rowCount()
    self.hoochiePapa = QtWidgets.QCheckBox(self.lrnStage)
    self.hoochiePapa.setText(_('Hoochie Papa! Randomize New Queue'))
    self.lrnStageGLayout.addWidget(self.hoochiePapa, r, 0, 1, 3)
    self.hoochiePapa.clicked.connect(lambda:toggle(self))

    r+=1
    self.hoochiePapaSortLbl=QtWidgets.QLabel(self.lrnStage)
    self.hoochiePapaSortLbl.setText(_("      Sort NewQ By:"))
    self.lrnStageGLayout.addWidget(self.hoochiePapaSortLbl, r, 0, 1, 1)

    self.hoochiePapaSort = QtWidgets.QComboBox(self.lrnStage)
    if ANKI21:
        itms=CUSTOM_SORT.items()
    else:
        itms=CUSTOM_SORT.iteritems()
    for i,v in itms:
        self.hoochiePapaSort.addItem(_(""))
        self.hoochiePapaSort.setItemText(i, _(v[0]))
    self.lrnStageGLayout.addWidget(self.hoochiePapaSort, r, 1, 1, 2)


def load(self, mw):
    qc = self.mw.col.conf
    cb=qc.get("hoochiePapa", 0)
    self.form.hoochiePapa.setCheckState(cb)
    idx=qc.get("hoochiePapaSort", 0)
    self.form.hoochiePapaSort.setCurrentIndex(idx)
    toggle(self.form)


def save(self):
    toggle(self.form)
    qc = self.mw.col.conf
    qc['hoochiePapa']=self.form.hoochiePapa.checkState()
    qc['hoochiePapaSort']=self.form.hoochiePapaSort.currentIndex()


def toggle(self):
    checked=self.hoochiePapa.checkState()
    if checked:
        grayout=False
    else:
        grayout=True
    self.hoochiePapaSort.setDisabled(grayout)
    self.hoochiePapaSortLbl.setDisabled(grayout)


aqt.forms.preferences.Ui_Preferences.setupUi = wrap(aqt.forms.preferences.Ui_Preferences.setupUi, setupUi, "after")
aqt.preferences.Preferences.__init__ = wrap(aqt.preferences.Preferences.__init__, load, "after")
aqt.preferences.Preferences.accept = wrap(aqt.preferences.Preferences.accept, save, "before")
