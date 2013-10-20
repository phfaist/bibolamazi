
import os
import os.path
import re

import filters
from filters import NoSuchFilter, FilterError
from core import butils


from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qtauto.ui_filterinstanceeditor import Ui_FilterInstanceEditor



class DefaultFilterOptionsModel(QAbstractTableModel):
    def __init__(self, filtername=None, optionstring=None, parent=None):
        super(DefaultFilterOptionsModel, self).__init__(parent)
        self._filtername = None
        self._fopts = None
        self._optionstring = None
        
        self.setFilterName(filtername)


    optionStringChanged = pyqtSignal('QString')


    def optionstring(self):
        return self._optionstring


    @pyqtSlot(QString)
    def setFilterName(self, filtername, force=False, noemit=False, reset_optionstring=True):
        filtername = str(filtername)

        if (not force and self._filtername == filtername):
            return
        
        self._filtername = filtername

        self._fopts = None
        try:
            # remember: filter_uses_default_arg_parser() may also raise NoSuchFilter
            if (filtername and filters.filter_uses_default_arg_parser(filtername)):
                self._fopts = filters.DefaultFilterOptions(filtername)
        except (NoSuchFilter,FilterError) as e:
            print "No such filter or filtererror: %s"%(unicode(e))
            pass

        if (reset_optionstring):
            self.setOptionString('', force=True, noemit=noemit)
        else:
            self.setOptionString(self._optionstring, force=True, noemit=noemit)

        if (not noemit):
            # we shan't emit anything anyway for a filter name change.
            pass

    @pyqtSlot(QString)
    def setOptionString(self, optionstring, force=False, noemit=False):
        optionstring = str(optionstring);

        # don't reset source list if it's the same. In particular, don't emit the changed signal.
        if (not force and optionstring == self._optionstring):
            return

        if (self._fopts is None):
            # no managed options
            return

        # parse the options
        try:
            (pargs, kwargs) = self._fopts.parse_optionstring(optionstring)
        except FilterError:
            self.ui.lstOptions.setEnabled(False)
            return

        self._optionstring = optionstring

        self._pargs = pargs
        self._kwargs = kwargs

        self._emitLayoutChanged()


    def rowCount(self, parent):
        if (self._fopts is None):
            return 0
        return len(self._fopts.filteroptions())

    def columnCount(self, parent):
        return 2
    
    def data(self, index, role=Qt.DisplayRole):
        if (self._fopts is None):
            return QVariant()
        
        filteroptions = self._fopts.filteroptions()

        col = index.column()
        row = index.row()

        if (row < 0 or row >= len(filteroptions)):
            return QVariant()

        if (col == 0):
            # argument name
            if (role == Qt.DisplayRole):
                return QVariant(QString(self._fopts.getSOptNameFromArg(filteroptions[row].argname)))
            return QVariant()

        if (col == 1):
            # argument value
            arg = filteroptions[row]

            val = self._kwargs.get(arg.argname)
            
            if (arg.argname not in self._kwargs):
                return QVariant()
            if (role == Qt.DisplayRole):
                return QVariant(QString(str(val)))
            if (role == Qt.EditRole):
                return QVariant(val)
            return QVariant()

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if (orientation == Qt.Vertical):
            return QVariant()

        if (section == 0):
            if (role == Qt.DisplayRole):
                return QVariant(QString(u"Filter Option"))
            return QVariant()

        if (section == 1):
            if (role == Qt.DisplayRole):
                return QVariant(QString(u"Value"))
            return QVariant()

        return QVariant()


    def flags(self, index):
        col = index.column()
        row = index.row()

        if (self._fopts is None):
            return Qt.NoItemFlags

        if (col == 0):
            return Qt.ItemIsSelectable | Qt.ItemIsEnabled
        if (col == 1):
            return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable


    def setData(self, index, value, role=Qt.EditRole):
        
        col = index.column()
        row = index.row()

        if (col != 1):
            return False

        if (self._fopts is None):
            return False

        filteroptions = self._fopts.filteroptions()

        if (row < 0 or row >= len(filteroptions)):
            return False

        arg = filteroptions[row]

        value = value.toPyObject()

        # validate type
        if (arg.argtypename is not None):
            typ = butils.resolve_type(arg.argtypename)
            value = typ(value)
        else:
            # by default, type is a string.
            value = str(value)

        self._kwargs[arg.argname] = value

        self._update_optionstring()

        self.dataChanged.emit(index, index)

        self._emitOptionStringChanged()

        print '%r' %(self._kwargs)
        return True


    def _update_optionstring(self):
        slist = []
        for arg in self._pargs:
            slist.append(butils.quotearg(arg))
            
        # iterate fopts arguments to preserve that ordering
        done_args = []
        for arg in self._fopts.filteroptions():
            v = self._kwargs.get(arg.argname,None)
            if (v is not None):
                soptarg = self._fopts.getSOptNameFromArg(arg.argname)
                if (arg.argtypename == 'bool'):
                    slist.append('-d'+soptarg+('' if v else '=0'))
                else:
                    slist.append('-s'+soptarg+'='+butils.quotearg(str(v)))
                    
            done_args.append(arg.argname)

        # and add any extra args
        for (k,v) in self._kwargs.iteritems():
            if (k in done_args):
                continue
            slist.append('--' + k + '=' + butils.quotearg(str(v)))

        self._optionstring = " ".join(slist)

        print "option string is now %r" %(self._optionstring)
            

    def _emitOptionStringChanged(self):
        self.optionStringChanged.emit(self._optionstring)

    def _emitLayoutChanged(self):
        self.layoutChanged.emit()




