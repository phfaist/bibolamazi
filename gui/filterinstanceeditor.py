
import os
import os.path

import filters


from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qtauto.ui_filterinstanceeditor import Ui_FilterInstanceEditor


class FilterInstanceEditor(QWidget):
    def __init__(self, parent):
        super(FilterInstanceEditor, self).__init__(parent)

        self.ui = Ui_FilterInstanceEditor()
        self.ui.setupUi(self)
        
        QObject.connect(self.ui.lstOptions.model(), SIGNAL('layoutChanged()'), self.update_stuff_moved)

        self.filterNameChanged.connect(self.filterInstanceDefinitionChanged)
        self.filterOptionsChanged.connect(self.filterInstanceDefinitionChanged)

        self._is_updating = False


    filterInstanceDefinitionChanged = pyqtSignal()
    filterNameChanged = pyqtSignal('QString')
    filterOptionsChanged = pyqtSignal('QStringList')

    filterHelpRequested = pyqtSignal('QString')
                        

    def filterName(self):
        return str(self.ui.cbxFilter.currentText())

    def optionList(self):
        return [str(self.ui.lstOptions.item(i).text())  for i in xrange(self.ui.lstOptions.count())]


    @pyqtSlot(QString, bool)
    @pyqtSlot(QString)
    def setFilterName(self, filtername, noemit=False):
        self._is_updating = True
        self.ui.cbxFilter.setEditText(filtername)
        self._is_updating = False
        if (not noemit):
            self.emitFilterNameChanged()
            

    @pyqtSlot(QStringList, bool)
    @pyqtSlot(QStringList)
    def setOptionList(self, optionlist, noemit=False):
        optionlist = [str(x) for x in list(optionlist)];
        
        # don't reset source list if it's the same. In particular, don't emit the changed signal.
        if (optionlist == self.optionList()):
            return
        
        self._is_updating = True
        self.ui.lstOptions.clear()
        for opt in optionlist:
            self.ui.lstSources.addItem(opt)

        self._is_updating = False

        if (not noemit):
            self.emitOptionListChanged()

    @pyqtSlot(bool)
    def setFilterOptionsOn(self, options):
        self.ui.lstOptions.setEnabled(options)
        self.ui.btnAddOption.setEnabled(options)
        self.ui.btnRemoveOption.setEnabled(options)

    def setFilterInstanceDefinition(self, filtername, optionlist, no_options=False, noemit=False):
        self.setFilterName(filtername, noemit=noemit)
        self.setFilterOptionsOn(not no_options)
        if (not no_options):
            self.setOptionList(optionlist, noemit=noemit)

    @pyqtSlot()
    def emitOptionListChanged(self):
        if (self._is_updating):
            return
        print "emitting!"
        self.filterOptionsChanged.emit(QStringList(self.optionList()))


    @pyqtSlot()
    def on_btnAddOptions_clicked(self):
        self.ui.lstOptions.addItem("")
        self.ui.lstOptions.editItem(self.ui.lstOptions.count()-1)
        self.emitOptionListChanged()

    @pyqtSlot()
    def on_btnRemoveOption_clicked(self):
        row = self.ui.lstOptions.currentRow()
        if (row < 0):
            print "No row selected"
            return

        print 'removing row %d' %(row)
        item = self.ui.lstOptions.takeItem(row)
        # ###TODO: FIXME: delete item?!?

        self.emitOptionListChanged()

    @pyqtSlot()
    def update_stuff_moved(self):
        # user moved stuff around
        print "Stuff moved around!"

        self.emitOptionListChanged()

    @pyqtSlot()
    def on_btnFilterHelp_clicked(self):
        self.filterHelpRequested(QString(self.filterName()))

        
