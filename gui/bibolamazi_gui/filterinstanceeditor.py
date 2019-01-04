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
from future.standard_library import install_aliases
install_aliases()

import os
import os.path
import re
import logging
import textwrap
from collections import OrderedDict
from urllib.parse import urlencode

import bibolamazi.init
from bibolamazi.core.bibfilter import factory as filters_factory
from bibolamazi.core.bibfilter.factory import NoSuchFilter, NoSuchFilterPackage, FilterError
from bibolamazi.core import butils
from bibolamazi.core.bibfilter.argtypes import EnumArgType, MultiTypeArgType, \
    CommaStrList, ColonCommaStrDict, StrEditableArgType

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


from .qtauto.ui_filterinstanceeditor import Ui_FilterInstanceEditor

from . import overlistbuttonwidget
from .helpbrowser import htmlescape
from .multitypeseditor import MultiTypesEditorWidget

logger = logging.getLogger(__name__)



def is_class_and_is_sub_class(x, kl):
    # graceful simple "no" answer if issubclass throws TypeError
    try:
        return issubclass(x, kl)
    except Exception:
        return False



def get_filter_list(filterpath=filters_factory.filterpath):
    logger.debug("filterinstanceeditor.get_filter_list()")
    filter_pkg_list = filters_factory.detect_filter_package_listings(filterpath=filterpath)
    logger.debug("filterinstanceeditor.get_filter_list(): filter_pkg_list=%r", filter_pkg_list)
    filter_list = []
    for (fpkg, flist) in filter_pkg_list.items():
        if fpkg == 'bibolamazi.filters':
            # built-in, ignore the filter package prefix.
            filter_list += [ finfo.filtername for finfo in flist]
        else:
            filter_list += [ fpkg+':'+finfo.filtername for finfo in flist ]
    logger.debug("filterinstanceeditor.get_filter_list(): filter_list=%r", filter_list)
    return filter_list




class RegisteredArgInputType:
    def __init__(self, typ, val):
        self.typ = typ
        self.type_arg_input = typ.type_arg_input
        self.value = val

    def createWidget(self, parent, option=None):
        if isinstance(self.type_arg_input, EnumArgType):
            cbx = QComboBox(parent)
            for val in self.type_arg_input.listofvalues:
                cbx.addItem(val)
            return cbx

        if isinstance(self.type_arg_input, MultiTypeArgType):
            return MultiTypesEditorWidget(self.type_arg_input, parent)

        if isinstance(self.type_arg_input, StrEditableArgType):
            f = QItemEditorFactory()
            return f.createEditor(QVariant.String, parent)

        logger.debug("Unknown type: type_arg_input=%r", self.type_arg_input)
        return None

    def setEditorData(self, editor):
        logger.debug("setEditorData(), self.value=%r", self.value)

        if isinstance(self.type_arg_input, EnumArgType):
            for i in range(editor.count()):
                if (str(editor.itemText(i)) == self.value):
                    editor.setCurrentIndex(i)
                    return
            return

        if isinstance(self.type_arg_input, MultiTypeArgType):
            # self.value is the given value being edited (bool -dXXX or string -sXXX=...)
            if isinstance(self.value, self.typ): # a multi_type_class instance directly
                editor.setTypeValue(self.value.valuetype, self.value.value)
            else:
                editor.setValue(self.value)
            return

        if isinstance(self.type_arg_input, StrEditableArgType):
            editor.setText(str(self.value))

        logger.debug("Unknown type: type_arg_input=%r", self.type_arg_input)
        return None

    def valueOf(self, editor):
        if isinstance(self.type_arg_input, EnumArgType):
            val = str(editor.itemText(editor.currentIndex()))
            logger.debug("GOT VALUE: %r", val)
            return val

        if isinstance(self.type_arg_input, MultiTypeArgType):
            t, v = editor.getTypeValue()
            logger.debug("GOT VALUE: %r, %r", t, v)
            return self.typ(t, v)

        if isinstance(self.type_arg_input, StrEditableArgType):
            return self.typ(editor.text())

        logger.debug("Unknown type: type_arg_input=%r", self.type_arg_input)
        return None
    


