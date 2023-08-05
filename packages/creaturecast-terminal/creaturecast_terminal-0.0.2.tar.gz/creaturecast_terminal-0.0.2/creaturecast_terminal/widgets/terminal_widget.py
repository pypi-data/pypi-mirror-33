
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *

import creaturecast_terminal.widgets.python_text_edit as pte

class TerminalWidget(QFrame):

    accepted = Signal(str)
    execute = Signal(str)
    text_changed = Signal(str)

    def __init__(self, *args, **kwargs):
        super(TerminalWidget, self).__init__(*args, **kwargs)


        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(1, 1, 1, 1)

        bottom_layout = QHBoxLayout()

        self.pythonTextEdit = pte.PythonTextEdit(self)


        self.execute_button = QPushButton('Execute', parent=self)
        self.cancelButton = QPushButton('Close', parent=self)
        self.cancelButton.setVisible(False)

        self.layout.addWidget(self.pythonTextEdit)
        self.layout.addWidget(self.execute_button)
        self.layout.addWidget(self.cancelButton)

        self.execute_button.pressed.connect(self.execute)
        self.cancelButton.pressed.connect(self.close)
        self.pythonTextEdit.textChanged.connect(self.emit_text_changed)

        self.resize(700, 200)

    def emit_text_changed(self):
        self.text_changed.emit(self.pythonTextEdit.toPlainText())

    def emit_accepted(self):
        self.accepted.emit(self.pythonTextEdit.toPlainText())

    def execute(self):
        text = self.pythonTextEdit.toPlainText()
        print text
        exec(text)

    '''
    def keyPressEvent(self, e):
        #print type(e), e.text()
        super(ScriptEditor, self).keyPressEvent(e)

        if ((e.modifiers() & Qt.ControlModifier) and e.key()==Qt.Key_Return):
            self.pythonTextEdit.emitCode()
            return
    '''