
import os
import os.path
import re

import filters
from filters import NoSuchFilter, FilterError
from core import butils


from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qtauto.ui_filterinstanceeditor import Ui_FilterInstanceEditor

import overlistbuttonwidget



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

        self._icon_remove = QIcon(":/pic/lstbtnremove.png")
        self._icon_add = QIcon(":/pic/lstbtnadd.png")

        self._emitLayoutChanged()


    @pyqtSlot('QString')
    def removeArgument(self, argname):
        argname = str(argname)
        
        print 'remove argument: %r' %(argname)
        
        if (argname in self._kwargs):

            print 'really removing argument!'
            
            del self._kwargs[argname]
            
            row = self.findArgByName(argname)
            idx = self.index(row, 2)
            self._update_optionstring()
            self.dataChanged.emit(idx,idx)
            self._emitOptionStringChanged()


    def rowCount(self, parent):
        if (self._fopts is None):
            return 0
        return len(self._fopts.filteroptions())

    def columnCount(self, parent):
        return 2
    

    def _make_empty_type(self, arg):
        if (arg.argtypename is not None):
            typ = butils.resolve_type(arg.argtypename)
            return typ()
        return str('')
        

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

        arg = filteroptions[row]
        val = self._kwargs.get(arg.argname)
        
        if (col == 1):
            # argument value

            if (role == overlistbuttonwidget.ROLE_OVERBUTTON):
                if (val is not None):
                    return QVariant(overlistbuttonwidget.OVERBUTTON_REMOVE)
                return QVariant(overlistbuttonwidget.OVERBUTTON_ADD)

            if (role == overlistbuttonwidget.ROLE_ARGNAME):
                return QVariant(QString(arg.argname))
            
            if (arg.argname not in self._kwargs):
                # request editing of argument for which we have no value yet
                if (role == Qt.EditRole):
                    editval = self._make_empty_type(arg)
                    return QVariant(editval)
                return QVariant()
            
            if (role == Qt.DisplayRole):
                return QVariant(QString(str(val)))
            if (role == Qt.EditRole):
                if (val is None):
                    return QVariant(self._make_empty_type(arg))
                return QVariant(val)
            return QVariant()

        if (col == 2):
            if (role == Qt.UserRole):
                # this returns the arg name that the button will refer to
                return QVariant(QString(arg.argname))
            if (role == Qt.DecorationRole):
                if (val is not None):
                    return QVariant(self._icon_remove)
                return QVariant(self._icon_add)

            return QVariant()


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

        if (section == 2):
            if (role == Qt.DisplayRole):
                return QVariant(QString(u""))
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
        if (col == 2):
            return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable

        print "DefaultFilterOptionsModel.flags(): BAD COLUMN: %d" %(col)
        return 0
    

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

    def findArgByName(self, argname):
        filteroptions = self._fopts.filteroptions()

        for row in xrange(len(filteroptions)):
            if (filteroptions[row].argname == argname):
                return row

        return None
    

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
                    slist.append('-d'+soptarg+('' if v else '=False'))
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



class DefaultFilterOptionsDelegate(QStyledItemDelegate):
    def __init__(self, parentView=None):
        super(DefaultFilterOptionsDelegate, self).__init__(parentView)
        self._view = parentView


##     removeArgument = pyqtSignal('QString')

##     def createEditor(self, parent, option, index):
##         if (index.column() != 2):
##             return super(DefaultFilterOptionsDelegate, self).createEditor(parent, option, index)

##         icon = index.data(Qt.DecorationRole).toPyObject()

##         if (icon is None):
##             print "Icon is none!!!"
##             icon = QIcon()

##         btn = QToolButton(parent)
##         btn.setProperty('argname', index.data(Qt.UserRole))
##         btn.setIcon(icon)
##         btn.setToolButtonStyle(Qt.ToolButtonIconOnly)
##         btn.clicked.connect(self._btnclicked)
##         return btn

##     def updateEditorGeometry(self, editor, option, index):
##         editor.setGeometry(option.rect)

##     @pyqtSlot()
##     def _btnclicked(self):
##         sender = self.sender()
##         argname = str(sender.property('argname').toString())

##         if (argname):
##             self.removeArgument.emit(QString(argname))

##     @pyqtSlot()
##     def update_buttons(self):
##         zemodel = self._view.model()
##         for k in xrange(zemodel.rowCount(QModelIndex())):
##             self._view.closePersistentEditor(zemodel.index(k,2))
##         for k in xrange(zemodel.rowCount(QModelIndex())):
##             self._view.openPersistentEditor(zemodel.index(k,2))
        



class FilterInstanceEditor(QWidget):
    def __init__(self, parent):
        super(FilterInstanceEditor, self).__init__(parent)

        self.ui = Ui_FilterInstanceEditor()
        self.ui.setupUi(self)
        
        for filtername in filters.__all__:
            self.ui.cbxFilter.addItem(filtername)

        self.filterNameChanged.connect(self.filterInstanceDefinitionChanged)
        self.filterOptionsChanged.connect(self.filterInstanceDefinitionChanged)

        self._is_updating = False

        self._filteroptionsmodel = DefaultFilterOptionsModel(filtername=None, parent=self)

        self._filteroptionsdelegate = DefaultFilterOptionsDelegate(parentView=self.ui.lstOptions)
        
        self.ui.lstOptions.setModel(self._filteroptionsmodel)
        self.ui.lstOptions.setItemDelegate(self._filteroptionsdelegate)

        self._filteroptionsmodel.optionStringChanged.connect(self.filterOptionsChanged)
        ##self._filteroptionsmodel.dataChanged.connect(self._filteroptionsdelegate.update_buttons)

        self._filterargbtn = overlistbuttonwidget.OverListButtonWidget(self.ui.lstOptions)
        self._filterargbtn.removeClicked.connect(self._filteroptionsmodel.removeArgument)
        self._filterargbtn.addIndexClicked.connect(self.ui.lstOptions.edit)

        self._filteroptionsmodel.optionStringChanged.connect(self._filterargbtn.updateDisplay)
        

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
        self.ui.lstOptions.setColumnWidth(2, 20)
        ##self._filteroptionsdelegate.update_buttons()

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

        