class DefaultFilterOptionsModel(QAbstractTableModel):
    def __init__(self, filterpathobj, parent=None):
        super(DefaultFilterOptionsModel, self).__init__(parent)
        self._filterpathobj = filterpathobj
        self._filtername = None
        self._finfo = None
        self._fopts = None
        self._optionstring = None
        self._optionstring_error = None
        self._optionstring_softerror = None


    optionStringChanged = pyqtSignal(str)

    optionStringSetError = pyqtSignal(str)
    optionStringSetSoftError = pyqtSignal(str)
    optionStringClearError = pyqtSignal()


    def optionstring(self):
        return self._optionstring

    def errorString(self):
        return self._optionstring_error

    def softErrorString(self):
        return self._optionstring_softerror


    def filterInfo(self):
        return self._finfo


    @pyqtSlot(str)
    def setFilterName(self, filtername, force=False, noemit=False, reset_optionstring=True):

        logger.debug("[Model]/setFilterName(%r)", filtername)
        logger.debug("path in filterpathobj is %r", self._filterpathobj)

        if filtername is None:
            # not initialized yet.
            return

        filtername = str(filtername)

        if (not force and self._filtername == filtername):
            return
        
        self._filtername = filtername

        self.beginResetModel()
        self._finfo = None
        self._fopts = None
        try:
            # remember: FilterInfo() may also raise NoSuchFilter
            self._finfo = filters_factory.FilterInfo(filtername, filterpath=self._filterpathobj)
            self._fopts = self._finfo.defaultFilterOptions()
        except Exception as e: #(NoSuchFilter,NoSuchFilterPackage,FilterError) as e:
            stre = str(e)
            logger.warning("Cannot inspect filter: %s", stre)
            import traceback
            logger.debug("%s", traceback.format_exc())
            self._optionstring_error = stre
            self.optionStringSetError.emit(stre)
            return
        finally:
            self.endResetModel()

        # self.optionStringClearError will be emitted, if appropriate after
        # successful parsing of option string

        if (reset_optionstring):
            self.setOptionString('', force=True, noemit=noemit)
        else:
            self.setOptionString(self._optionstring, force=True, noemit=noemit)

        #if (not noemit):
        #    # we shan't emit anything anyway for a filter name change.
        #    pass


    @pyqtSlot(str)
    def setOptionString(self, optionstring, force=False, noemit=False):

        if not self._fopts:
            logger.warning("Can't set option string because we can't manage filter options for this filter")
            return None

        optionstring = str(optionstring);

        # don't reset source list if it's the same. In particular, don't emit the changed signal.
        if (not force and optionstring == self._optionstring and self._optionstring_error is None):
            return

        if (self._fopts is None):
            # no managed options
            return

        # parse the options
        try:
            optspec = self._fopts.parse_optionstring_to_optspec(optionstring)
        except Exception as e:
            logger.debug("error parsing option string.")
            errstr = str(e)
            if not errstr:
                errstr = "Unknown error"
            self._optionstring_error = errstr
            # emit regardless of noemit; noemit refers to content changes...
            self.optionStringSetError.emit(errstr)
            return

        if self._optionstring_error is not None:
            # reset any earlier error
            self._optionstring_error = None
            self.optionStringClearError.emit()

        # if the arguments are syntactically valid, but semantically invalid,
        # then display an error string but let the user edit the options anyway
        filter_opts_valid = True
        try:
            (xpargs, xkwargs) = self._finfo.parseOptionStringArgs(optionstring)
            self._finfo.validateOptionStringArgs(xpargs, xkwargs)
        except Exception as e:
            logger.debug("option string is invalid for filter, displaying error")
            errstr = str(e)
            if not errstr:
                errstr = "Invalid option string (unknown error)"
            self._optionstring_softerror = errstr
            # emit regardless of noemit; noemit refers to content changes...
            self.optionStringSetSoftError.emit(errstr)
            # ... but proceed here ...
            filter_opts_valid = False

        if filter_opts_valid and self._optionstring_softerror is not None:
            # reset any earlier soft error
            self._optionstring_softerror = None
            self.optionStringClearError.emit()

        self._optionstring = optionstring

        # optspec from above. Use user-input, not deduced ones with filter's
        # default values, as parseOptionStringArgs() etc. returns!!
        pargs = optspec['_args']
        kwargs = optspec['kwargs']
        if pargs is None:
            pargs = []

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
    


    def argdocForIndex(self, index):
        if not self._fopts:
            return None
        
        filteroptions = self._fopts.filterOptions()
        #col = index.column()
        #if (col < 0 or col >= 2):
        #    return None
        row = index.row()
        if (row < 0 or row >= len(filteroptions)):
            return None
        arg = filteroptions[row]
        return arg.doc
        

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
                if arg.argtypename is not None:
                    typ = butils.resolve_type(arg.argtypename, self._finfo.fmodule)
                else:
                    typ = str
                if hasattr(typ, 'type_arg_input'):
                    editval = RegisteredArgInputType(typ, val)
                elif is_class_and_is_sub_class(typ, str) and val is None:
                    editval = typ('')
                elif typ in [bool, int, float, str]:
                    try:
                        editval = typ(val) # resort to Qt's editor for these types.
                    except Exception:
                        # in case typ(val) generates an exception because val is invalid ...?
                        editval = typ()
                else:
                    editval = str(val) # always resort to string so that something can be edited
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

        if self._fopts:
            filteroptions = self._fopts.filterOptions()
        else:
            filteroptions = []

        if (row < 0 or row >= len(filteroptions)):
            return False

        arg = filteroptions[row]

        logger.debug("Got value: %r", value)

        # validate type
        typ = None
        if (arg.argtypename is not None):
            typ = butils.resolve_type(arg.argtypename, self._finfo.fmodule)
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
        if not self._fopts:
            return None

        filteroptions = self._fopts.filterOptions()

        for row in range(len(filteroptions)):
            if (filteroptions[row].argname == argname):
                return row

        return None
    

    def _update_optionstring(self):
        if not self._fopts:
            return None

        slist = []
        for arg in self._pargs:
            slist.append(butils.quotearg(arg))
            
        # iterate fopts arguments to preserve that ordering
        done_args = []
        for arg in self._fopts.filterOptions():
            v0 = self._kwargs.get(arg.argname,None)

            v = v0
            if hasattr(v0, 'type_arg_input') and hasattr(v0.type_arg_input, 'option_val_repr'):
                v = v0.type_arg_input.option_val_repr(v0)

            logger.debug("formatting options, %r -> %r (-> %r)", arg.argname, v0, v)
            if v is not None:
                soptarg = self._fopts.getSOptNameFromArg(arg.argname)
                if (arg.argtypename == 'bool' or isinstance(v, bool)):
                    slist.append('-d'+soptarg+('' if v else '=False'))
                else:
                    slist.append('-s'+soptarg+'='+butils.quotearg(str(v)))
                    
            done_args.append(arg.argname)

        # and add any extra args
        for (k,v) in self._kwargs.items():
            if (k in done_args):
                continue
            slist.append('-s' + k + '=' + butils.quotearg(str(v)))

        optstring = " ".join(slist)
        if len(optstring) > 80:
            # long option string, so keep each option on a separate line
            indentstr = " "*(len("filter: ") + len(self._filtername) + 1)
            optstring = ("\n" + indentstr).join(slist)

        self._optionstring = optstring

        logger.debug("option string is now %r", self._optionstring)
            

    def _emitOptionStringChanged(self):
        self.optionStringChanged.emit(self._optionstring)

    def _emitLayoutChanged(self):
        self.layoutChanged.emit()



