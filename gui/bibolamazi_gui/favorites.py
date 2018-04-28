
# -*- coding: utf-8 -*-

################################################################################
#                                                                              #
#   This file is part of the Bibolamazi Project.                               #
#   Copyright (C) 2014 by Philippe Faist                                       #
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


from html import escape as htmlescape

from collections import namedtuple
import logging

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import bibolamazi.init
from .overlistbuttonwidget import OverListButtonWidgetBase
from .qtauto.ui_favoritesoverbtns import Ui_FavoritesOverBtns

logger = logging.getLogger(__name__)


class FavoriteCmd(object):
    def __init__(self, name, cmd, builtin=False):
        self.name = name
        self.cmd = cmd
        self.builtin = builtin


builtin_cmds = [
    FavoriteCmd(name="fixes (simple)",
                cmd=("""\
filter: fixes -dFixSpaceAfterEscape -dRemoveTypeFromPhd -dRemoveFileField -dEncodeUtf8ToLatex"""),
                builtin=True),
    FavoriteCmd(name="fixes (extensive)",
                cmd=("""\
filter: fixes -dFixSpaceAfterEscape
              -dEncodeUtf8ToLatex
              -dRemoveTypeFromPhd
              -sRemoveFullBraces=title
              -sRemoveFullBracesNotLang=german
              -sProtectNames="Maxwell,Landauer,Neumann,Szilard,Bell,I,II,IV,XIV,C++,Gram,ALPS,Ehrenfest,Pauli,Monte,Carlo,CVX,Finetti,Rényi,R{\\'e}nyi,R{\\'{e}}nyi,Golden-Thompson,QBism,Boltzmann,Birkhoff,Gibbs,Einstein,Podolsky,Rosen,Hamiltonian,Petz,AdS,CFT"
              -dRemoveFileField
              -sRenameLanguage=en:english,French:frenchb,German:german,Deutsch:german
              -dFixMendeleyBugUrls"""),
                builtin=True),
    FavoriteCmd(name="arxiv (for notes & verbose)",
                cmd="filter: arxiv -sMode=eprint -sUnpublishedMode=eprint -dThesesCountAsPublished -dWarnJournalRef",
                builtin=True),
    FavoriteCmd(name="arxiv (for articles & finalizing)",
                cmd="filter: arxiv -sMode=strip -sUnpublishedMode=unpublished-note",
                builtin=True),
    FavoriteCmd(name="url (standard cleanup)",
                cmd="filter: url -dStripAllIfDoiOrArxiv -dStripDoiUrl -dStripArxivUrl -dKeepFirstUrlOnly",
                builtin=True),
    FavoriteCmd(name="orderentries (alphabetically by cite key)",
                cmd="filter: orderentries -sOrder=alphabetical",
                builtin=True),
    ];

class FavoriteCmdsList(QObject):
    def __init__(self, parent):
        super(FavoriteCmdsList,self).__init__(parent)
        self.favlist = [];

    favChanged = pyqtSignal()

    def loadDefaults(self):
        self.favlist[:] = builtin_cmds

    def loadFromSettings(self, settings):
        settings.beginGroup("Favorites")

        self.favlist[:] = builtin_cmds
        
        siz = settings.beginReadArray("custom_favorite_cmds")
        for i in range(siz):
            settings.setArrayIndex(i)
            self.favlist.append(FavoriteCmd(name=self._get_settings_str(settings, "name"),
                                            cmd=self._get_settings_str(settings, "cmd")))
        settings.endArray()

        settings.endGroup()

        self.favChanged.emit()

    def _get_settings_str(self, settings, field):
        val = settings.value(field)
        if val is None:
            return ''
        return str(val)

    def saveToSettings(self, settings):
        settings.beginGroup("Favorites")

        custom_favlist = [x for x in self.favlist if not x.builtin]

        settings.beginWriteArray("custom_favorite_cmds", len(custom_favlist))
        for i in range(len(custom_favlist)):
            fav = custom_favlist[i]
            settings.setArrayIndex(i)
            settings.setValue("name", str(fav.name))
            settings.setValue("cmd", str(fav.cmd))
        settings.endArray()

        settings.endGroup()

    def addFavorite(self, favcmd):
        self.favlist += [favcmd]
        self.favChanged.emit()

    def moveFavorite(self, oldind, newind):
        if oldind == newind:
            return

        if oldind < newind:
            self.favlist[oldind:newind] = self.favlist[oldind+1:newind] + [self.favlist[oldind]]
        else: # oldind > newind
            self.favlist[newind:oldind+1] = [self.favlist[oldind]] + self.favlist[newind:oldind]

        self.favChanged.emit()




