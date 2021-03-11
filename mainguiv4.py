# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main.ui'
#
# Created by: PyQt5 UI code generator 5.14.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets
from ClickableLineEdit import ClickableLineEdit

from PyQt5.QtCore import Qt
from asteval import Interpreter
import re
import linecommands


aeval = Interpreter()


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):

        self.lines = []
        self.layoutchildren = []
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1111, 716)
        MainWindow.setWindowFlags(Qt.FramelessWindowHint|Qt.CustomizeWindowHint|Qt.WindowStaysOnTopHint) #or FramelessWindowHint
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        #self.centralwidget = Frame(MainWindow)
        self.centralwidget.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.centralwidget.setObjectName("centralwidget")

        self.scrollArea = QtWidgets.QScrollArea(self.centralwidget)



        self.scrollAreaContents = QtWidgets.QWidget(self.scrollArea)

        self.scrollArea.setWidget(self.scrollAreaContents)



        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.scrollAreaContents)
        self.verticalLayout_2.setContentsMargins(9, 9, -1, -1)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")


        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        Scrollbar = QtWidgets.QScrollBar()
        self.scrollArea.setVerticalScrollBar(Scrollbar)

        self.mainLayout = QtWidgets.QBoxLayout(0, self.centralwidget)
        self.mainLayout.addWidget(self.scrollArea,0)
        self.mainLayout.setContentsMargins(0,0,0,0)

        lineEdit = ClickableLineEdit(self.centralwidget)
        self.lines.append(lineEdit)
        self.lines[0].setObjectName("lineEdit")
        self.verticalLayout_2.addWidget(self.lines[0], 0, QtCore.Qt.AlignTop)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1111, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.initialize(0)
        # self.lines[0].pressed.connect(lambda: self.moved(self.lines[0]))
        # DONE left off on trying to make a key for moving cursor up and moving cursor down, basically having an event filter and sending a signal per

        self.active = self.lines[0]
        self.activeid = 0
        self.layoutchildren.insert(0, self.lines[0])

        # >>>DONE>>>>left off trying to find a way to only insert new lines at the active line, which i was planning to do by finding out which lineedit is being clicked and entered within and then finding the index of that and using it in the insert func
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))

    def activeCell(self, line):
        self.active = line
        self.activeid = self.layoutchildren.index(self.active)

        #print(self.active)

    def newCell(self, command):
        lineEdit = ClickableLineEdit(self.centralwidget)
        # >>>DONE>>>problem is basically that in this function you are appending rather than inserting at a point so it always leads back to the last entry
        # SOLUTION it appeared that -1 for array entry is relative so it'll always reference last entry no matter what, rather than a specific entry
        #print(self.activeid+1<len(self.layoutchildren))
        latestindex = self.activeid + 2 if self.activeid+1<len(self.layoutchildren) and self.layoutchildren[self.activeid+1].isReadOnly() else self.activeid + 1 #make this consistent with the other statements like it
        self.lines.append(lineEdit)
        current = len(self.lines) - 1
        self.lines[current].setObjectName("lineEdit_" + str(current))
        self.verticalLayout_2.insertWidget(latestindex, self.lines[current], QtCore.Qt.AlignTop)

        self.initialize(current)

        self.layoutchildren.insert(latestindex, self.lines[current])
        if (not command):
            cursorposition = self.layoutchildren[self.activeid].cursorPosition()
            # print(cursorposition)
            temptext = self.layoutchildren[self.activeid].displayText()
            self.layoutchildren[self.activeid].setText(temptext[0:cursorposition])
            self.layoutchildren[latestindex].setText(temptext[cursorposition:])

            self.layoutchildren[latestindex].setFocus()
            self.layoutchildren[latestindex].setCursorPosition(0)
            # print([i.displayText() for i in self.lines])
            self.active = self.layoutchildren[latestindex]
            self.activeid = latestindex
        else:
            self.layoutchildren[latestindex].setReadOnly(True) #DONETODO lots of issues with this rn
        # self.lines[current].pressed.connect(lambda: self.moved(self.lines[current]))

        # stopped at trying to move cursor to next cell when pressing enter, and when not at the end of a cell moving all text forward to next cell and keeping all before it

    def remCell(self,command = False, keytype = ""):#DONETODO add delete key jit
        #print(self.layoutchildren[self.activeid].cursorPosition())
        #print(self.layoutchildren[self.activeid].displayText())
        #print(self.activeid-1)
        if (self.layoutchildren[self.activeid].cursorPosition()==0 and self.activeid-1>=0 and keytype=="backspace") or command:
            if not command and self.activeid-1>=0:
                reference = self.activeid-2 if self.activeid-2 >= 0 and self.layoutchildren[self.activeid-1].isReadOnly() else self.activeid-1 #DONETODO make all same bruh
                #print(self.activeid, reference)
                self.layoutchildren[reference].setFocus()
                temp = self.layoutchildren[self.activeid]
            else:
                temp = self.layoutchildren[self.activeid + 1]
            self.lines.remove(temp)
            self.layoutchildren.remove(temp)
            texttemp = temp.displayText()
            self.verticalLayout_2.removeWidget(temp)
            temp.deleteLater()
            temp = None
            if not command and self.activeid-1>=0:
                previoustextemp = self.layoutchildren[reference].displayText()
                self.layoutchildren[reference].setText(previoustextemp + texttemp)
                self.layoutchildren[reference].setCursorPosition(len(previoustextemp))
                self.activeid = reference
                self.active = self.layoutchildren[self.activeid]
        #TODO combine with other one above
        elif self.layoutchildren[self.activeid].cursorPosition()==len(self.layoutchildren[self.activeid].displayText()) and self.activeid+1<len(self.layoutchildren) and keytype=="delete":
            if not command and self.activeid+1<len(self.layoutchildren):
                reference = self.activeid
                deletionid = self.activeid+2 if self.activeid+2 < len(self.layoutchildren) and self.layoutchildren[self.activeid+1].isReadOnly() else self.activeid+1 #DONETODO make all same bruh
                #print(self.activeid, reference)

                temp = self.layoutchildren[deletionid]
            self.lines.remove(temp)
            self.layoutchildren.remove(temp)
            texttemp = temp.displayText()
            self.verticalLayout_2.removeWidget(temp)
            temp.deleteLater()
            temp = None
            if not command:
                previoustextemp = self.layoutchildren[reference].displayText()
                #print(previoustextemp)
                self.layoutchildren[reference].setText(previoustextemp + texttemp)
                self.layoutchildren[reference].setCursorPosition(len(previoustextemp))


        elif keytype=="backspace":
            self.layoutchildren[self.activeid].backspace()
        elif(keytype=="delete"):
            self.layoutchildren[self.activeid].del_()
        return

    # DONETODO fix the whole shit about how this is a function on it's own and the click function isn't
    #DONETODO cleanup code
    #DONETODO make this work not dumbly
    # DONETODO use regex to make this respond to any command and then strip the command from the format to search a list or something for the command
    #DONETODO make the output cell readonly and make it so that theres only one cell deletion function
    def textCheck(self):
        check = self.active.displayText()
        m = re.match('([A-Z-a-z-0-9]+)::(.*)', check)
        #print(m)
        #print(self.activeid + 1 < len(self.layoutchildren) and self.layoutchildren[self.activeid + 1].isReadOnly())
        if m:
            command = m.group(1)
            #print("ok", command)
            if command in linecommands.commandslist:
                if not (self.activeid + 1 < len(self.layoutchildren) and self.layoutchildren[self.activeid + 1].isReadOnly()):
                    self.newCell(True)
                #DONETODO need to expand to all commands and reformat code prolly
                #DONETODO rework to make this more efficient
                expression = self.layoutchildren[self.activeid].displayText()[len(command)+2:]
                func = linecommands.commandslist[command]
                try:
                    output = linecommands.commandslist[command](expression)
                except:
                    output = "INVALID INPUT"
                self.layoutchildren[self.activeid + 1].setText(str(output))
        elif self.activeid + 1 < len(self.layoutchildren) and self.layoutchildren[self.activeid + 1].isReadOnly():
            #print("bruv")
            #print(self.layoutchildren[self.activeid].displayText())
            self.remCell(True)



    def cursorKey(self, direction):
        cursor = self.layoutchildren[self.activeid].cursorPosition()
        movement = direction*2 if 0<=self.activeid+direction<len(self.layoutchildren) and self.layoutchildren[self.activeid+direction].isReadOnly() else direction
        if 0 <= self.activeid + movement < len(self.layoutchildren):
            self.layoutchildren[self.activeid + movement].setFocus()
            self.layoutchildren[self.activeid + movement].setCursorPosition(cursor)

            self.activeid = self.activeid + movement
            self.active = self.layoutchildren[self.activeid]

    def initialize(self, index):
        self.lines[index].returnPressed.connect(lambda: self.newCell(False))
        self.lines[index].clicked.connect(lambda: self.activeCell(self.lines[index]))
        # self.lines[0].keyPressEvent = self.keyPressEvent
        self.lines[index].up.connect(lambda: self.cursorKey(-1))
        self.lines[index].down.connect(lambda: self.cursorKey(1))
        self.lines[index].textChanged.connect(self.textCheck) #figure out whether this should be edited or changed

        self.lines[index].backspacekey.connect(lambda: self.remCell(False, "backspace"))
        self.lines[index].deletekey.connect(lambda:self.remCell(False, "delete"))


        #self.lines[index].focusout.connect()

        # self.lines[index].returnPressed.connect(self.lines[index].commandDone)
        # self.lines[index].editingFinished.connect(self.lines[index].commandDone)

