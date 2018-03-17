
# -*- coding: utf-8 -*-

################################################################################
#                                                                              #
#   This file is part of the Bibolamazi Project.                               #
#   Copyright (C) 2013 by Philippe Faist                                       #
#   philippe.faist@bluewin.ch                                                  #
#                                                                              #
#   Bibolamazi is free software: you can redistribute it and/or modify         #
#   it under the terms of the GNU General Public License as published by       #
#   the Free Software Foundation, either version 3 of the License, or          #
#   (at your option) any later version.                                        #
#                                                                              #
#   Bibolamazi is distributed in the hope that it will be useful,              #
#   but WITHOUT ANY WARRANTY; without even the implied warranty of             #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the              #
#   GNU General Public License for more details.                               #
#                                                                              #
#   You should have received a copy of the GNU General Public License          #
#   along with Bibolamazi.  If not, see <http://www.gnu.org/licenses/>.        #
#                                                                              #
################################################################################

# Py2/Py3 support
from __future__ import unicode_literals, print_function
from past.builtins import basestring
from future.utils import python_2_unicode_compatible, iteritems
from builtins import range
from builtins import str as unicodestr


import os
import os.path
import re
import logging
import textwrap

import bibolamazi.init
from bibolamazi.core.bibfilter import factory as filters_factory
from bibolamazi.core.bibfilter.factory import NoSuchFilter, NoSuchFilterPackage, FilterError
from bibolamazi.core import butils
from bibolamazi.core.bibfilter.argtypes import EnumArgType, CommaStrList

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


from .qtauto.ui_filterinstanceeditor import Ui_FilterInstanceEditor

from . import overlistbuttonwidget

logger = logging.getLogger(__name__)


def get_filter_list():
    filter_pkg_list = filters_factory.detect_filter_package_listings()
    filter_list = []
    for (fpkg, flist) in filter_pkg_list.items():
        if fpkg == 'bibolamazi.filters':
            # built-in, ignore the filter package prefix.
            filter_list += flist
        else:
            filter_list += [ fpkg+':'+f for f in flist ]
    return filter_list




class RegisteredArgInputType:
    def __init__(self, typ, val):
        self.type_arg_input = typ.type_arg_input
        self.value = val

    def createWidget(self, parent, option):
        if (isinstance(self.type_arg_input, EnumArgType)):
            cbx = QComboBox(parent)
            for val in self.type_arg_input.listofvalues:
                cbx.addItem(val)

            return cbx

        logger.debug("Unknown type: type_arg_input=%r", self.type_arg_input)
        return None

    def setEditorData(self, editor):
        if (isinstance(self.type_arg_input, EnumArgType)):
            for i in range(editor.count()):
                if (str(editor.itemText(i)) == self.value):
                    editor.setCurrentIndex(i)
                    return
            return

        logger.debug("Unknown type: type_arg_input=%r", self.type_arg_input)
        return None

    def valueOf(self, editor):
        if (isinstance(self.type_arg_input, EnumArgType)):
            val = str(editor.itemText(editor.currentIndex()))
            logger.debug("GOT VALUE: %r", val)
            return val

        logger.debug("Unknown type: type_arg_input=%r", self.type_arg_input)
        return None
    


