from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QLineEdit, QApplication
from PyQt5.QtCore import Qt, QVariantAnimation, QEasingCurve, QVariant, QObject
from PyQt5.QtGui import QPainter, QBrush, QPen, QColor, QFontMetrics
import re

from sortedcontainers import SortedDict

import linecommands


class ClickableLineEdit(QLineEdit):

    def __init__(self, parent=None):
        super().__init__(parent)
        stylesheet = """
                QLineEdit {
                    background-color: transparent;
                    color: white;
                    border-style: none;
                    margin: 0 0 0 0;
                }
                """

        self.parent = parent
        self.setStyleSheet(stylesheet)

        self.highlights = []  # TODO a stack type dtype where you basically have dict blocks that you remove once they've been faded out, where each block is: key(start pos) type text color auxvalue #maybe convert to object

        self.refgroups = []

        self.referenced = []
        self.referring = []
        # TODO why these shits in different forms, one is in just the offset form while one is absolute index bruh wtf

        self.active = False
        self.focused = False
        self.refmode = False

        self.realDisplayTextCache = None
        self.refDisplayTextCache = None

        self.setFocusPolicy(Qt.NoFocus)

        self.numresults = 0  # TODO use in most places where you use get nearest not read only, as this is way easier to store

    clicked = pyqtSignal(object)
    identify = pyqtSignal(object)

    def mousePressEvent(self, event):
        if QApplication.keyboardModifiers() == Qt.ShiftModifier and not self.active:
            self.identify.emit(self)
        else:
            super(ClickableLineEdit, self).mousePressEvent(event)
            self.clicked.emit(self)
        # QLineEdit.mousePressEvent(self, event)

    up = pyqtSignal()
    down = pyqtSignal()
    backspacekey = pyqtSignal()
    deletekey = pyqtSignal()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Backspace:
            self.backspacekey.emit()
            return
        elif event.key() == Qt.Key_Delete:
            self.deletekey.emit()
            return
        super(ClickableLineEdit, self).keyPressEvent(event)

        if (event.key() == Qt.Key_Up):
            self.up.emit()
            return
        elif (event.key() == Qt.Key_Down):
            self.down.emit()
            return

        return

    def realDisplayText(self):
        if self.refmode:
            return self.refToReal()
        else:
            return self.displayText()

    def refToReal(self, displaytext=None):
        if displaytext is None:
            displaytext = self.displayText()
        text = ""
        for s in range(len(self.refgroups)):
            text += (displaytext[self.refgroups[s - 1][2][1]:self.refgroups[s][2][0]] if s > 0 else displaytext[:self.refgroups[s][2][0]]) + self.refgroups[s][1]
        if len(self.refgroups) > 0:
            text += displaytext[self.refgroups[len(self.refgroups) - 1][2][1]:]
        if text == "":
            return displaytext
        else:
            return text

    def refDisplayText(self):
        if self.refmode:
            return self.displayText()
        else:
            return self.realToRef()

    def realToRef(self, displaytext=None):
        if displaytext is None:
            displaytext = self.displayText()
        text = ""
        for s in range(len(self.refgroups)):
            text += (displaytext[self.refgroups[s - 1][3][1]:self.refgroups[s][3][0]] if s > 0 else displaytext[:self.refgroups[s][3][0]]) + self.refgroups[s][0]
        if len(self.refgroups) > 0:
            text += displaytext[self.refgroups[len(self.refgroups) - 1][3][1]:]
        if text == "":
            return displaytext
        else:
            return text

    def focusToggle(self):
        self.animToggle(self.focused)
        if self.focused:
            if len(self.refgroups) > 0:
                self.setText(self.refToReal())
        else:
            if len(self.refgroups) > 0:
                self.setText(self.realToRef())
        self.focused = not self.focused

    def animToggle(self, focusout):
        for highlight in self.highlights:
            if highlight.type == "m1":
                highlight.doAnim(100, focusout)
            elif highlight.type == "m3":
                highlight.doAnim(300, focusout)

    def addRef(self, reference):
        if reference not in self.referenced:
            self.referenced.append(reference)

    def remRef(self, reference):
        if reference in self.referenced:
            self.referenced.remove(reference)

    def addHighlight(self, animstate):
        self.highlights.append(animstate)
        self.paintingActive()
        animstate.updated.connect(self.update)
        if animstate.type == "m22":
            animstate.doAnim(100)

    def findHighlight(self, type=None, initialstart=None, initialwidth=None, initialcolor=None, finalstart=None, finalwidth=None, finalcolor=None):
        for highlight in self.highlights:
            if type is not None and highlight.type != type:
                continue
            if initialstart is not None and abs(highlight.initialstate["start"] - initialstart) > 1:
                print("initialstart", highlight.initialstate["start"], initialstart)
                continue
            if initialwidth is not None and abs(highlight.initialstate["width"] - initialwidth) > 1:
                print("initialwidth", highlight.initialstate["width"], initialwidth)
                continue
            if initialcolor is not None and highlight.initialstate["color"] != initialcolor:
                continue
            if finalstart is not None and abs(highlight.finalstate["start"] - finalstart) > 1:
                print("finalstart", highlight.finalstate["start"], finalstart)
                continue
            if finalwidth is not None and abs(highlight.finalstate["width"] - finalwidth) > 1:
                print("finalwidth", highlight.finalstate["width"], finalwidth)
                continue
            if finalcolor is not None and highlight.finalstate["color"] != finalcolor:
                continue
            return highlight

    def paintEvent(self, event):
        painter = QPainter(self)
        inputcolor = QColor("#1D3A5A")
        outputcolor = QColor("#264965")
        if self.isReadOnly():
            painter.setPen(QPen(outputcolor, 16, Qt.SolidLine))
        else:
            painter.setPen(QPen(inputcolor, 16, Qt.SolidLine))
        painter.drawLine(0, 8, 1000000, 8)  # TODO make this not work retardedly, along with the other paints
        painter.setPen(Qt.transparent)

        for index, highlight in enumerate(self.highlights):

            if highlight.type == "m1":
                painter.setBrush(highlight.currentstate["color"])
                painter.drawRect(-10, -50, 12 + highlight.currentstate["width"], 100)
                self.setTextMargins(highlight.currentstate["width"] - highlight.initialstate["width"], 0, 0, 0)
            elif highlight.type == "m21":
                painter.setBrush(highlight.currentstate["color"])
                final = highlight.currentstate["width"]
                painter.drawRect(highlight.currentstate["start"], -50, final + 4, 100)
            elif highlight.type == "m22":
                painter.setBrush(highlight.currentstate["color"])
                final = highlight.currentstate["width"]
                painter.drawRect(highlight.currentstate["start"], -50, final + 4, 100)
                if highlight.finishedLoopCount() > 0:
                    self.highlights.pop(index)
            elif highlight.type == "m3":
                painter.setBrush(highlight.currentstate["color"])
                final = highlight.currentstate["width"]
                painter.drawRect(highlight.currentstate["start"], -50, final + 4, 100)

        super(ClickableLineEdit, self).paintEvent(event)



