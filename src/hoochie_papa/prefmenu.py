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
from .lib.com.lovac42.anki.version import ANKI20
from .lib.com.lovac42.anki.gui.checkbox import TristateCheckbox
from .lib.com.lovac42.anki.gui import muffins


def setupUi(self, Preferences):
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

    r+=1
    footnote_label = QLabel(papa_groupbox)
    footnote_label.setText(_("&nbsp;&nbsp;&nbsp;<i>* If there is anything you don't understand, GIYF.</i>"))
    papa_grid_layout.addWidget(footnote_label, r, 0, 1, 3)


def load(self, mw):
    qc = self.mw.col.conf
    cb = qc.get("hoochiePapa", Qt.Unchecked)
    self.form.hoochiePapa.setCheckState(cb)
    idx = qc.get("hoochiePapaSort", 0)
    self.form.hoochiePapaSort.setCurrentIndex(idx)
    onClick(self.form)


def save(self):
    onClick(self.form)
    qc = self.mw.col.conf
    qc['hoochiePapa'] = int(self.form.hoochiePapa.checkState())
    qc['hoochiePapaSort'] = self.form.hoochiePapaSort.currentIndex()


def onClick(form):
    state = form.hoochiePapa.checkState()
    grayout = state == Qt.Unchecked
    form.hoochiePapaSort.setDisabled(grayout)
    form.hoochiePapaSortLbl.setDisabled(grayout)



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