class DefaultFilterOptionsModel(QAbstractTableModel):
    def __init__(self, filtername=None, optionstring=None, parent=None):
        super(DefaultFilterOptionsModel, self).__init__(parent)
        self._filtername = None
        self._fopts = None
        self._optionstring = None
        
        self.setFilterName(filtername)


    optionStringChanged = pyqtSignal(str)


    def optionstring(self):
        return self._optionstring

    @pyqtSlot(str)
    def setFilterName(self, filtername, force=False, noemit=False, reset_optionstring=True):
        filtername = str(filtername)

        if (not force and self._filtername == filtername):
            return
        
        self._filtername = filtername

        self._fopts = None
        try:
            # remember: filter_uses_default_arg_parser() may also raise NoSuchFilter
            if (filtername and filters_factory.filter_uses_default_arg_parser(filtername)):
                self._fopts = filters_factory.DefaultFilterOptions(filtername)
        except (NoSuchFilter,NoSuchFilterPackage,FilterError) as e:
            logger.warning("No such filter, no such filter package or filtererror: %s", str(e))
            pass

        if (reset_optionstring):
            self.setOptionString('', force=True, noemit=noemit)
        else:
            self.setOptionString(self._optionstring, force=True, noemit=noemit)

        if (not noemit):
            # we shan't emit anything anyway for a filter name change.
            pass

    @pyqtSlot(str)
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
            optspec = self._fopts.parse_optionstring_to_optspec(optionstring)
        except (FilterError,ValueError):
            logger.debug('error parsing option string, returning')
            return

        self._optionstring = optionstring

        pargs = optspec['_args']
        if pargs is None:
            pargs = []
        kwargs = optspec['kwargs']

        # NEW IN BIBOLAMAZI v3 : NO. pargs are ONLY given to the *args of the filter, and
        # never distributed to declared arguments as for a python function call. (That was
        # unnatural and confusing behavior.)
        #
        # # treat pargs as arguments to the function. These are usually declared arguments, simply
        # # provided without the key.
        # i = 0
        # argoptlist = self._fopts.filterDeclOptions()
        # while (len(pargs) and i < len(argoptlist)):
        #     # this parg corresponds to a kwarg.
        #     arg = argoptlist[i]
        #     if (arg.argname in kwargs):
        #         logger.warning("argument `%s' already given.", arg.argname)
        #         # don't pass this argument; stop argument parsing.
        #         break
        #     kwargs[arg.argname] = pargs.pop(0) # pop out first value into kwargs
        #     i = i + 1 # next declared argument in argoptlist

        self._pargs = pargs
        self._kwargs = kwargs

        self._emitLayoutChanged()


    @pyqtSlot(str)
    def removeArgument(self, argname):
        argname = str(argname)
        
        logger.debug('remove argument: %r', argname)
        
        if (argname in self._kwargs):

            logger.debug('really removing argument!')
            
            del self._kwargs[argname]
            
            row = self.findArgByName(argname)
            idx = self.index(row, 2)
            self._update_optionstring()
            self.dataChanged.emit(idx,idx)
            self._emitOptionStringChanged()


    def rowCount(self, parent):
        if parent.isValid():
            return 0
        if (self._fopts is None):
            return 0
        return len(self._fopts.filterOptions())

    def columnCount(self, parent):
        if parent.isValid():
            return 0
        return 2
    

    #def _make_empty_type(self, arg):
    #    if (arg.argtypename is not None):
    #        fmodule = filters_factory.get_module(self._filtername, False)
    #        typ = butils.resolve_type(arg.argtypename, fmodule)
    #        return typ()
    #    return str('')
        

    def data(self, index, role=Qt.DisplayRole):
        if (self._fopts is None):
            return None
        
        filteroptions = self._fopts.filterOptions()

        col = index.column()
        row = index.row()

        if (row < 0 or row >= len(filteroptions)):
            return None

        # the argument specification of the current row (_ArgDoc namedtuple instance)
        arg = filteroptions[row]

        if (col == 0):
            # argument name
            if (role == Qt.DisplayRole):
                return str(self._fopts.getSOptNameFromArg(filteroptions[row].argname))

            # tool-tip documentation
            if (role == Qt.ToolTipRole):
                return textwrap.fill(arg.doc, width=80)

            return None

        # the value of the argument of the current row.
        val = self._kwargs.get(arg.argname)
        
        if (col == 1):
            # argument value

            if (role == overlistbuttonwidget.ROLE_OVERBUTTON):
                if (val is not None):
                    return overlistbuttonwidget.OVERBUTTON_REMOVE
                return overlistbuttonwidget.OVERBUTTON_ADD

            if (role == overlistbuttonwidget.ROLE_ARGNAME):
                return str(arg.argname)
            
            if (role == Qt.DisplayRole):
                if (val is None):
                    return None
                return str(val)

            # request editing value of argument
            if (role == Qt.EditRole):
                if (arg.argtypename is not None):
                    fmodule = filters_factory.get_module(self._filtername, False)
                    typ = butils.resolve_type(arg.argtypename, fmodule)
                else:
                    typ = str
                if (hasattr(typ, 'type_arg_input')):
                    editval = RegisteredArgInputType(typ, val)
                elif (issubclass(typ, str) and val is None):
                    editval = typ('')
                elif (issubclass(typ, CommaStrList)):
                    editval = str(val)
                else:
                    editval = typ(val)
                return editval
            return None

        return None


    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if (orientation == Qt.Vertical):
            return None

        if (section == 0):
            if (role == Qt.DisplayRole):
                return str(u"Filter Option")
            return None

        if (section == 1):
            if (role == Qt.DisplayRole):
                return str(u"Value")
            return None

        return None


    def flags(self, index):
        col = index.column()
        row = index.row()

        if (self._fopts is None):
            return Qt.NoItemFlags

        if (col == 0):
            return Qt.ItemIsSelectable | Qt.ItemIsEnabled
        if (col == 1):
            return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable

        logger.debug("DefaultFilterOptionsModel.flags(): BAD COLUMN: %d", col)
        return 0
    

    def setData(self, index, value, role=Qt.EditRole):
        
        col = index.column()
        row = index.row()

        if (col != 1):
            return False

        if (self._fopts is None):
            return False

        if (role != Qt.EditRole):
            return False

        filteroptions = self._fopts.filterOptions()

        if (row < 0 or row >= len(filteroptions)):
            return False

        arg = filteroptions[row]

        logger.debug("Got value: %r", value)

        # validate type
        typ = None
        if (arg.argtypename is not None):
            typ = butils.resolve_type(arg.argtypename, filters_factory.get_module(self._filtername, False))
        if (typ == None):
            typ = str
            
        value = typ(value)

        logger.debug("Got final value: %r ; typ=%r", value, typ)

        self._kwargs[arg.argname] = value

        self._update_optionstring()

        self.dataChanged.emit(index, index)

        self._emitOptionStringChanged()

        logger.debug("_kwargs is %r", self._kwargs)
        return True

    def findArgByName(self, argname):
        filteroptions = self._fopts.filterOptions()

        for row in range(len(filteroptions)):
            if (filteroptions[row].argname == argname):
                return row

        return None
    

    def _update_optionstring(self):
        slist = []
        for arg in self._pargs:
            slist.append(butils.quotearg(arg))
            
        # iterate fopts arguments to preserve that ordering
        done_args = []
        for arg in self._fopts.filterOptions():
            v = self._kwargs.get(arg.argname,None)
            if (v is not None):
                soptarg = self._fopts.getSOptNameFromArg(arg.argname)
                if (arg.argtypename == 'bool'):
                    slist.append('-d'+soptarg+('' if v else '=False'))
                else:
                    slist.append('-s'+soptarg+'='+butils.quotearg(str(v)))
                    
            done_args.append(arg.argname)

        # and add any extra args
        for (k,v) in self._kwargs.items():
            if (k in done_args):
                continue
            slist.append('-s' + k + '=' + butils.quotearg(str(v)))

        self._optionstring = " ".join(slist)

        logger.debug("option string is now %r", self._optionstring)
            

    def _emitOptionStringChanged(self):
        self.optionStringChanged.emit(self._optionstring)

    def _emitLayoutChanged(self):
        self.layoutChanged.emit()