class TitleBar(QtWidgets.QDialog):
    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.setWindowFlags(Qt.FramelessWindowHint)
        css = """
        QWidget{
            Background: #AA00AA;
            color:white;
            font:12px bold;
            font-weight:bold;
            border-radius: 1px;
            height: 11px;
        }
        QDialog{
            Background-image:url('img/titlebar bg.png');
            font-size:12px;
            color: black;

        }
        QToolButton{
            Background:#AA00AA;
            font-size:11px;
        }
        QToolButton:hover{
            Background: #FF00FF;
            font-size:11px;
        }
        """
        self.setAutoFillBackground(True)
        self.setBackgroundRole(QtGui.QPalette.Highlight)
        #self.setStyleSheet(css)
        self.minimize=QtWidgets.QToolButton(self)
        #self.minimize.setIcon(QtGui.QIcon('img/min.png'))
        self.maximize=QtWidgets.QToolButton(self)
        #self.maximize.setIcon(QtGui.QIcon('img/max.png'))
        close=QtWidgets.QToolButton(self)
        #close.setIcon(QtGui.QIcon('img/close.png'))
        self.minimize.setMinimumHeight(0)
        close.setMinimumHeight(0)
        self.maximize.setMinimumHeight(0)
        self.setWindowTitle("Window Title")
        hbox=QtWidgets.QHBoxLayout(self)
        hbox.addWidget(self.minimize)
        hbox.addWidget(self.maximize)
        hbox.addWidget(close)
        hbox.insertStretch(0,500)
        hbox.setSpacing(0)
        self.setSizePolicy(QtWidgets.QSizePolicy.Minimum,QtWidgets.QSizePolicy.Minimum)
        self.maxNormal=False
        close.clicked.connect(self.close)
        self.minimize.clicked.connect(self.showSmall)
        self.maximize.clicked.connect(self.showMaxRestore)

    def showSmall(self):
        box.showMinimized()

    def showMaxRestore(self):
        if(self.maxNormal):
            box.showNormal()
            self.maxNormal= False
            self.maximize.setIcon(QtGui.QIcon('img/max.png'))
            #print('1')
        else:
            box.showMaximized()
            self.maxNormal=  True
            #print('2')
            self.maximize.setIcon(QtGui.QIcon('img/max2.png'))

    def close(self):
        box.close()

    def mousePressEvent(self,event):
        if event.button() == Qt.LeftButton:
            box.moving = True
            box.offset = event.pos()

    def mouseMoveEvent(self,event):
        if box.moving: box.move(event.globalPos()-box.offset)


