# -*- coding: utf-8 -*-
# Copyright: (C) 2018-2020 Lovac42
# Support: https://github.com/lovac42/HoochiePapa
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html


import aqt
import aqt.preferences
from aqt.qt import *
from anki.lang import _
from anki.hooks import wrap


from .sort import CUSTOM_SORT
from .lib.com.lovac42.anki.version import ANKI21, ANKI20
from .lib.com.lovac42.anki.gui.checkbox import TristateCheckbox
from .lib.com.lovac42.anki.gui import muffins


if ANKI21:
    from PyQt5 import QtCore, QtGui, QtWidgets
else:
    from PyQt4 import QtCore, QtGui as QtWidgets


def setupUi(self, Preferences):
    grid_layout = muffins.getMuffinsTab(self)
    r = grid_layout.rowCount()

    papa_groupbox = QtWidgets.QGroupBox(self.lrnStage)
    papa_groupbox.setTitle("Hoochie Papa!")
    papa_grid_layout = QtWidgets.QGridLayout(papa_groupbox)
    grid_layout.addWidget(papa_groupbox, r, 0, 1, 3)

    self.hoochiePapa = TristateCheckbox(papa_groupbox)
    self.hoochiePapa.setTristate(False)
    self.hoochiePapa.setDescriptions({
        Qt.Unchecked:        "Hoochie Papa addon has been disabled",
        Qt.PartiallyChecked: "Error, should not have seen this.",
        Qt.Checked:          "Randomize new cards, check subdeck limits",
    })

    papa_grid_layout.addWidget(self.hoochiePapa, r, 0, 1, 3)
    self.hoochiePapa.clicked.connect(lambda:toggle(self))

    r+=1
    self.hoochiePapaSortLbl=QtWidgets.QLabel(papa_groupbox)
    self.hoochiePapaSortLbl.setText(_("      Sort new cards by:"))
    papa_grid_layout.addWidget(self.hoochiePapaSortLbl, r, 0, 1, 1)

    self.hoochiePapaSort = QtWidgets.QComboBox(papa_groupbox)
    sort_itms = CUSTOM_SORT.iteritems if ANKI20 else CUSTOM_SORT.items
    for i,v in sort_itms():
        self.hoochiePapaSort.addItem("")
        self.hoochiePapaSort.setItemText(i, _(v[0]))
    papa_grid_layout.addWidget(self.hoochiePapaSort, r, 1, 1, 3)



def load(self, mw):
    qc = self.mw.col.conf
    cb = qc.get("hoochiePapa", Qt.Unchecked)
    self.form.hoochiePapa.setCheckState(cb)
    idx = qc.get("hoochiePapaSort", 0)
    self.form.hoochiePapaSort.setCurrentIndex(idx)
    toggle(self.form)


def save(self):
    toggle(self.form)
    qc = self.mw.col.conf
    qc['hoochiePapa'] = int(self.form.hoochiePapa.checkState())
    qc['hoochiePapaSort'] = self.form.hoochiePapaSort.currentIndex()


def toggle(self):
    state = self.hoochiePapa.checkState()
    self.hoochiePapaSort.setDisabled(state == Qt.Unchecked)
    self.hoochiePapaSortLbl.setDisabled(state == Qt.Unchecked)



# Wrap crap ######################

aqt.forms.preferences.Ui_Preferences.setupUi = wrap(
    aqt.forms.preferences.Ui_Preferences.setupUi, setupUi, "after"
)

aqt.preferences.Preferences.__init__ = wrap(
    aqt.preferences.Preferences.__init__, load, "after"
)

aqt.preferences.Preferences.accept = wrap(
    aqt.preferences.Preferences.accept, save, "before"
)