class DefaultFilterOptionsDelegate(QStyledItemDelegate):
    def __init__(self, parentView=None):
        super(DefaultFilterOptionsDelegate, self).__init__(parentView)
        self._view = parentView


    def createEditor(self, parent, option, index):
        if (index.column() != 1):
            return super(DefaultFilterOptionsDelegate, self).createEditor(parent, option, index)
        
        data = index.data(Qt.EditRole)
        if (isinstance(data, RegisteredArgInputType)):
            # do our own processing with some custom widgets.
            rr = data
            w = rr.createWidget(parent, option)
            w.setProperty('_RegisteredArgInputType', data)
            return w
        
        return super(DefaultFilterOptionsDelegate, self).createEditor(parent, option, index)
    
    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)
    
    def setEditorData(self, editor, index):
        rr = editor.property('_RegisteredArgInputType')
        if rr is None:
            return super(DefaultFilterOptionsDelegate, self).setEditorData(editor, index)
        
        rr = rr
        rr.setEditorData(editor) # the value is already contained in the rr object

    def setModelData(self, editor, model, index):
        rr = editor.property('_RegisteredArgInputType')
        if rr is None:
            return super(DefaultFilterOptionsDelegate, self).setModelData(editor, model, index)
        
        rr = rr
        model.setData(index, rr.valueOf(editor))





