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
# from .lib.com.lovac42.anki.gui import muffins


if ANKI21:
    from PyQt5 import QtCore, QtGui, QtWidgets
else:
    from PyQt4 import QtCore, QtGui as QtWidgets


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
    sort_itms = CUSTOM_SORT.iteritems if ANKI20 else CUSTOM_SORT.items
    for i,v in sort_itms():
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




aqt.forms.preferences.Ui_Preferences.setupUi = wrap(
    aqt.forms.preferences.Ui_Preferences.setupUi, setupUi, "after"
)

aqt.preferences.Preferences.__init__ = wrap(
    aqt.preferences.Preferences.__init__, load, "after"
)

aqt.preferences.Preferences.accept = wrap(
    aqt.preferences.Preferences.accept, save, "before"
)
