from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QMenuBar,QToolButton,QHBoxLayout,QWidget
from PyQt5.QtCore import Qt, QVariantAnimation, QEasingCurve, pyqtSignal, QSize
import PyQt5.QtCore
from PyQt5.QtGui import QPainter, QBrush, QPen, QColor, QIcon,QPixmap
import re

class CustomMenuBar(QWidget):
    newwindowrequest = pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)
        self.mainwindow=parent
        self.newwindow = QToolButton(self)
        icon = QIcon()
        icon.addPixmap(QPixmap("icons/windowadd.png"),QIcon.Normal,QIcon.Off)
        self.newwindow.setIcon(icon)
        self.newwindow.setStyleSheet("background-color: rgba(255,255,255,0)")
        #self.newwindow.setIcon(QIcon("/windowadd.png"))
        #self.newwindow.setIconSize(QSize(40,0))
        self.minimize=QToolButton(self)
        icon = QIcon()
        icon.addPixmap(QPixmap("icons/windowminimize.png"), QIcon.Normal, QIcon.Off)
        self.minimize.setIcon(icon)
        self.minimize.setStyleSheet("background-color: rgba(255,255,255,0)")
        #self.minimize.setIcon(QIcon("/windowminimize.png"))
        self.maximize=QToolButton(self)
        icon = QIcon()
        icon.addPixmap(QPixmap("icons/windowmin.png"), QIcon.Normal, QIcon.Off)
        self.maximize.setIcon(icon)
        self.maximize.setStyleSheet("background-color: rgba(255,255,255,0)")
        #self.maximize.setIcon(QIcon("/windowmin.png"))
        close = QToolButton(self)
        icon = QIcon()
        icon.addPixmap(QPixmap("icons/windowclose.png"), QIcon.Normal, QIcon.Off)
        close.setIcon(icon)
        close.setStyleSheet("background-color: rgba(255,255,255,0)")
        #close.setIcon(QIcon("/windowclose.png"))
        hbox=QHBoxLayout(self)
        hbox.setContentsMargins(-1,-1,-1,0)
        hbox.addWidget(self.newwindow)
        hbox.addWidget(self.minimize)
        hbox.addWidget(self.maximize)
        hbox.addWidget(close)
        hbox.insertStretch(1, 500)
        self.setFixedHeight(20)
        self.newwindow.clicked.connect(self.newWindow)
        self.minimize.clicked.connect(self.showSmall)
        self.maximize.clicked.connect(self.showMaxRestore)
        close.clicked.connect(self.close)
        self.maxNormal = False
    def newWindow(self):
        self.newwindowrequest.emit()
    def showSmall(self):
        #print("minimized")
        self.mainwindow.showMinimized()
    def showMaxRestore(self):
        if self.maxNormal:
            self.mainwindow.showNormal()
            icon = QIcon()
            icon.addPixmap(QPixmap("windowmin.png"), QIcon.Normal, QIcon.Off)
            self.maximize.setIcon(icon)
            self.mainwindow.setContentsMargins(15,15,15,15)
            self.maxNormal = False
            #print('1')
        else:
            self.mainwindow.showMaximized()
            icon = QIcon()
            self.mainwindow.setContentsMargins(0,0,0,0)
            icon.addPixmap(QPixmap("windowmax.png"), QIcon.Normal, QIcon.Off)
            self.maximize.setIcon(icon)
            self.maxNormal = True
            #print('2')
        self.mainwindow.repaint()
        self.mainwindow.update()
        self.mainwindow.repaint()
        self.mainwindow.updateGeometry()
        self.mainwindow.updateMicroFocus()
        self.updateGeometry()
        self.repaint()
        self.update()
        self.repaint()
        self.updateMicroFocus()
        self.show()
        self.mainwindow.show()
    def close(self):
        #print('closed')
        self.mainwindow.close()
    def mousePressEvent(self,event):
        #print(event.pos())
        if event.button() == Qt.LeftButton:
            ogwidth = self.mainwindow.width()
            self.mainwindow.moving = True
            self.mainwindow.offset = event.pos()
            if (self.maxNormal):
                self.mainwindow.showNormal()
                self.maxNormal = False
                scaleratio=self.mainwindow.width()/ogwidth
                self.mainwindow.offset.setX(self.mainwindow.offset.x()*scaleratio)
    def mouseMoveEvent(self,event):
        if self.mainwindow.moving:
            self.mainwindow.move(event.globalPos()-self.mainwindow.offset)
