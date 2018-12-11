# -*- coding: utf-8 -*-
# Copyright: (C) 2018 Lovac42
# Support: https://github.com/lovac42/HoochiePapa
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
# Version: 0.0.2

# Title is in reference to Seinfeld, no relations to the current slang term.

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
        lim=min(self.queueLimit,lim)
        self._newQueue=getNewQueuePerSubDeck(self,lim)
        if self._newQueue:
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



def getNewQueuePerSubDeck(self,penetration):
    newQueue=[]
    pen=penetration//len(self.col.decks.active())
    pen=max(5,pen) #if div by large val
    for did in self._newDids:
        lim=self._deckNewLimit(did)
        if not lim: continue
        lim=min(pen,lim)

        arr=self.col.db.list("""
select id from cards where
did = ? and queue = 0
order by due limit ?""", did, lim)
        newQueue.extend(arr)
        if len(newQueue)>=penetration: break
    return newQueue


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


if ANKI21:
    from PyQt5 import QtCore, QtGui, QtWidgets
else:
    from PyQt4 import QtCore, QtGui as QtWidgets

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

def setupUi(self, Preferences):
    r=self.gridLayout_4.rowCount()
    self.hoochiePapa = QtWidgets.QCheckBox(self.tab_1)
    self.hoochiePapa.setObjectName(_fromUtf8("hoochiePapa"))
    self.hoochiePapa.setText(_('Hoochie Papa! Randomize NEW'))
    self.hoochiePapa.toggled.connect(lambda:toggle(self))
    self.gridLayout_4.addWidget(self.hoochiePapa, r, 0, 1, 3)

def __init__(self, mw):
    qc = self.mw.col.conf
    cb=qc.get("hoochiePapa", 0)
    self.form.hoochiePapa.setCheckState(cb)

def accept(self):
    qc = self.mw.col.conf
    qc['hoochiePapa']=self.form.hoochiePapa.checkState()

def toggle(self):
    checked=not self.hoochiePapa.checkState()==0
    if checked:
        try:
            self.serenityNow.setCheckState(0)
        except: pass

aqt.forms.preferences.Ui_Preferences.setupUi = wrap(aqt.forms.preferences.Ui_Preferences.setupUi, setupUi, "after")
aqt.preferences.Preferences.__init__ = wrap(aqt.preferences.Preferences.__init__, __init__, "after")
aqt.preferences.Preferences.accept = wrap(aqt.preferences.Preferences.accept, accept, "before")
