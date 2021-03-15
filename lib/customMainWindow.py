from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import Qt, QVariantAnimation, QEasingCurve
from PyQt5.QtGui import QPainter, QBrush, QPen, QColor, QFontMetrics


class customMainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.borderwidth = 35
        self.bottomoffset = 20  # TODO fix to make less dumb
        self.resizing = False
        self.setMouseTracking(True)

    def mouseReleaseEvent(self, event):
        super(customMainWindow,self).mouseReleaseEvent(event)
        self.resizing = False
    def mousePressEvent(self, event):
        super(customMainWindow, self).mousePressEvent(event)
        #print("ok so like you clicked the:")
        print(event.pos(), self.width(), self.height())
        if event.button() == Qt.LeftButton:
            #print("left button")
            if self.width() - event.pos().x() < self.borderwidth:
                #print("clicked border right")
                self.resizing = True  # why this work tho, why don't you need to reset it to False
                self.bordernum = 2
            elif self.height() - (event.pos().y() + self.bottomoffset) < self.borderwidth:
                #print("clicked border bottom")
                self.resizing = True
                self.bordernum = 1
            elif event.pos().x() < self.borderwidth:
                #print("clicked border left")
                self.resizing = True
                self.bordernum = 0
                self.tempx = self.x() + self.width()
            else:
                self.resizing = False
                self.bordernum = -1

    def mouseMoveEvent(self, event):
        super(customMainWindow, self).mouseMoveEvent(event)
        self.grabMouse()
        #print(self.width(), self.height(), event.pos(), self.borderwidth)
        if event.pos().y() < self.borderwidth:
            self.releaseMouse()
            self.setCursor(Qt.ArrowCursor)
        elif self.width() - event.pos().x() < self.borderwidth:
            self.setCursor(Qt.SizeHorCursor)
        elif self.height() - (event.pos().y() + self.bottomoffset) < self.borderwidth:
            self.setCursor(Qt.SizeVerCursor)
        elif event.pos().x() < self.borderwidth:
            self.setCursor(Qt.SizeHorCursor)
        else:
            self.releaseMouse()
            self.setCursor(Qt.ArrowCursor)

        if self.resizing:
            #print("holy crap it's moving")
            if self.bordernum == 2:
                #print(self.width(), event.globalPos().x(), self.x())
                self.resize(event.globalPos().x() - self.x(), self.height())
            elif self.bordernum == 1:
                #print(self.height(), event.globalPos().y(), self.y())
                self.resize(self.width(), event.globalPos().y() + self.bottomoffset - self.y())
            elif self.bordernum == 0:
                #print(event.globalPos().x(), self.tempx)
                self.move(event.globalPos().x(), self.y())
                self.resize(self.tempx - event.globalPos().x(), self.height())