ROLE_CMD            = Qt.UserRole + 2014
ROLE_FAV_EDITABLE   = ROLE_CMD + 1
ROLE_FAVCMD_OBJECT  = ROLE_CMD + 2
ROLE_CMD_IS_BUILTIN = ROLE_CMD + 3

class FavoritesModel(QAbstractTableModel):
    def __init__(self, favcmds, parent):
        super(FavoritesModel, self).__init__(parent=parent)
        self._favcmds = favcmds;
        self._favcmds.favChanged.connect(self.modelReset)
        self._edit_mode = False

    def setEditMode(self, editmodeon):
        self._edit_mode = editmodeon;
        self.modelReset.emit()

    def rowCount(self, index=QModelIndex()):
        if index.isValid():
            return 0;
        return len(self._favcmds.favlist);

    def columnCount(self, index=QModelIndex()):
        if index.isValid():
            return 0;
        return 1;


    def flags(self, index):
        if self._edit_mode:
            if not index.isValid():
                return Qt.ItemIsDropEnabled
            flags = (Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsDragEnabled)
            row = index.row()
            if row >= 0 and row < len(self._favcmds.favlist):
                if not self._favcmds.favlist[row].builtin:
                    flags = (flags | Qt.ItemIsEditable)
            return flags
        return (Qt.ItemIsSelectable | Qt.ItemIsEnabled)


    def data(self, index, role=Qt.DisplayRole):

        if not index.isValid():
            return None
        
        col = index.column()
        row = index.row()

        if (row < 0 or row >= len(self._favcmds.favlist)):
            return None

        if role == Qt.BackgroundRole:
            if self._favcmds.favlist[row].builtin:
                return QBrush(QColor(255,255,235))
            else:
                if self._edit_mode:
                    return QBrush(QColor(255,230,230))
                else:
                    return QBrush(QColor(235,255,255))

            return None

        if (role == ROLE_FAV_EDITABLE):
            return self._edit_mode

        if (role == ROLE_CMD):
            return self._favcmds.favlist[row].cmd

        if (role == ROLE_CMD_IS_BUILTIN):
            return self._favcmds.favlist[row].builtin

        if (role == ROLE_FAVCMD_OBJECT):
            return self._favcmds.favlist[row]

        # argument name
        if (role == Qt.DisplayRole):
            return self._favcmds.favlist[row].name

        # editable name
        if (role == Qt.EditRole):
            return self._favcmds.favlist[row].name
        
        # tool-tip documentation
        if (role == Qt.ToolTipRole):
            return self._favcmds.favlist[row].cmd

        return None

    def setData(self, index, value, role=Qt.EditRole):
        if not index.isValid():
            return False
        
        col = index.column()
        row = index.row()

        if (row < 0 or row >= len(self._favcmds.favlist)):
            return False

        self._favcmds.favlist[row].name = str('' if value is None else value)
        self.modelReset.emit()
        return True
        

    def removeFavorite(self, row):
        if (isinstance(row, QModelIndex)):
            row = row.row()
        if row < 0 or row >= len(self._favcmds.favlist):
            return
        del self._favcmds.favlist[row]
        self.modelReset.emit()

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if (orientation == Qt.Vertical):
            return None

        if (section == 0):
            if (role == Qt.DisplayRole):
                return u""
            return None

        if (section == 1):
            if (role == Qt.DisplayRole):
                return u""
            return None

        return None

    def supportedDropActions(self):
        return Qt.MoveAction

    def mimeTypes(self):
        return [ "application/x-bibolamazi-internalmove-favorites" ];

    def mimeData(self, indexes):
        logger.longdebug("indexes=%r", indexes)
        if len(indexes) != 1:
            return None

        mimeData = QMimeData()
        mimeData.setData('application/x-bibolamazi-internalmove-favorites',
                         QByteArray(str('%d' %(indexes[0].row()))))
        logger.longdebug("mimeData=%r", mimeData)
        return mimeData

    def dropMimeData(self, data, action, row, column, parent):
        logger.longdebug(
            "Drop! data=%r (formats=%r), action=%r, row=%r, column=%r, parent=%r (%d,%d)",
            data, list(data.formats()), action, row, column, parent, parent.row(), parent.column()
        )

        if not data.hasFormat('application/x-bibolamazi-internalmove-favorites'):
            return False

        if row < 0 or parent.isValid():
            return False

        oldrow = int(data.data("application/x-bibolamazi-internalmove-favorites"))
        logger.longdebug("oldrow: %r", oldrow)

        self._favcmds.moveFavorite(oldrow, row);
        return True



