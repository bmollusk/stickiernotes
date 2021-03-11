# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main.ui'
#
# Created by: PyQt5 UI code generator 5.14.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets
from ClickableLineEdit import ClickableLineEdit
from CustomMenuBar import CustomMenuBar

from PyQt5.QtCore import Qt
from asteval import Interpreter
import re
import linecommands


aeval = Interpreter()

class Ui_MainWindow(object):
    def setupUi(self, MainWindow,id,x,y):
        self.id = id
        self.mainwindow = MainWindow
        self.lines = []
        self.layoutchildren = []
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1111, 716)
        MainWindow.setWindowFlags(Qt.FramelessWindowHint|Qt.WindowStaysOnTopHint|Qt.MSWindowsFixedSizeDialogHint)
        
        # self.mainwindowcontainer = QtWidgets.QWidget()
        # self.mainwindowcontainer.setLayout(QtWidgets.QGridLayout())
        # self.mainwindowcontainer.setWindowFlags(Qt.FramelessWindowHint)
        # self.mainwindowcontainer.setAttribute(Qt.WA_TranslucentBackground)

        MainWindow.setAttribute(Qt.WA_TranslucentBackground)

        self.centralwidget = QtWidgets.QWidget(MainWindow)

        # self.mainwindowcontainer.layout().addWidget(MainWindow)
        # self.mainwindowcontainer.layout().setContentsMargins(10,10,10,10)

        shadow = QtWidgets.QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15.0)
        shadow.setColor(QtGui.QColor(0,0,0,160))
        shadow.setOffset(0,0)
        # MainWindow.setGraphicsEffect(shadow)
        MainWindow.setContentsMargins(15,15,15,15)
        self.centralwidget.setGraphicsEffect(shadow)

        self.centralwidget.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.centralwidget.setObjectName("centralwidget")

        self.titlebar = CustomMenuBar(MainWindow)
        self.titlebar.newwindowrequest.connect(lambda: self.createNewWindow())
        self.scrollArea = QtWidgets.QScrollArea(self.centralwidget)



        self.scrollAreaContents = QtWidgets.QWidget(self.scrollArea)

        self.scrollArea.setWidget(self.scrollAreaContents)



        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.scrollAreaContents)
        self.verticalLayout_2.setContentsMargins(9, 0, -1, -1)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")


        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        Scrollbar = QtWidgets.QScrollBar()
        self.scrollArea.setVerticalScrollBar(Scrollbar)

        self.mainLayout = QtWidgets.QBoxLayout(2,self.centralwidget)

        self.mainLayout.addWidget(self.titlebar,0)
        self.mainLayout.addWidget(self.scrollArea,1)


        self.mainLayout.setContentsMargins(0,0,0,0)

        lineEdit = ClickableLineEdit(self.centralwidget)
        self.lines.append(lineEdit)
        self.lines[0].setObjectName("lineEdit")
        self.verticalLayout_2.addWidget(self.lines[0], 0, QtCore.Qt.AlignTop)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        #self.menubar = CustomMenuBar(MainWindow)
        #self.menubar.setNativeMenuBar(False)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1111, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.statusbar.setSizeGripEnabled(False)
        self.initialize(0)
        # self.lines[0].pressed.connect(lambda: self.moved(self.lines[0]))
        # DONE left off on trying to make a key for moving cursor up and moving cursor down, basically having an event filter and sending a signal per

        self.active = self.lines[0]
        self.activeid = 0
        self.layoutchildren.insert(0, self.lines[0])


        #self.loadSession()
        # >>>DONE>>>>left off trying to find a way to only insert new lines at the active line, which i was planning to do by finding out which lineedit is being clicked and entered within and then finding the index of that and using it in the insert func
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
    def saveSession(self):
        settings=QtCore.QSettings("bbqmollusc","stickiernotes")
        settings.remove("window"+str(self.id))
        settings.beginGroup("window"+str(self.id))
        settings.setValue("activeid",self.activeid)
        paus=self.lines[self.activeid].cursorPosition()
        settings.setValue("cursorPosition", paus)
        #print("activeid",self.activeid)
        for i in range(len(self.lines)):
            print(str(i),self.lines[i].displayText())
            settings.setValue(str(i),self.lines[i].displayText())
        print(settings.allKeys())
        settings.endGroup()
        print(settings.childGroups())
    def loadSession(self):
        settings = QtCore.QSettings("bbqmollusc", "stickiernotes")
        read = False
        settings.beginGroup("window"+str(self.id))
        print(settings.group())
        if len(settings.allKeys())-2>0:
            temp = self.lines[0]
            self.lines.remove(temp)
            self.layoutchildren.remove(temp)
            self.verticalLayout_2.removeWidget(temp)
            temp.deleteLater()
            temp = None
            for i in range(len(settings.allKeys())-2):
                val = str(settings.value(str(i), ""))
                m = re.match('([A-Z-a-z-0-9]+)::(.*)', val)
                lineEdit = ClickableLineEdit(self.centralwidget)
                lineEdit.setText(val)
                lineEdit.setObjectName("lineEdit_" + str(i))
                self.lines.append(lineEdit)
                self.verticalLayout_2.insertWidget(i,self.lines[i],QtCore.Qt.AlignTop)
                self.initialize(i)
                self.layoutchildren.append(self.lines[i])
                if read:
                    self.lines[i].setReadOnly(True)
                    read = False
                if m:
                    read = True
        if self.lines[len(self.lines)-1].isReadOnly():
            pos = len(self.lines)-2
        else:
            pos = len(self.lines)-1
        self.lines[settings.value("activeid",pos)].setFocus()#TODO have if statement for if this is readonly otherwise skip to prior one
        self.activeid = settings.value("activeid",pos)
        self.active = self.lines[self.activeid]
        self.active.setCursorPosition(settings.value("cursorPosition",0))
        settings.endGroup()
        if "window"+str(self.id + 1) in settings.childGroups():
            self.createNewWindow()
    def activeCell(self, line):
        self.active = line
        self.activeid = self.layoutchildren.index(self.active)
        print(self.id)
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
        self.saveSession()


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

    def createNewWindow(self):
        #print("made")
        newMainWindow = QtWidgets.QMainWindow()

        newui = Ui_MainWindow()
        newui.setupUi(newMainWindow,self.id+1,self.mainwindow.x()+10,self.mainwindow.y()+10)
        newMainWindow.show()
        newMainWindow.move(self.mainwindow.x()+10,self.mainwindow.y()+10)
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
    #MainWindow = Window()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow,0,MainWindow.x(),MainWindow.y())
    MainWindow.show()
    sys.exit(app.exec_())