class Frame(QtWidgets.QFrame):
    def __init__(self, parent=None):
        QtWidgets.QFrame.__init__(self, parent)
        self.m_mouse_down= False
        self.setFrameShape(QtWidgets.QFrame.StyledPanel)
        css = """
        QFrame{
            Background:  #D700D7;
            color:white;
            font:13px ;
            font-weight:bold;
            }
        """
        self.setStyleSheet(css)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setMouseTracking(True)
        self.m_titleBar= TitleBar(self)
        self.m_content= QtWidgets.QWidget(self)
        vbox=QtWidgets.QVBoxLayout(self)
        vbox.addWidget(self.m_titleBar)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(0)
        layout=QtWidgets.QVBoxLayout()
        layout.addWidget(self.m_content)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        vbox.addLayout(layout)
        # Allows you to access the content area of the frame
        # where widgets and layouts can be added

    def contentWidget(self):
        return self.m_content

    def titleBar(self):
        return self.m_titleBar

    def mousePressEvent(self,event):
        self.m_old_pos = event.pos()
        self.m_mouse_down = event.button()== Qt.LeftButton

    def mouseMoveEvent(self,event):
        x=event.x()
        y=event.y()

    def mouseReleaseEvent(self,event):
        m_mouse_down=False


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    stylesheet = """
                    QMainWindow,QScrollArea,.QWidget {
                        border-style:none;
                        background-color: #101229;
                    }
                    QScrollBar {
                       border-style: none;
                       width: 0px;
                    }
                    """
    app.setStyleSheet(stylesheet)
    MainWindow = QtWidgets.QMainWindow()
    box = Frame()
    box.move(60, 60)
    l = QtWidgets.QVBoxLayout(box.contentWidget())
    l.setContentsMargins(0, 0, 0, 0)
    l.addWidget(MainWindow)
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    box.show()
    sys.exit(app.exec_())