class DefaultFilterOptionsDelegate(QStyledItemDelegate):
    def __init__(self, parentView=None):
        super(DefaultFilterOptionsDelegate, self).__init__(parentView)
        self._view = parentView


    def sizeHint(self, option, index):
        # add vertical spacing
        return super(DefaultFilterOptionsDelegate, self).sizeHint(option, index) + QSize(0,6)

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
        
        rr.setEditorData(editor) # the value is already contained in the rr object

    def setModelData(self, editor, model, index):
        rr = editor.property('_RegisteredArgInputType')
        if rr is None:
            return super(DefaultFilterOptionsDelegate, self).setModelData(editor, model, index)
        
        val = rr.valueOf(editor)

        logger.debug("setModelData(): value is = %r", val)

        model.setData(index, val)




# ------------------------------------------------------------------------------



class FilterInstanceEditor(QWidget):
    def __init__(self, parent):
        super(FilterInstanceEditor, self).__init__(parent)

        self._is_updating = True

        self.ui = Ui_FilterInstanceEditor()
        self.ui.setupUi(self)

        self.filterpath = OrderedDict(filters_factory.filterpath)

        self.ui.btnAddFavorite.clicked.connect(self.requestAddToFavorites)

        self.filterNameChanged.connect(self.filterInstanceDefinitionChanged)
        self.filterOptionsChanged.connect(self.filterInstanceDefinitionChanged)

        self._filteroptionsmodel = DefaultFilterOptionsModel(filterpathobj=self.filterpath,
                                                             parent=self)

        self._filteroptionsdelegate = DefaultFilterOptionsDelegate(parentView=self.ui.lstOptions)
        
        self.ui.lstOptions.setModel(self._filteroptionsmodel)
        self.ui.lstOptions.setItemDelegate(self._filteroptionsdelegate)

        self.ui.lstOptions.selectionModel().currentChanged.connect(self.option_selected)

        self._filteroptionsmodel.optionStringChanged.connect(self.filterOptionsChanged)

        self._filterargbtn = overlistbuttonwidget.OverListButtonWidget(self.ui.lstOptions)
        self._filterargbtn.removeClicked.connect(self._filteroptionsmodel.removeArgument)
        self._filterargbtn.addIndexClicked.connect(self.ui.lstOptions.edit)
        self._filterargbtn.editIndexClicked.connect(self.ui.lstOptions.edit)

        self._filteroptionsmodel.optionStringChanged.connect(self._filterargbtn.updateDisplay)
        self._filteroptionsmodel.optionStringSetError.connect(self.show_optionstring_error)
        self._filteroptionsmodel.optionStringSetSoftError.connect(self.show_optionstring_softerror)
        self._filteroptionsmodel.optionStringClearError.connect(self.clear_optionstring_error)

        self._is_updating = False

        self.clear_optionstring_error()
        

    filterInstanceDefinitionChanged = pyqtSignal()
    filterNameChanged = pyqtSignal(str)
    filterOptionsChanged = pyqtSignal(str)

    filterHelpRequested = pyqtSignal(str)

    requestAddToFavorites = pyqtSignal()
    

    def filterName(self):
        return self.ui.lblFilterName.text()

    def optionString(self):
        return self._filteroptionsmodel.optionstring()

    def errorString(self):
        return self._filteroptionsmodel.errorString()

    def softErrorString(self):
        return self._filteroptionsmodel.softErrorString()

    @pyqtSlot(str, bool)
    @pyqtSlot(str)
    def setFilterName(self, filtername, noemit=False, force=False, reset_optionstring=True):

        logger.debug("setFilterName(%r)", filtername)
        
        if (not force and self.ui.lblFilterName.text() == filtername):
            return
        
        self._is_updating = True
        self.ui.lblFilterName.setText(filtername) #cbxFilter.setEditText(filtername)
        self._is_updating = False

        self._filteroptionsmodel.setFilterName(filtername, noemit=True,
                                               reset_optionstring=reset_optionstring)

        self.ui.lstOptions.resizeColumnToContents(0)
        
        if (not noemit):
            self.emitFilterNameChanged()

        logger.debug("setFilterName(%r) done.", filtername)


    @pyqtSlot(str)
    def setOptionString(self, optionstring, noemit=False, force=False):
        logger.debug("setOptionString(%r)", optionstring)
        self._filteroptionsmodel.setOptionString(optionstring, force=force, noemit=noemit)
        self.option_selected(self.ui.lstOptions.selectionModel().currentIndex())
        #self.ui.lstOptions.resizeColumnToContents(0)
        #self.ui.lstOptions.setColumnWidth(0, self.ui.lstOptions.width()/3)
        #self.ui.lstOptions.setColumnWidth(1, 100)
        ##self._filteroptionsdelegate.update_buttons()
        logger.debug("setOptionString() done")

    def setFilterPath(self, filterpath):
        # do not allocate new object for self.filterpath, it is referenced by
        # other objects that depend on it
        self.filterpath.clear()
        self.filterpath.update(filterpath)

    def setFilterInstanceDefinition(self, filtername, optionstring, noemit=False):
        logger.debug("setFilterInstanceDefinition(filtername=%r, optionstring=%r, noemit=%r)",
                     filtername, optionstring, noemit)
        self.setFilterName(filtername, noemit=noemit, force=True, reset_optionstring=True)
        self.setOptionString(optionstring, noemit=noemit)


    @pyqtSlot(str)
    def show_optionstring_error(self, errstr):
        self.ui.lblErrorMsg.setText("Error: " + errstr)
        self.ui.lblErrorMsg.setVisible(True)
        self.ui.lstOptions.setEnabled(False)

    @pyqtSlot(str)
    def show_optionstring_softerror(self, errstr):
        self.ui.lblErrorMsg.setText("Invalid options: " + errstr)
        self.ui.lblErrorMsg.setVisible(True)

    @pyqtSlot()
    def clear_optionstring_error(self):
        self.ui.lblErrorMsg.setVisible(False)
        self.ui.lstOptions.setEnabled(True)
        
    @pyqtSlot()
    def emitFilterNameChanged(self):
        if (self._is_updating):
            return
        logger.debug("emitting filterNameChanged! filterName=%s", self.filterName())
        self.filterNameChanged.emit(str(self.filterName()))


    def showEvent(self, event):

        self.ui.lstOptions.setColumnWidth(0, self.ui.lstOptions.width()/3)

        return super(FilterInstanceEditor, self).showEvent(event)

    
    @pyqtSlot('QModelIndex', 'QModelIndex')
    def option_selected(self, currentindex, previousindex=None):
        doc = self._filteroptionsmodel.argdocForIndex(currentindex)
        if doc:
            doc = ("<p>" + htmlescape(doc) +
                   " <a style=\"text-decoration:none\" href=\"action:/help\">" +
                   "more\N{HORIZONTAL ELLIPSIS}</a></p>")
            self.ui.lblOptionHelp.setText(doc)
            self.ui.lblOptionHelp.setVisible(True)
        else:
            self.ui.lblOptionHelp.setVisible(False)


    def on_lblOptionHelp_linkActivated(self, link):
        if link == 'action:/help':
            self.request_filter_help()
        else:
            logger.warning("Invalid link action in filter instance: %r", link)

    @pyqtSlot()
    def on_btnFilterHelp_clicked(self):
        self.request_filter_help()

    def request_filter_help(self):
        finfo = self._filteroptionsmodel.filterInfo()

        if finfo is None:
            logger.warning("request_filter_help: No filter information available.")
            return
        
        url = 'help:/filters/%s' % ( str(finfo.filtername) )
        qs = dict(filterpackage=finfo.filterpackagespec)
        url += '?'+urlencode(qs)
        logger.debug("Filter help: requesting topic URL %s", url)
        self.filterHelpRequested.emit(url)

        