class FilterInstanceEditor(QWidget):
    def __init__(self, parent):
        super(FilterInstanceEditor, self).__init__(parent)

        self._is_updating = True

        self.ui = Ui_FilterInstanceEditor()
        self.ui.setupUi(self)
        
        for filtername in get_filter_list():
            self.ui.cbxFilter.addItem(filtername)

        self.ui.btnAddFavorite.clicked.connect(self.requestAddToFavorites)

        self.filterNameChanged.connect(self.filterInstanceDefinitionChanged)
        self.filterOptionsChanged.connect(self.filterInstanceDefinitionChanged)

        self._filteroptionsmodel = DefaultFilterOptionsModel(filtername=None, parent=self)

        self._filteroptionsdelegate = DefaultFilterOptionsDelegate(parentView=self.ui.lstOptions)
        
        self.ui.lstOptions.setModel(self._filteroptionsmodel)
        self.ui.lstOptions.setItemDelegate(self._filteroptionsdelegate)

        self._filteroptionsmodel.optionStringChanged.connect(self.filterOptionsChanged)
        ##self._filteroptionsmodel.dataChanged.connect(self._filteroptionsdelegate.update_buttons)

        self._filterargbtn = overlistbuttonwidget.OverListButtonWidget(self.ui.lstOptions)
        self._filterargbtn.removeClicked.connect(self._filteroptionsmodel.removeArgument)
        self._filterargbtn.addIndexClicked.connect(self.ui.lstOptions.edit)
        self._filterargbtn.editIndexClicked.connect(self.ui.lstOptions.edit)

        self._filteroptionsmodel.optionStringChanged.connect(self._filterargbtn.updateDisplay)

        self._is_updating = False
        

    filterInstanceDefinitionChanged = pyqtSignal()
    filterNameChanged = pyqtSignal(str)
    filterOptionsChanged = pyqtSignal(str)

    filterHelpRequested = pyqtSignal(str)

    requestAddToFavorites = pyqtSignal()
    

    def filterName(self):
        return self.ui.cbxFilter.currentText()

    def optionString(self):
        return self._filteroptionsmodel.optionstring()


    @pyqtSlot(str, bool)
    @pyqtSlot(str)
    def setFilterName(self, filtername, noemit=False, force=False, reset_optionstring=True):
        logger.debug("setFilterName(%r)", filtername)
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


    @pyqtSlot(str)
    def setOptionString(self, optionstring, noemit=False, force=False):
        self._filteroptionsmodel.setOptionString(optionstring, force=force, noemit=noemit)
        self.ui.lstOptions.resizeColumnToContents(0)
        self.ui.lstOptions.setColumnWidth(2, 20)
        ##self._filteroptionsdelegate.update_buttons()

    def setFilterInstanceDefinition(self, filtername, optionstring, noemit=False):
        self.setFilterName(filtername, noemit=noemit, force=True, reset_optionstring=True)
        self.setOptionString(optionstring, noemit=noemit)

    @pyqtSlot()
    def emitFilterNameChanged(self):
        if (self._is_updating):
            return
        logger.debug("emitting filterNameChanged! filterName=%s", self.filterName())
        self.filterNameChanged.emit(str(self.filterName()))

    @pyqtSlot(str)
    def on_cbxFilter_editTextChanged(self, s):
        if (self._is_updating):
            return
        self.setFilterName(s, force=True, reset_optionstring=False)


    @pyqtSlot()
    def on_btnFilterHelp_clicked(self):
        self.filterHelpRequested.emit('filters/%s' %(str(self.filterName())))

        