class FilterInstanceEditor(QWidget):
    def __init__(self, parent):
        super(FilterInstanceEditor, self).__init__(parent)

        self.ui = Ui_FilterInstanceEditor()
        self.ui.setupUi(self)
        
        self.filterNameChanged.connect(self.filterInstanceDefinitionChanged)
        self.filterOptionsChanged.connect(self.filterInstanceDefinitionChanged)

        self._is_updating = False

        self._filteroptionsmodel = DefaultFilterOptionsModel(filtername=None, parent=self)
        self.ui.lstOptions.setModel(self._filteroptionsmodel)

        self._filteroptionsmodel.optionStringChanged.connect(self.filterOptionsChanged)



    filterInstanceDefinitionChanged = pyqtSignal()
    filterNameChanged = pyqtSignal('QString')
    filterOptionsChanged = pyqtSignal('QString')

    filterHelpRequested = pyqtSignal('QString')
                        

    def filterName(self):
        return str(self.ui.cbxFilter.currentText())

    def optionString(self):
        return self._filteroptionsmodel.optionstring()


    @pyqtSlot(QString, bool)
    @pyqtSlot(QString)
    def setFilterName(self, filtername, noemit=False, force=False, reset_optionstring=True):
        print "setFilterName(%r)"%(filtername)
        if (not force and self.ui.cbxFilter.currentText() == filtername):
            return
        
        self._is_updating = True
        self.ui.cbxFilter.setEditText(filtername)
        self._is_updating = False

        self._filteroptionsmodel.setFilterName(filtername, noemit=True,
                                               reset_optionstring=reset_optionstring)

        self.ui.lstOptions.resizeColumnToContents(0)
        
        if (not noemit):
            self.emitFilterNameChanged()


    @pyqtSlot(QString)
    def setOptionString(self, optionstring, noemit=False, force=False):
        self._filteroptionsmodel.setOptionString(optionstring, force=force, noemit=noemit)
        self.ui.lstOptions.resizeColumnToContents(0)

    def setFilterInstanceDefinition(self, filtername, optionstring, noemit=False):
        self.setFilterName(filtername, noemit=noemit, force=True, reset_optionstring=False)
        self.setOptionString(optionstring, noemit=noemit)

    @pyqtSlot()
    def emitFilterNameChanged(self):
        if (self._is_updating):
            return
        print "emitting!"
        self.filterNameChanged.emit(QString(self.filterName()))

    @pyqtSlot(QString)
    def on_cbxFilter_editTextChanged(self, s):
        if (self._is_updating):
            return
        self.setFilterName(s, force=True, reset_optionstring=False)


    @pyqtSlot()
    def on_btnFilterHelp_clicked(self):
        self.filterHelpRequested.emit('filters/%s' %(QString(self.filterName())))

        
