# -*- coding: utf-8 -*-
# Copyright: (C) 2020 Lovac42
# Support: https://github.com/lovac42/HoochiePapa
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html


from aqt import mw
from aqt.utils import tooltip


FILTERED_DECK = 3


class Tests:
    def __init__(self):
        self.reset()

    def reset(self):
        self.state = -1

    def testWrap(self, checkbox):
        if mw.state != "review":
            tooltip("Papa can't run self-tests, you are not in the reviewer.", period=1200)
        elif not mw.col.sched.newCount:
            tooltip("Papa can't run self-tests, you don't have enough new cards.", period=1200)
        else:
            self.reset()
            # Clears queue from blocking test. But
            # this must be reset to avoid
            # double loading of the same card.
            mw.col.sched.newCount = 20
            mw.col.sched._newQueue = []
            try:
                mw.col.sched._fillNew()
            finally:
                mw.reset()

            if self.state==FILTERED_DECK:
                tooltip("Papa doesn't work with filtered decks.", period=1200)
                return

            assert checkbox == self.state, "\
HoochiePapa, self-test failed. Test value was not as expected."

            if checkbox:
                tooltip("Papa was wrapped successfully!", period=800)
            else:
                tooltip("Papa was unwrapped...", period=800)


run_tests = Tests()
