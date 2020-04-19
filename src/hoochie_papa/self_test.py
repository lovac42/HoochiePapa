# -*- coding: utf-8 -*-
# Copyright: (C) 2020 Lovac42
# Support: https://github.com/lovac42/HoochiePapa
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html


from aqt import mw
from aqt.utils import tooltip


FILTERED_DECK = 3


class Tests:
    def __init__(self):
        self.reset(None)

    def reset(self, old):
        self.old = old
        self.state = -1

    def testWrap(self, state):
        if mw.state != "review":
            tooltip("Papa can't run self-tests, you are not in the reviewer.", period=1200)
        elif not mw.col.sched.newCount:
            tooltip("Papa can't run self-tests, you don't have enough new cards.", period=1200)
        elif self.old:

            from .hoochiePapa import fillNew

            # Clears queue from blocking test. But
            # this must be reset to avoid
            # double loading of the same card.
            mw.col.sched._newQueue = []
            try:
                fillNew(mw.col.sched, self.old)
            finally:
                mw.reset()

            assert state == self.state or self.state == FILTERED_DECK, "\
HoochiePapa, self-test failed. Test value was not as expected."

            if self.state==FILTERED_DECK:
                tooltip("Papa doesn't work with filtered decks.", period=1200)
            elif state:
                tooltip("Papa is wrapped successfully!", period=800)
            else:
                tooltip("Papa is unwrapped...", period=800)


run_tests = Tests()
