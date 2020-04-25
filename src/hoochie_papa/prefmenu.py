# -*- coding: utf-8 -*-
# Copyright: (C) 2018-2020 Lovac42
# Support: https://github.com/lovac42/HoochiePapa
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html


import aqt
import aqt.preferences
from aqt import mw
from aqt.qt import *
from anki.lang import _
from anki.hooks import wrap

from .sort import CUSTOM_SORT
from .self_test import run_tests
from .lib.com.lovac42.anki.version import ANKI20
from .lib.com.lovac42.anki.gui.checkbox import TristateCheckbox
from .lib.com.lovac42.anki.gui import muffins


loaded = False


def setupUi(self, Preferences):
    global loaded
    loaded = False

    papa_groupbox = muffins.getMuffinsGroupbox(self, "Hoochie Papa!")
    papa_grid_layout = QGridLayout(papa_groupbox)

    r=0
    self.hoochiePapa = TristateCheckbox(papa_groupbox)
    self.hoochiePapa.setTristate(False)
    self.hoochiePapa.setDescriptions({
        Qt.Unchecked:        "Hoochie Papa addon has been disabled",
        Qt.PartiallyChecked: "Error, should not have seen this.",
        Qt.Checked:          "Randomize new cards, check subdeck limits",
    })
    papa_grid_layout.addWidget(self.hoochiePapa, r, 0, 1, 3)
    self.hoochiePapa.clicked.connect(lambda:onClick(self))
    self.hoochiePapa.onClick = onClick

    r+=1
    self.hoochiePapaSortLbl=QLabel(papa_groupbox)
    self.hoochiePapaSortLbl.setText(_("      Sort new cards by:"))
    papa_grid_layout.addWidget(self.hoochiePapaSortLbl, r, 0, 1, 1)

    self.hoochiePapaSort = QComboBox(papa_groupbox)
    sort_itms = CUSTOM_SORT.iteritems if ANKI20 else CUSTOM_SORT.items
    for i,v in sort_itms():
        self.hoochiePapaSort.addItem("")
        self.hoochiePapaSort.setItemText(i, _(v[0]))
    papa_grid_layout.addWidget(self.hoochiePapaSort, r, 1, 1, 3)
    self.hoochiePapaSort.currentIndexChanged.connect(lambda:onChanged(self.hoochiePapaSort))


def load(self, mw):
    global loaded
    qc = self.mw.col.conf
    cb = qc.get("hoochiePapa", Qt.Unchecked)
    self.form.hoochiePapa.setCheckState(cb)
    idx = qc.get("hoochiePapaSort", 0)
    self.form.hoochiePapaSort.setCurrentIndex(idx)
    _updateDisplay(self.form)
    loaded = True


def onClick(form):
    state = int(form.hoochiePapa.checkState())
    mw.col.conf['hoochiePapa'] = state #save
    _updateDisplay(form)
    run_tests.testWrap(state)


def _updateDisplay(form):
    state = form.hoochiePapa.checkState()
    grayout = state == Qt.Unchecked
    form.hoochiePapaSort.setDisabled(grayout)
    form.hoochiePapaSortLbl.setDisabled(grayout)


def onChanged(combobox):
    idx = combobox.currentIndex()
    mw.col.conf['hoochiePapaSort'] = idx
    if loaded:
        run_tests.testSort(idx)


# Wrap crap ######################

# if point version < 23? Use old wrap
# TODO: Find the point version for these new hooks.

aqt.forms.preferences.Ui_Preferences.setupUi = wrap(
    aqt.forms.preferences.Ui_Preferences.setupUi, setupUi, "after"
)

aqt.preferences.Preferences.__init__ = wrap(
    aqt.preferences.Preferences.__init__, load, "after"
)

# aqt.preferences.Preferences.accept = wrap(
    # aqt.preferences.Preferences.accept, save, "before"
# )