class FavoritesItemDelegate(QStyledItemDelegate):

    def __init__(self, parent):
        super(FavoritesItemDelegate, self).__init__(parent=parent)

    def paint(self, painter, option, index):

        painter.save()

        options = QStyleOptionViewItem(option)
        self.initStyleOption(options, index)
        options.text = ""

        htmlitem = self._htmlitem(index)

        doc = QTextDocument()
        doc.setHtml(htmlitem)

        style = QApplication.style() if options.widget is None \
            else options.widget.style()
        style.drawControl(QStyle.CE_ItemViewItem, options, painter)

        ctx = QAbstractTextDocumentLayout.PaintContext()

        if option.state & QStyle.State_Selected:
            ctx.palette.setColor(QPalette.Text, option.palette.color(
                                 QPalette.Active, QPalette.HighlightedText))

        textRect = style.subElementRect(QStyle.SE_ItemViewItemText, options)
        painter.translate(textRect.topLeft())
        painter.setClipRect(textRect.translated(-textRect.topLeft()))
        doc.documentLayout().draw(painter, ctx)

        painter.restore()        

    def sizeHint(self, option, index):

        options = QStyleOptionViewItem(option)
        self.initStyleOption(options, index)
        options.text = ""

        htmlitem = self._htmlitem(index, bare=True)

        doc = QTextDocument()
        doc.setHtml(htmlitem)
        doc.setTextWidth(options.rect.width())
        return QSize(doc.idealWidth(), doc.size().height())

    def _htmlitem(self, index, bare=False):

        favcmd = index.data(ROLE_FAVCMD_OBJECT)

        html = (
            "<html><head/><body>"+
            "<p style=\"font-weight:bold; margin: 3px 0px 0px 0px;\">" + htmlescape(favcmd.name) + "</p>"
            )

        html += "<p style=\"font-weight:italic; font-size: 0.9em; color: #808080; margin: 5px 0px 5px 0px;\">"
        if not bare:
            html += htmlescape(favcmd.cmd.strip())
        else:
            html += "&nbsp;"
        html += "</p>"

        html += "</body></html>"

        return html


class FavoritesOverBtns(OverListButtonWidgetBase):
    def __init__(self, itemview):
        super(FavoritesOverBtns, self).__init__(itemview=itemview)

        self.ui = Ui_FavoritesOverBtns()
        self.ui.setupUi(self)
        

    insertCommand = pyqtSignal('QString')

    def show_status(self, idx):
        if not idx.isValid():
            return False

        if idx.data(ROLE_FAV_EDITABLE):
            # edit mode
            self.ui.btnInsert.hide()
            self.ui.btnEndEdit.show()
            self.ui.btnEdit.setVisible(True if not idx.data(ROLE_CMD_IS_BUILTIN) else False)
            self.ui.btnDelete.setVisible(True if not idx.data(ROLE_CMD_IS_BUILTIN) else False)
            return True

        # else: normal, not editable
        self.ui.btnInsert.show()
        self.ui.btnEdit.show()
        self.ui.btnEndEdit.hide()
        self.ui.btnDelete.hide()
        return True

    @pyqtSlot()
    def on_btnInsert_clicked(self):
        curidx = self.curIndex()
        if not curidx.isValid():
            return

        self.insertCommand.emit( "\n" + curidx.data(ROLE_CMD) + "\n" )

    @pyqtSlot()
    def on_btnEdit_clicked(self):
        curidx = self.curIndex()
        if curidx.isValid() and curidx.data(ROLE_FAV_EDITABLE):
            # already in edit mode, initiate edit of item text:
            self.itemView().edit(curidx)
            return

        self.itemView().model().setEditMode(True)
        self.itemView().setCurrentIndex(self.curIndex())
        self.updateDisplay()

    @pyqtSlot()
    def on_btnEndEdit_clicked(self):
        self.itemView().model().setEditMode(False)
        self.updateDisplay()


    @pyqtSlot()
    def on_btnDelete_clicked(self):
        curidx = self.curIndex()
        if curidx.data(ROLE_CMD_IS_BUILTIN):
            QMessageBox.critical(self, "Built-in", "You can't remove a built-in favorite command")
        if QMessageBox.question(self, "Confirm deletion",
                                "Are you sure you want to delete this favorite command?",
                                QMessageBox.Yes|QMessageBox.No,
                                QMessageBox.No) != QMessageBox.Yes:
            return

        curidx.model().removeFavorite(curidx)
        self.updateDisplay()


    def get_widget_rect(self, rect):
        return rect