class QLineAnimation(QVariantAnimation):
    def __init__(self, line, parent=None):
        super().__init__(parent)
        self.line = line

    def updateCurrentValue(self, value):
        super(QLineAnimation, self).updateCurrentValue(value)
        if not value == 0:
            pass


class AnimState(QObject):
    def __init__(self, type, initialstart, initialwidth, initialcolor, finalstart=None, finalwidth=None, finalcolor=None, currentinitial=True):
        super().__init__()
        self.type = type
        finalstart = initialstart if finalstart is None else finalstart
        finalwidth = initialwidth if finalwidth is None else finalwidth
        finalcolor = initialcolor if finalcolor is None else finalcolor
        self.initialstate = {"start": initialstart, "width": initialwidth, "color": QColor(initialcolor)}
        self.currentstate = {"start": initialstart, "width": initialwidth, "color": QColor(initialcolor)} \
            if currentinitial else {"start": finalstart, "width": finalwidth, "color": QColor(finalcolor)}
        self.finalstate = {"start": finalstart, "width": finalwidth, "color": QColor(finalcolor)}
        self.anim = QLineAnimation(self)
        self.anim.valueChanged.connect(self.updateSelf)
        self.finishedloops = 0
        self.anim.finished.connect(self.incLoop)

    def doAnim(self, duration=100, forward=True):
        start = 0.0 if forward else 1.0
        end = 1.0 if forward else 0.0

        self.anim.setStartValue(start)
        self.anim.setEndValue(end)
        self.anim.setDuration(duration)
        self.anim.setEasingCurve(QEasingCurve.InOutQuad)
        self.anim.start()

    updated = pyqtSignal()

    def updateSelf(self, value):
        self.currentstate["start"] = self.initialstate["start"] * (1.0 - value) + self.finalstate["start"] * value
        self.currentstate["width"] = self.initialstate["width"] * (1.0 - value) + self.finalstate["width"] * value
        red = self.initialstate["color"].red() * (1.0 - value) + self.finalstate["color"].red() * value
        green = self.initialstate["color"].green() * (1.0 - value) + self.finalstate["color"].green() * value
        blue = self.initialstate["color"].blue() * (1.0 - value) + self.finalstate["color"].blue() * value
        alpha = self.initialstate["color"].alpha() * (1.0 - value) + self.finalstate["color"].alpha() * value
        currentcolor = QColor(red, green, blue, alpha)
        self.currentstate["color"] = currentcolor
        self.updated.emit()  # why this cause m1 to no work but m2 to work

    def isAnimating(self):
        return self.anim.state() == 2

    def incLoop(self):
        self.finishedloops += 1

    def finishedLoopCount(self):
        return self.finishedloops

    def copy(self, type=None, initialstart=None, initialwidth=None, initialcolor=None, finalstart=None, finalwidth=None, finalcolor=None):
        """

        :type original: AnimState
        """

        type = self.type if type is None else type
        initialstart = self.initialstate["start"] if initialstart is None else initialstart
        initialwidth = self.initialstate["width"] if initialwidth is None else initialwidth
        initialcolor = self.initialstate["color"] if initialcolor is None else initialcolor
        finalstart = self.finalstate["start"] if finalstart is None else finalstart
        finalwidth = self.finalstate["width"] if finalwidth is None else finalwidth
        finalcolor = self.finalstate["color"] if finalcolor is None else finalcolor

        return AnimState(type, initialstart, initialwidth, initialcolor, finalstart, finalwidth, finalcolor)

    def toprimitive(self):
        return [self.type, self.initialstate, self.finalstate]

    @staticmethod
    def fromprimitive(primitive,currentinitial):
        return AnimState(primitive[0], primitive[1]["start"], primitive[1]["width"], primitive[1]["color"], primitive[2]["start"], primitive[2]["width"], primitive[2]["color"],currentinitial)
