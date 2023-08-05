
import json
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
import creaturecast_terminal.widgets.syntax_hilighter as phl

class TextEdit(QTextEdit):
    def __init__(self,parent=None):
        super(TextEdit,self).__init__(parent)
        self.setFont(QFont('courier', 9, True))


        self.wrap = False

    @property
    def wrap(self):
        option=self.document().defaultTextOption()
        return not bool(option.wrapMode() == option.NoWrap)

    @wrap.setter
    def wrap(self,value):
        option=self.document().defaultTextOption()
        if value:
            option.setWrapMode(option.WrapAtWordBoundaryOrAnywhere)
        else:
            option.setWrapMode(option.NoWrap)
        self.document().setDefaultTextOption(option)


class ResultsTextEdit(TextEdit):
    def __init__(self, parent=None):
        super(ResultsTextEdit, self).__init__(parent)
        self.setReadOnly(True)
        font=QFont('courier', 9)
        self.setFont(font)
        pal = QPalette()
        bgc = QColor(22,22,22)
        pal.setColor(QPalette.Base, bgc)
        text_color = QColor(211, 211, 211)
        pal.setColor(QPalette.Text, text_color)
        self.setPalette(pal)

defaultCode = '#use the variable "projects" to refer to currently selected items in the project tree'


class PythonTextEdit(TextEdit):

    code = Signal(str)

    def __init__(self, parent=None, code=None):
        super(PythonTextEdit, self).__init__(parent)
        self.completer = None
        self.namespace = globals().copy()
        self.setCompleter(Completer([]))
        if code is None:
            self.document().setPlainText(defaultCode)
        else:
            self.document().setPlainText(code)

        self.highlighter = phl.PythonHighlighter(self.document())
        self.cursorPositionChanged.connect(self.highlightCurrentLine)


    def emitCode(self):
        self.code.emit(self.toPlainText())


    def mimeTypes( self ):
        return ['text/plain', 'text/uri-list', 'text/python-code']


    def canInsertFromMimeData(self, mimedata):
        for format in ['text/plain', 'text/uri-list', 'text/python-code']:
            if mimedata.hasFormat(format):
                return True
        return super(PythonTextEdit, self).canInsertFromMimeData(mimedata)

    def dragMoveEvent(self, event):
        mimeData = event.mimeData()
        mimeData.setData('text/python-code', mimeData.data('text/plain'))
        super(PythonTextEdit, self).dragMoveEvent(event)

    def insertFromMimeData(self, mimeData):
        if mimeData.hasFormat('text/uri-list'):
            urls = mimeData.urls()
            firstPath = str(urls[0].path())[1:]
            if firstPath.endswith('.py'):
                with open(firstPath, mode='r') as f:
                    self.document().setPlainText(f.read())
                    return True
            if firstPath.endswith('.json'):
                with open(firstPath, mode='r') as f:
                    data = json.loads(f.read())
                    if 'code' in data:
                        self.document().setPlainText(data['code'])
                    return True
        super(PythonTextEdit, self).insertFromMimeData(mimeData)

    def highlightCurrentLine(self):
        #Create a selection region that shows the current line
        #Taken from the codeeditor.cpp exampl(
        selection = QTextEdit.ExtraSelection()
        lineColor = QColor(99, 99, 99)

        selection.format.setBackground(lineColor)
        selection.format.setProperty(QTextFormat.FullWidthSelection, True)
        selection.cursor = self.textCursor()
        selection.cursor.clearSelection()
        self.setExtraSelections([selection])


    def loadUserCache(self):
        if self.descriptor:
            userCode = self.user.loadSettings(self.descriptor)
            if userCode:
                self.document().setPlainText(userCode)
            else:
                self.document().setPlainText(defaultCode)


    def saveUserCache(self):
        self.user.saveSettings(self.descriptor, self.document().toPlainText())

    def createStandardContextMenu(self):
        menu = super(TextEdit, self).createStandardContextMenu()
        menu.addAction("Execute Code", self.executeContents)
        menu.addAction("Execute Selected", self.executeSelected)
        return menu

    def contextMenuEvent(self, event):
        menu = self.createStandardContextMenu()
        menu.exec_(self.mapToGlobal(event.pos()))

    def setCompleter(self,completer):
        if self.completer:
            self.disconnect(self.completer, 0, 0)
        self.completer=completer
        if (not self.completer):
            return
        self.completer.setWidget(self)
        self.completer.setCompletionMode(QCompleter.PopupCompletion)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.connect(self.completer, SIGNAL('activated(QString)'), self.insertCompletion)

    def completer(self):
        return self.completer

    def insertCompletion(self,string):
        tc=self.textCursor()
        tc.movePosition(QTextCursor.StartOfWord,QTextCursor.KeepAnchor)
        tc.insertText(string)
        self.setTextCursor(tc)

    def textUnderCursor(self):
        tc=self.textCursor()
        tc.select(QTextCursor.WordUnderCursor)
        return tc.selectedText()

    def keyPressEvent(self, e):
        #print type(e), e.text()

        if (self.completer and self.completer.popup().isVisible()):
            if e.key() in (Qt.Key_Enter, Qt.Key_Return, Qt.Key_Escape, Qt.Key_Tab, Qt.Key_Backtab):
                e.ignore()
                return
        isShortcut=((e.modifiers() & Qt.ControlModifier) and e.key() == Qt.Key_E)
        if not self.completer or not isShortcut:
            super(TextEdit, self).keyPressEvent(e)

        ctrlOrShift = e.modifiers() & (Qt.ControlModifier | Qt.ShiftModifier)
        if (not self.completer or (ctrlOrShift
                                   and not e.text())):
            return

        eow= str("~!@#$%^&*()_+{}|:\"<>?,./;'[]\\-=")
        hasModifier = (e.modifiers() != Qt.NoModifier) and not ctrlOrShift
        completionPrefix = self.textUnderCursor()

        if (not isShortcut
            and (hasModifier
                 or not e.text()
                 or len(completionPrefix) < 2
                 or e.text()[-1] in eow)):
            self.completer.popup().hide()
            return

        itemList = self.namespace.keys()
        self.completer.update([k for k in itemList if completionPrefix in k])
        self.completer.popup().setCurrentIndex(self.completer.completionModel().index(0, 0))

        cr = self.cursorRect()
        cr.setWidth(self.completer.popup().sizeHintForColumn(0)
                    + self.completer.popup().verticalScrollBar().sizeHint().width())
        self.completer.complete(cr)

    def setCode(self, code):
        self.document().setPlainText(code)



class Completer(QCompleter):
    def __init__(self,stringlist,parent=None):
        super(Completer,self).__init__(parent)
        self.stringlist=stringlist
        self.setModel(QStringListModel(self.stringlist))


    def update(self,completionText):
        #filtered=self.stringlist.filter(completionText,Qt.CaseInsensitive)
        self.model().setStringList(completionText)
        self.popup().setCurrentIndex(self.model().index(0, 0))