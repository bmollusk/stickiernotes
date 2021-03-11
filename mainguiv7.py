
#

#



from PyQt5 import QtCore, QtGui, QtWidgets
from ClickableLineEdit import ClickableLineEdit
from CustomMenuBar import CustomMenuBar
from customMainWindow import customMainWindow

from PyQt5.QtCore import Qt
from asteval import Interpreter
import re
import linecommands

aeval = Interpreter()


class Ui_MainWindow(object):
    def setupUi(self, MainWindow, id, x, y):
        self.id = id
        self.mainwindow = MainWindow
        self.lines = []
        self.layoutchildren = []
        self.actualtext = dict()

        # initialize MainWindow
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1111, 716)
        MainWindow.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.MSWindowsFixedSizeDialogHint)
        MainWindow.setAttribute(Qt.WA_TranslucentBackground)

        self.centralwidget = QtWidgets.QWidget(MainWindow)

        # add window shadow effect
        shadow = QtWidgets.QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15.0)
        shadow.setColor(QtGui.QColor(0, 0, 0, 160))
        shadow.setOffset(0, 0)
        MainWindow.setContentsMargins(15, 15, 15, 15)
        self.centralwidget.setGraphicsEffect(shadow)

        # set up central widget
        self.centralwidget.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.centralwidget.setObjectName("centralwidget")

        # create titlebar
        self.titlebar = CustomMenuBar(MainWindow)
        self.titlebar.newwindowrequest.connect(lambda: self.createNewWindow())

        # create scroll area
        self.scrollArea = QtWidgets.QScrollArea(self.centralwidget)
        self.scrollAreaContents = QtWidgets.QWidget(self.scrollArea)
        self.scrollArea.setWidget(self.scrollAreaContents)

        # create vertical layout
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.scrollAreaContents)
        self.verticalLayout_2.setContentsMargins(9, 0, -1, -1)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")

        #set resizing properties on scrollarea
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        #add scroll bar
        Scrollbar = QtWidgets.QScrollBar()
        self.scrollArea.setVerticalScrollBar(Scrollbar)

        #add main layout
        self.mainLayout = QtWidgets.QGridLayout(self.centralwidget)

        #create size grip
        self.sizegrip = QtWidgets.QSizeGrip(self.centralwidget)

        #add titlebar, scrollarea, and sizegrip
        self.mainLayout.addWidget(self.titlebar, 1, 1)
        self.mainLayout.addWidget(self.scrollArea, 2, 1)
        self.mainLayout.addWidget(self.sizegrip, 3, 1, 1, 1, Qt.AlignBottom | Qt.AlignRight)

        #set main layout margins
        self.mainLayout.setContentsMargins(0, 0, 0, 0)

        #create first lineedit
        lineEdit = ClickableLineEdit(self.centralwidget ,self)
        self.lines.append(lineEdit)
        self.lines[0].setObjectName("lineEdit")
        self.verticalLayout_2.addWidget(self.lines[0], 0, QtCore.Qt.AlignTop)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)

        # add menubar and statusbar
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1111, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.statusbar.setSizeGripEnabled(False)
        self.initialize(0)

        # initialize active
        self.active = self.lines[0]
        self.activeid = 0
        self.active.active = True
        self.layoutchildren.insert(0, self.lines[0])

        # housekeeping
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        #load session
        self.loadSession()

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))

    def saveSession(self):
        settings = QtCore.QSettings("bbqmollusc", "stickiernotes")

        settings.remove("window" + str(self.id))
        if not (len(self.lines )==1 and self.lines[0].displayText( )==""):
            settings.beginGroup("window" + str(self.id))
            settings.setValue("activeid", self.activeid)
            settings.setValue("lines" ,len(self.lines))
            if self.activeid < len(self.layoutchildren):
                paus = self.lines[self.activeid].cursorPosition(  )  # TODO Make this consistent tf
                settings.setValue("cursorPosition", paus)

            for i in range(len(self.lines)):

                if len(self.lines[i].refgroups ) >0 and i== self.activeid:
                    chopped = self.lines[i].getNormText()
                    settings.setValue(str(i), "".join(chopped))
                else:
                    settings.setValue(str(i), self.lines[i].displayText())
                settings.setValue(str(i) + "/refgroup", self.lines[i].refgroups)
                settings.setValue(str(i) + "/referenced", self.lines[i].referenced)
                settings.setValue(str(i) + "/referring", self.lines[i].referring)
                settings.setValue(str(i) + "/readonly", self.lines[i].isReadOnly())

            settings.endGroup()

    def loadSession(self):
        settings = QtCore.QSettings("bbqmollusc", "stickiernotes")

        settings.beginGroup("window" + str(self.id))

        if settings.value("lines", 1) > 0:
            temp = self.lines[0]
            self.lines.remove(temp)
            self.layoutchildren.remove(temp)
            self.verticalLayout_2.removeWidget(temp)
            temp.deleteLater()
            temp = None
            for i in range(settings.value("lines", 1)):
                val = str(settings.value(str(i), ""))
                lineEdit = ClickableLineEdit(self.centralwidget, self)
                lineEdit.setText(val)
                lineEdit.refgroups = settings.value(str(i) + "/refgroup", [])
                lineEdit.referenced = [int(j) for j in settings.value(str(i) + "/referenced", [])]
                lineEdit.referring = [int(j) for j in settings.value(str(i) + "/referring", [])]
                lineEdit.setObjectName("lineEdit_" + str(i))
                self.lines.append(lineEdit)
                self.verticalLayout_2.insertWidget(i, self.lines[i], QtCore.Qt.AlignTop)
                self.initialize(i)
                self.layoutchildren.append(self.lines[i])
                read = (settings.value(str(i) + "/readonly", 'false')) == "true"
                if read:
                    self.lines[i].setReadOnly(True)
        if self.lines[len(self.lines) - 1].isReadOnly():
            pos = len(self.lines) - 2
        else:
            pos = len(self.lines) - 1
        self.lines[settings.value("activeid",
                                  pos)].setFocus()
        self.activeid = settings.value("activeid", pos)
        self.active = self.lines[self.activeid]
        self.active.active = True  # TODO make all this shit into a function

        self.active.setCursorPosition(settings.value("cursorPosition", 0))
        settings.endGroup()
        if "window" + str(self.id + 1) in settings.childGroups():
            self.createNewWindow()

    def activeCell(self, line):
        self.active.active = False
        self.active = line
        self.activeid = self.layoutchildren.index(self.active)
        self.active.active = True

    def newCell(self, command, num=1): #creates *num* amount of new cells, specify whether new cells are output cells for a command or not
        self.scrollArea.verticalScrollBar().setValue(self.scrollArea.verticalScrollBar().maximum())
        for i in range(num):
            lineEdit = ClickableLineEdit(self.centralwidget, self)  # TODO make this shit work better, there's two others of em too

            j = self.activeid + 1
            while j < len(self.layoutchildren) and self.layoutchildren[j].isReadOnly():
                j += 1

            latestindex = j
            self.lines.append(lineEdit)
            current = len(self.lines) - 1
            self.lines[current].setObjectName("lineEdit_" + str(current))
            self.verticalLayout_2.insertWidget(latestindex, self.lines[current], QtCore.Qt.AlignTop)

            self.initialize(current)

            self.layoutchildren.insert(latestindex, self.lines[current])
            if (not command):
                cursorposition = self.layoutchildren[self.activeid].cursorPosition()

                temptext = self.layoutchildren[self.activeid].displayText()
                self.layoutchildren[self.activeid].setText(temptext[0:cursorposition])
                self.layoutchildren[latestindex].setText(temptext[cursorposition:])

                self.layoutchildren[latestindex].setFocus()
                self.layoutchildren[latestindex].setCursorPosition(0)

                self.activeCell(self.layoutchildren[latestindex])
            else:
                self.layoutchildren[latestindex].setReadOnly(True)

    def remCell(self, command=False, keytype="", num=1):
        for i in range(num):

            ind = 0
            temprefs = []

            if (self.layoutchildren[
                    self.activeid].cursorPosition() == 0 and self.activeid - 1 >= 0 and keytype == "backspace") or command:

                if not command and self.activeid - 1 >= 0:

                    j = self.activeid - 1
                    while j >= 0 and self.layoutchildren[j].isReadOnly():
                        j -= 1
                    reference = j

                    self.layoutchildren[reference].setFocus()
                    ind = self.activeid
                    temp = self.layoutchildren[self.activeid]
                else:
                    ind = self.activeid + 1
                    temp = self.layoutchildren[self.activeid + 1]
                for i in temp.referring:
                    temprefs.append(ind + i)

                self.lines.remove(temp)
                self.layoutchildren.remove(temp)
                texttemp = temp.refDisplayText()
                self.verticalLayout_2.removeWidget(temp)
                temp.deleteLater()
                temp = None
                if not command and self.activeid - 1 >= 0:
                    previoustextemp = self.layoutchildren[reference].refDisplayText()
                    self.layoutchildren[reference].setText(previoustextemp + texttemp)
                    self.layoutchildren[reference].setCursorPosition(len(previoustextemp))
                    self.active.active = False
                    self.activeid = reference
                    self.active = self.layoutchildren[self.activeid]
                    self.active.active = True

            elif self.layoutchildren[self.activeid].cursorPosition() == len(
                    self.layoutchildren[self.activeid].refDisplayText()) and self.activeid + 1 < len(
                self.layoutchildren) and keytype == "delete":
                if not command and self.activeid + 1 < len(self.layoutchildren):
                    reference = self.activeid

                    j = self.activeid + 1
                    while j + 1 < len(self.layoutchildren) and self.layoutchildren[j].isReadOnly():
                        j += 1

                    ind = j
                    deletionid = j
                    temp = self.layoutchildren[deletionid]
                for i in temp.referring:
                    temprefs.append(ind + i)

                self.lines.remove(temp)
                self.layoutchildren.remove(temp)
                texttemp = temp.refDisplayText()
                self.verticalLayout_2.removeWidget(temp)
                temp.deleteLater()
                temp = None
                if not command:
                    previoustextemp = self.layoutchildren[reference].refDisplayText()

                    self.layoutchildren[reference].setText(previoustextemp + texttemp)
                    self.layoutchildren[reference].setCursorPosition(len(previoustextemp))
            elif keytype == "backspace":
                self.layoutchildren[self.activeid].backspace()
            elif (keytype == "delete"):
                self.layoutchildren[self.activeid].del_()
            for j in temprefs:
                self.layoutchildren[j].remRef(ind)
        return

    def textCheck(self, tocheck=-1, recurse=True):

        if (tocheck == -1):
            tocheck = self.activeid
        recurselist = [tocheck, tocheck + 1]
        check = self.layoutchildren[tocheck].refDisplayText()
        m = re.match('([A-Z-a-z-0-9]+)::(.*)', check)

        if m:
            command = m.group(1)

            if command in linecommands.commandslist:
                expression = self.layoutchildren[tocheck].realDisplayText()[len(command) + 2:]
                func = linecommands.commandslist[command]
                try:
                    output = linecommands.commandslist[command](expression)
                except:
                    output = "INVALID INPUT"

                if isinstance(output, list):
                    i = 0
                    while tocheck + i + 1 < len(self.layoutchildren) and self.layoutchildren[tocheck + i + 1].isReadOnly():
                        i += 1
                    recurselist[1] = tocheck + i + 2
                    if i > len(output):
                        self.remCell(True, num=i - len(output))
                    elif i < len(output):
                        self.newCell(True, len(output) - i)



                else:
                    recurselist[1] = tocheck + 2
                    if not (tocheck + 1 < len(self.layoutchildren) and self.layoutchildren[tocheck + 1].isReadOnly()):
                        self.newCell(True)

                if isinstance(output, list):
                    for i in range(len(output)):
                        self.layoutchildren[tocheck + i + 1].setText(str(output[i]))
                else:
                    self.layoutchildren[tocheck + 1].setText(str(output))
        elif tocheck + 1 < len(self.layoutchildren) and self.layoutchildren[tocheck + 1].isReadOnly():
            i = 0
            while tocheck + i + 1 < len(self.layoutchildren) and self.layoutchildren[tocheck + i + 1].isReadOnly():
                i += 1

            self.remCell(True, num=i)
        m2 = re.match('(.*):([A-Z-a-z-0-9]+):(.*):', check)
        if m2:

            command = m2.group(2)

            expression = m2.group(3)

            if command in linecommands.commandslist:
                func = linecommands.commandslist[command]
                try:
                    output = linecommands.commandslist[command](expression)

                except:
                    output = "INVALID INPUT"
                self.layoutchildren[tocheck].fades.append(str(output))

                before = self.layoutchildren[tocheck].displayText()[:len(m2.group(1))]

                after = self.layoutchildren[tocheck].displayText()[
                        len(m2.group(1)) + 1 + len(m2.group(2)) + 1 + len(m2.group(3)) + 1:]

                self.layoutchildren[tocheck].setText(before + str(output) + after)

        # TODO make it so when it doesnt find anything it empties the refgroups array thx ;)

        string = check
        m3 = re.search(r'<(-[0-9]+)>', string)
        m31 = [j for j in re.finditer(r'<(-[0-9]+)>', string)]
        ind = 0
        while m3:
            num = int(m3.group(1))

            if tocheck + num >= 0:
                before = string[:m3.span()[0]]
                output = "|" + self.layoutchildren[tocheck + num].displayText() + "|"
                if self.layoutchildren[tocheck].latestspan == m31[ind].span(1):
                    self.layoutchildren[tocheck].fades.append(True)

                after = string[m3.span()[1]:]

                string = before + str(output) + after
                m3 = re.search(r'<(-[0-9]+)>', string)
            else:
                before = string[:m3.span()[0]]
                output = "<!" + str(num) + ">"
                if self.layoutchildren[tocheck].latestspan == m3.span(1):
                    self.layoutchildren[tocheck].fades.append(False)

                after = string[m3.span()[1]:]

                string = before + str(output) + after
                m3 = re.search(r'<(-[0-9]+)>', string)
            ind += 1
        m4 = [j for j in re.finditer(r'\|([^\|]+)\|', string)]

        if len(m4) > 0:
            temp = []
            for j in range(len(m4)):
                temp.append([m31[j].group(0), m4[j].group(0), m31[j].span(0), m4[j].span(0)])  # TODO this is where there's an issue, it's with the span shit nigga cause you be like ha gay
            minus = 0

            tempus = []
            for i in m31:
                num = int(i.group(1))
                tempus.append(num)
                self.layoutchildren[tocheck + num].addRef(tocheck)
            for i in self.layoutchildren[tocheck].referring:
                if i not in tempus:
                    self.layoutchildren[tocheck + i].remRef(tocheck)
            self.layoutchildren[tocheck].referring = tempus
            for t in range(len(temp)):
                temp[t][1] = temp[t][1][1:len(temp[t][1]) - 1]
                temp[t][3] = (temp[t][3][0] - minus, temp[t][3][1] - minus - 2)
                minus += 2

            self.layoutchildren[tocheck].refgroups = temp
        else:
            self.layoutchildren[tocheck].refgroups = []
            for i in self.layoutchildren[tocheck].referring:
                self.layoutchildren[tocheck + i].remRef(tocheck)

        # TODO maybe make so all the ones use active or get the array thing
        if recurse:
            for i in range(recurselist[0], recurselist[1]):
                self.refRecurse(i)

        self.saveSession()

    def refRecurse(self, index):
        for r1 in self.layoutchildren[index].referenced:
            r = self.layoutchildren[r1]
            oboe = []
            offset = 0
            refgroups = []
            for s in range(len(r.refgroups)):
                if index - self.layoutchildren.index(r) != int(r.refgroups[s][0][1:len(r.refgroups[s][0]) - 1]):
                    ob, oe = r.refgroups[s][3]
                    r.refgroups[s][3] = (ob + offset, oe + offset)
                    continue
                r.refgroups[s][1] = self.layoutchildren[index].realDisplayText()
                ob, oe = r.refgroups[s][3]
                oboe.append((ob, oe))
                r.refgroups[s][3] = (ob + offset, ob + len(self.layoutchildren[index].realDisplayText()) + offset)
                offset += len(self.layoutchildren[index].realDisplayText()) - (oe - ob)
                refgroups.append(r.refgroups[s])
            chopped = []
            # TODO rn this is a bunch of ifs, which is bad, make this not a bunch of ifs
            for s in range(len(oboe)):
                if s == 0 and s == len(oboe) - 1:
                    before = r.displayText()[:oboe[s][0]]
                    chopped.append(before)
                    output = refgroups[s][1]
                    chopped.append(output)
                    after = r.displayText()[oboe[s][1]:]
                    chopped.append(after)
                elif s == 0:
                    before = r.displayText()[:oboe[s][0]]
                    chopped.append(before)
                    output = refgroups[s][1]
                    chopped.append(output)
                    after = r.displayText()[oboe[s][1]:oboe[s + 1][0]]
                    chopped.append(after)
                elif s == len(oboe) - 1:

                    output = refgroups[s][1]
                    chopped.append(output)
                    after = r.displayText()[oboe[s][1]:]
                    chopped.append(after)
                else:

                    output = refgroups[s][1]
                    chopped.append(output)
                    after = r.displayText()[oboe[s][1]:oboe[s + 1][0]]
                    chopped.append(after)
            if (len(r.refgroups) > 0):
                newstr = "".join(chopped)
                r.setText(newstr)
                self.textCheck(r1)

            self.refRecurse(r1)

    def cursorKey(self, direction):
        cursor = self.layoutchildren[self.activeid].cursorPosition()

        j = self.activeid + direction

        if direction < 0:
            while j >= 0 and self.layoutchildren[j].isReadOnly():
                j -= 1
        else:
            while j < len(self.layoutchildren) and self.layoutchildren[j].isReadOnly():
                j += 1
        movement = j

        if 0 <= movement < len(self.layoutchildren):
            self.layoutchildren[movement].setFocus()
            check = self.layoutchildren[movement].displayText()
            m = re.match('([A-Z-a-z-0-9]+)::(.*)', check)
            if m:
                offset = len(m.group(1)) + 2
                self.layoutchildren[movement].setCursorPosition(cursor + offset)
            else:
                self.layoutchildren[movement].setCursorPosition(cursor)

            self.active.active = False
            self.activeid = movement
            self.active = self.layoutchildren[self.activeid]
            self.active.active = True

    def insertReference(self, referral):
        beg = self.layoutchildren[self.activeid].displayText()[:self.layoutchildren[self.activeid].cursorPosition()]
        end = self.layoutchildren[self.activeid].displayText()[self.layoutchildren[self.activeid].cursorPosition():]
        ind = self.layoutchildren.index(referral) - self.activeid
        self.layoutchildren[self.activeid].setText(beg + "<" + str(ind) + end)
        self.layoutchildren[self.activeid].setFocus()

    def initialize(self, index):
        self.lines[index].returnPressed.connect(lambda: self.newCell(False))
        self.lines[index].clicked.connect(lambda: self.activeCell(self.lines[index]))

        self.lines[index].up.connect(lambda: self.cursorKey(-1))
        self.lines[index].down.connect(lambda: self.cursorKey(1))
        self.lines[index].textEdited.connect(lambda: self.textCheck())

        self.lines[index].backspacekey.connect(lambda: self.remCell(False, "backspace"))
        self.lines[index].deletekey.connect(lambda: self.remCell(False, "delete"))

        self.lines[index].identify.connect(self.insertReference)

    def createNewWindow(self):

        newMainWindow = QtWidgets.QMainWindow()

        newui = Ui_MainWindow()
        newui.setupUi(newMainWindow, self.id + 1, self.mainwindow.x() + 10, self.mainwindow.y() + 10)
        newMainWindow.show()
        newMainWindow.move(self.mainwindow.x() + 10, self.mainwindow.y() + 10)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    stylesheet = """
                    QMainWindow,QScrollArea,.QWidget {
                        border-style:none;
                        background-color: #101229
                    }
                    QScrollBar {
                       border-style: none;
                       width: 0px;
                    }
                    """
    app.setStyleSheet(stylesheet)
    MainWindow = customMainWindow()

    ui = Ui_MainWindow()
    ui.setupUi(MainWindow, 0, MainWindow.x(), MainWindow.y())
    MainWindow.show()
    sys.exit(app.exec_())
