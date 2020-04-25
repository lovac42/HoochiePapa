# -*- coding: utf-8 -*-
# Copyright: (C) 2020 Lovac42
# Support: https://github.com/lovac42/HoochiePapa
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html


from aqt import mw
from aqt.utils import tooltip

from .const import ADDON_NAME
from .config import Config
from .lib.com.lovac42.anki.backend.utils import isSorted
from .lib.com.lovac42.anki.version import ANKI20

if ANKI20:
    range = xrange


class Tests:
    conf = Config(ADDON_NAME)

    def __init__(self):
        self.reset()

    def reset(self):
        self.state = -1

    def _isReview(self):
        if mw.state == "review":
            tooltip("Papa can't run self-tests during review.", period=1200)
            return True

    def _selectDeck(self, did=1):
        old_did = mw.col.decks.selected()
        mw.col.decks.select(did)
        # act = mw.col.decks.active()[:]
        mw.col.sched._newDids = [did]
        return old_did

    def _restoreDeck(self, did):
        mw.col.decks.select(did)
        mw.col.sched._resetNew()

    def _setupTestCounts(self):
        mw.col.sched.newCount = 20
        mw.col.sched.revCount = 20
        mw.col.sched.lrnCount = 20
        mw.col.sched._newQueue = []


    def testWrap(self, checkbox):
        "This tests for addon conflict, to make sure HoochiePapa was wrapped correctly."
        if not self.conf.get("run_self_test_wrap", True) or self._isReview():
            return

        self.reset()
        self._setupTestCounts()
        old_did = self._selectDeck(1)
        try:
            mw.col.sched._fillNew()
        finally:
            self._restoreDeck(old_did)

        assert checkbox == self.state, "HoochiePapa, self-test failed. Test value was not as expected."

        if checkbox==2:
            tooltip("Papa was wrapped successfully!", period=800)
        elif checkbox==0:
            tooltip("Papa was unwrapped...", period=800)
        else:
            raise ValueError("Checkbox state was not expected.")


    def testSort(self, index):
        if not self.conf.get("run_self_test_sort", False) or self._isReview():
            return
        if index > 11:
            raise ValueError("Index was not expected.")

        expected=0
        old_did = self._selectDeck(1)
        try:
            for i in range(5):
                r = self._testSort(index)
                if r < 0:
                    tooltip("Papa can't run self-tests. Not enough cards in default deck for testing.", period=2000)
                    return
                expected += r
        finally:
            self._restoreDeck(old_did)

        # ensure a pass-rate of 3/5 due to unpredictable randomness.
        assert expected == 5 or (index in (0,11) and expected >= 3), "HoochiePapa, self-test failed. Tested values were not as expected."

        tooltip("Papa sort-test: OK", period=800)


    def _testSort(self, index):
        "This test require some cards put inside the Default anki folder."
        self.reset()
        self._setupTestCounts()

        mw.col.sched._fillNew()
        cids = mw.col.sched._newQueue
        if not cids or len(cids)<10:
            return -1

        arr = []
        for cid in cids:
            card = mw.col.getCard(cid)
            if index in (0,11,1,2):
                arr.append(card.due)
            elif index in (3,4):
                arr.append(card.id)
            elif index in (5,6):
                arr.append(card.mod)
            elif index in (7,8):
                arr.append(card.left)
            elif index in (9,10):
                arr.append(card.factor)
            else:
                raise ValueError("Index was not expected.")

        # print(arr)

        dr = False #desired result
        if index in (1,3,5,7,9):
            dr = isSorted(arr, key=lambda x, y: x >= y)
        elif index in (2,4,6,8,10):
            dr = isSorted(arr, key=lambda x, y: x <= y)
        else: #idx = 0 or 11, test random
            #TODO:
            #  This test does not account for x >= y
            #  caused by addon conflicts.
            not_rand = isSorted(arr, key=lambda x, y: x <= y)
            if not_rand: #not random, test for same due
                dr = isSorted(arr, key=lambda x, y: x == y)
            else:
                dr = True

        if not dr:
            return 0
        return 1




run_tests = Tests()
