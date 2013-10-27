
from PyQt4.QtCore import *
from PyQt4.QtGui import *


from qtauto.ui_overlistbuttonwidget import Ui_OverListButtonWidget


ROLE_OVERBUTTON = Qt.UserRole + 137

OVERBUTTON_NONE = 0
OVERBUTTON_ADD = 1
OVERBUTTON_REMOVE = 2

ROLE_ARGNAME = Qt.UserRole + 138


class OverListButtonWidget(QWidget):
    def __init__(self, itemview):
        super(OverListButtonWidget, self).__init__(itemview.viewport())
        self.hide()

        self.ui = Ui_OverListButtonWidget()
        self.ui.setupUi(self)

        self._view = itemview
        self._view.viewport().setMouseTracking(True)
        self._view.viewport().installEventFilter(self)

        self._lastpos = None

        #self._timer = QTimer(self)
        #self._timer.setInterval(100)
        #self._timer.setSingleShot(True)
        #self._timer.timeout.connect(self.repaint)
        

    addClicked = pyqtSignal('QString')
    editClicked = pyqtSignal('QModelIndex')
    removeClicked = pyqtSignal('QString')
    addIndexClicked = pyqtSignal('QModelIndex')
    editIndexClicked = pyqtSignal('QModelIndex')
    removeIndexClicked = pyqtSignal('QModelIndex')
    

    def eventFilter(self, obj, event):

        if (obj == self._view.viewport()):
            if (event.type() == QEvent.FocusOut):
                self.hide()
            if (event.type() == QEvent.MouseMove):
                self.updateDisplay(event.pos())
            if (event.type() == QEvent.Leave):
                self.updateDisplay(False)

        return super(OverListButtonWidget, self).eventFilter(obj, event)

    @pyqtSlot()
    def updateDisplay(self, pos=None):
        if (pos is None):
            pos = self._lastpos
        elif pos is False:
            pos = None
        self._lastpos = pos

        if pos is None:
            self._disappear()
            return
            
        idx = self._view.indexAt(pos)
        if (not idx.isValid()):
            self._disappear()
            return
        v = idx.data(ROLE_OVERBUTTON)
        if (not v.isValid()):
            self._disappear()
            return
        whichbtn = v.toPyObject()

        if (whichbtn == OVERBUTTON_ADD):
            self.ui.btnAdd.show()
            self.ui.btnEdit.hide()
            self.ui.btnRemove.hide()
            self._appear(idx)
            return
        if (whichbtn == OVERBUTTON_REMOVE):
            self.ui.btnAdd.hide()
            self.ui.btnEdit.show()
            self.ui.btnRemove.show()
            self._appear(idx)
            return

        self._disappear()
        return

    def _disappear(self):
        self._curidx = None
        self.hide()

    def _appear(self, idx):
        self.show()
        rect = self._view.visualRect(idx)
        sh = self.minimumSizeHint()
        rect.setLeft(rect.right()-sh.width())
        self.setGeometry(rect)
        self._curidx = idx #QPersistentModelIndex(idx)
        #self.update()
        #self.repaint()
        #self._timer.start()
        

    @pyqtSlot()
    def on_btnAdd_clicked(self):
        if (self._curidx is None):
            return
        self.addIndexClicked.emit(self._curidx)
        self.addClicked.emit(self._curidx.data(ROLE_ARGNAME).toString())

    @pyqtSlot()
    def on_btnEdit_clicked(self):
        if (self._curidx is None):
            return
        self.editIndexClicked.emit(self._curidx)
        self.editClicked.emit(self._curidx.data(ROLE_ARGNAME).toString())

    @pyqtSlot()
    def on_btnRemove_clicked(self):
        if (self._curidx is None):
            return
        self.removeIndexClicked.emit(self._curidx)
        self.removeClicked.emit(self._curidx.data(ROLE_ARGNAME).toString())


    
        
