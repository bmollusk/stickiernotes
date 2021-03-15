from PyQt5 import QtCore, QtGui, QtWidgets
from lib.ClickableLineEditv2 import ClickableLineEdit, AnimState
from lib.CustomMenuBar import CustomMenuBar
from lib.customMainWindow import customMainWindow
from bisect import bisect_right
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFontMetrics, QColor
from asteval import Interpreter
import re
import linecommands


# aeval = Interpreter()

class Ui_MainWindow(object):
    def setupUi(self, MainWindow, id, x, y):
        self.id = id
        self.mainwindow = MainWindow
        self.layoutchildren = []

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
        self.scrollArea.setFocusPolicy(Qt.NoFocus)
        self.scrollAreaContents = QtWidgets.QWidget(self.scrollArea)
        self.scrollArea.setWidget(self.scrollAreaContents)

        # create vertical layout
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.scrollAreaContents)
        self.verticalLayout_2.setContentsMargins(9, 0, -1, -1)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")

        # set resizing properties on scrollarea
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        # add scroll bar
        Scrollbar = QtWidgets.QScrollBar()
        self.scrollArea.setVerticalScrollBar(Scrollbar)

        # add main layout
        self.mainLayout = QtWidgets.QGridLayout(self.centralwidget)

        # create size grip
        self.sizegrip = QtWidgets.QSizeGrip(self.centralwidget)

        # add titlebar, scrollarea, and sizegrip
        self.mainLayout.addWidget(self.titlebar, 1, 1)
        self.mainLayout.addWidget(self.scrollArea, 2, 1)
        self.mainLayout.addWidget(self.sizegrip, 3, 1, 1, 1, Qt.AlignBottom | Qt.AlignRight)

        # set main layout margins
        self.mainLayout.setContentsMargins(0, 0, 0, 0)

        # create first lineedit
        lineEdit = ClickableLineEdit(self.centralwidget)

        self.verticalLayout_2.addWidget(lineEdit, 0, QtCore.Qt.AlignTop)
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

        # initialize active
        self.active = lineEdit
        self.activeid = 0
        self.active.active = True
        self.active.focused = True
        self.layoutchildren.insert(0, lineEdit)
        self.initialize(0)

        # housekeeping
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        # load session
        # self.loadSession()

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))

    def saveSession(self):  # saves the current session
        settings = QtCore.QSettings("bbqmollusc", "stickiernotes")

        settings.remove("window" + str(self.id))
        if not (len(self.layoutchildren) == 1 and self.layoutchildren[0].displayText() == ""):
            settings.beginGroup("window" + str(self.id))
            settings.setValue("activeid", self.activeid)
            settings.setValue("lines", len(self.layoutchildren))
            if self.activeid < len(self.layoutchildren):
                paus = self.layoutchildren[self.activeid].cursorPosition()  # TODO Make this consistent tf
                settings.setValue("cursorPosition", paus)

            for i in range(len(self.layoutchildren)):
                settings.setValue(str(i), self.layoutchildren[i].displayText())
                settings.setValue(str(i) + "/refgroup", self.layoutchildren[i].refgroups)
                settings.setValue(str(i) + "/referenced", self.layoutchildren[i].referenced)
                settings.setValue(str(i) + "/referring", self.layoutchildren[i].referring)
                settings.setValue(str(i) + "/readonly", self.layoutchildren[i].isReadOnly())

            settings.endGroup()

    def getNearestNotReadOnly(self, index, direction):  # gets the nearest line that isn't read only given a starting index and direction to search
        i = 1
        while self.validIndex(index + direction * i) and self.layoutchildren[index + direction * i].isReadOnly():  # TODO make this count for a while loop
            i += 1
        return index + direction * i

    def deleteLine(self, temp):  # deletes a line, different from removing a line, which uses this function
        self.layoutchildren.remove(temp)
        texttemp = temp.refDisplayText()
        self.verticalLayout_2.removeWidget(temp)
        temp.deleteLater()
        temp = None
        return texttemp

    def loadSession(self):  # loads a session
        settings = QtCore.QSettings("bbqmollusc", "stickiernotes")

        settings.beginGroup("window" + str(self.id))

        if settings.value("lines", 1) > 0:
            temp = self.layoutchildren[0]
            self.deleteLine(temp)
            for i in range(settings.value("lines", 1)):
                val = str(settings.value(str(i), ""))
                lineEdit = ClickableLineEdit(self.centralwidget)
                lineEdit.setText(val)
                lineEdit.refgroups = settings.value(str(i) + "/refgroup", [])
                lineEdit.referenced = [int(j) for j in settings.value(str(i) + "/referenced", [])]
                lineEdit.referring = [int(j) for j in settings.value(str(i) + "/referring", [])]
                lineEdit.setObjectName("lineEdit_" + str(i))
                self.layoutchildren.append(lineEdit)
                self.verticalLayout_2.insertWidget(i, lineEdit, QtCore.Qt.AlignTop)
                self.initialize(i)
                read = (settings.value(str(i) + "/readonly", 'false')) == "true"
                if read:
                    lineEdit.setReadOnly(True)

        pos = self.getNearestNotReadOnly(len(self.layoutchildren) - 1, -1)
        self.layoutchildren[settings.value("activeid",
                                           pos)].setFocus()
        self.activeCell(settings.value("activeid", pos))

        self.active.setCursorPosition(settings.value("cursorPosition", 0))
        settings.endGroup()
        if "window" + str(self.id + 1) in settings.childGroups():
            self.createNewWindow()

    def activeCell(self, line):  # changes the current active cell, given either an index or a reference to the cell
        if (line == self.activeid or line==self.active) and self.active.hasFocus():
            return
        self.active.active = False
        self.active.focusToggle()
        if isinstance(line, int):
            self.active = self.layoutchildren[line]
            self.activeid = line
        else:
            self.active = line
            self.activeid = self.layoutchildren.index(self.active)
        self.active.active = True
        self.active.focusToggle()
        self.active.setFocus()

    def splitText(self, firstindex, secondindex, cursorposition):  # splits the text of the first index into that line and another line
        temptext = self.layoutchildren[firstindex].refDisplayText()
        self.layoutchildren[firstindex].setText(temptext[0:cursorposition])
        self.layoutchildren[secondindex].setText(temptext[cursorposition:])

        self.layoutchildren[secondindex].setCursorPosition(0)

        oldnumresults = self.layoutchildren[firstindex].numresults

        self.textCheck(firstindex)  # TODO also reset highlights
        self.layoutchildren[firstindex].setText(self.layoutchildren[firstindex].refToReal())
        self.layoutchildren[firstindex].animToggle(True)

        newnumresults = self.layoutchildren[firstindex].numresults
        secondindex = secondindex + (newnumresults - oldnumresults)  # TODO do this sort of update for anything with textcheck near it that has a possibility of failing due to rapidly updating things

        newtext = self.updateTextRefOffset(self.layoutchildren[secondindex].displayText(), True)
        self.layoutchildren[secondindex].setText(newtext)
        self.textCheck(secondindex)

    def updateTextRefOffset(self, text, add=True):
        offset = -1 if add else 1
        string = text
        m31 = [j for j in re.finditer(r'<(-[0-9]+)>', string)]
        newstring = ""
        for i in range(len(m31)):
            newstring += string[m31[i - 1].span(0)[1] - 1:m31[i].span(0)[0] + 1] + str(int(string[m31[i].span(0)[0] + 1:m31[i].span(0)[1] - 1]) + offset) if i > 0 \
                else string[:m31[i].span(0)[0] + 1] + str(int(string[m31[i].span(0)[0] + 1:m31[i].span(0)[1] - 1]) + offset)
        if len(m31) > 0:
            newstring += string[m31[len(m31) - 1].span(0)[1] - 1:]
        return newstring if newstring != "" else string

    def joinText(self, firstindex, secondindex):  # joins the text of two lines given their indices
        texttemp = self.layoutchildren[secondindex].refDisplayText()
        texttemp = self.updateTextRefOffset(texttemp, False)
        previoustextemp = self.layoutchildren[firstindex].refDisplayText()

        self.layoutchildren[firstindex].setText(previoustextemp + texttemp)
        self.layoutchildren[firstindex].setCursorPosition(len(previoustextemp))

        self.M3Match(firstindex)

    def validIndex(self, index):  # checks if an index is valid
        return 0 <= index < len(self.layoutchildren)

    def updateRefgroupRefOffsets(self, index, add=True):  # where index is the index of the added or removed element
        offset = -1 if add else 1
        start = index
        for li in range(start, len(self.layoutchildren)):
            line = self.layoutchildren[li]
            for ref in range(len(line.refgroups)):
                refnum = int(line.refgroups[ref][0][1:len(line.refgroups[ref][0]) - 1])
                if li + refnum + offset < index and refnum < 0:
                    line.refgroups[ref] = ("<" + str(refnum + offset) + ">", line.refgroups[ref][1], line.refgroups[ref][2],
                                           line.refgroups[ref][3])  # TODO might not be accounting for the fact that a change in digit numbers will cause an offset, ie 1 to 2 digit
                    line.referring[ref] = refnum + offset  # TODO refgroups and referring have uncomfortably close roles
                    self.layoutchildren[li + refnum + offset].remRef(li + offset)
                    self.layoutchildren[li + refnum + offset].addRef(li)
                else:
                    self.layoutchildren[li + refnum].remRef(li + offset)
                    self.layoutchildren[li + refnum].addRef(li)

    def removeRefgroup(self, index, currindex):  # TODO combine with prior function using a lambda function for the check and the sets
        line = self.layoutchildren[index]
        for ref in range(len(line.refgroups)):
            refnum = int(line.refgroups[ref][0][1:len(line.refgroups[ref][0]) - 1])
            if index + refnum == currindex:
                line.refgroups[ref] = ("<-" + str(0) + ">", line.refgroups[ref][1], line.refgroups[ref][2],
                                       line.refgroups[ref][3])  # TODO might not be accounting for the fact that a change in digit numbers will cause an offset, ie 1 to 2 digit
                line.referring[ref] = -0
                string = line.displayText()
                highlight = line.findHighlight(finalstart=line.fontMetrics().width(string[:line.refgroups[ref][3][0]]), finalwidth=line.fontMetrics().width(line.refgroups[ref][1]))
                highlight.initialstate["color"] = QColor('#ba8a8a')

    def newCell(self, index=None, command=False, num=1):  # creates *num* amount of new cells, specify whether new cells are output cells for a command or not
        if index is None:
            index = self.activeid
        self.scrollArea.verticalScrollBar().setValue(self.scrollArea.verticalScrollBar().maximum())  # TODO might result in errors if you don't want to make a new cell at the end of scroll
        for i in range(num):
            lineEdit = ClickableLineEdit(self.centralwidget)  # TODO make this shit work better, there's two others of em too

            latestindex = self.getNearestNotReadOnly(index, 1)

            lineEdit.setObjectName("lineEdit_" + str(len(self.layoutchildren)))
            self.verticalLayout_2.insertWidget(latestindex, lineEdit, QtCore.Qt.AlignTop)

            self.layoutchildren.insert(latestindex, lineEdit)
            self.initialize(latestindex)

            self.updateRefgroupRefOffsets(latestindex)  # TODO figure out whether this should be before or aftre all the shits

            if (not command):
                cursorposition = self.layoutchildren[self.activeid].cursorPosition()
                self.active.highlights = []
                self.activeCell(self.layoutchildren[latestindex])  # TODO put this above the other one perhaps
                self.splitText(index, latestindex, cursorposition)
            else:
                if latestindex < self.activeid:
                    self.activeid += 1
                self.layoutchildren[latestindex].setReadOnly(True)

    def remCell(self, index=None, command=False, keytype="",
                num=1):  # deletes num amount of cells, specify whether cells are of an output for a command or not, and also can specify if it is a backspace or delete key operation
        if index is None:
            index = self.activeid
        for i in range(num):
            ind = None  # index of the deleted line
            temp = None  # temporary reference to the deleted line
            if command:
                ind = index + 1  # TODO fix inefficiency with this for repeated deletions like for a command,
                # as since it deletes this index the update refgroups has to go through all the other lines below it, and repeats for every addition,
                # however if we just do the last index for the command, it'll only have to go through one each time as the prior one was already deleted
                # but also consider implications, as that would make it so that the updaterefgroups command also updates for all those elements that reference an alement prior to the last index
                temp = self.layoutchildren[index + 1]
                if ind < self.activeid:
                    self.activeid -= 1
            elif keytype == "backspace":
                if self.validIndex(index - 1) and self.active.cursorPosition() == 0:
                    reference = self.getNearestNotReadOnly(index, -1)
                    ind = index
                    temp = self.layoutchildren[index]

                    first = reference
                    second = index

                    self.activeCell(first)
                    self.joinText(first, second)
                else:
                    self.layoutchildren[index].backspace()
            elif keytype == "delete":
                if self.validIndex(index + 1) and self.active.cursorPosition() == len(self.active.displayText()):
                    reference = index
                    ind = self.getNearestNotReadOnly(index, 1)
                    temp = self.layoutchildren[ind]
                    self.joinText(reference, ind)
                else:
                    self.layoutchildren[index].del_()
            if temp:
                for j in temp.referring:
                    if j < 0:  # TODO make the whole check if valid ref part of the iterator generated by referring
                        self.layoutchildren[ind + j].remRef(ind)
                for k in temp.referenced:
                    self.removeRefgroup(k, ind)
                self.deleteLine(temp)
                self.updateRefgroupRefOffsets(ind, False)

        return

    def M1Match(self, tocheck):  # Matching for line commands
        check = self.layoutchildren[tocheck].realDisplayText()
        m = re.match('([A-Z-a-z-0-9]+)::(.*)', check)
        if m:
            command = m.group(1)
            expression = check[len(command) + 2:]
            if command in linecommands.commandslist:
                func = linecommands.commandslist[command]
                try:
                    output = func(expression)
                except:
                    output = "INVALID INPUT"
                if not isinstance(output, list):
                    output = [output]
                readonlyendindex = self.getNearestNotReadOnly(tocheck, 1) - 1
                readonlyamt = readonlyendindex - tocheck
                if readonlyamt < len(output):
                    self.newCell(index=tocheck, command=True, num=len(output) - readonlyamt)
                elif readonlyamt > len(output):
                    self.remCell(index=tocheck, command=True, num=readonlyamt - len(output))

                self.layoutchildren[tocheck].numresults = len(output)

                for i in range(len(output)):  # TODO get rid of residual info
                    self.layoutchildren[tocheck + i + 1].setText(str(output[i]))
                if command in linecommands.colors:
                    color = linecommands.colors[command]
                else:
                    color = Qt.darkRed
                self.layoutchildren[tocheck].addHighlight(AnimState("m1", 0, self.active.fontMetrics().width(command + "::"), color, 0, 1, color))
        elif self.validIndex(tocheck + 1) and self.layoutchildren[tocheck + 1].isReadOnly():
            i = self.getNearestNotReadOnly(tocheck, 1) - 1
            amt = i - tocheck
            self.remCell(index=tocheck, command=True, num=amt)

    def M2Match(self, tocheck):
        check = self.layoutchildren[tocheck].displayText()
        m2_1 = re.match(r'(.*):([A-Z-a-z-0-9]+):(.*)\s{0,}', check)
        m2 = re.match('(.*):([A-Z-a-z-0-9]+):(.*):', check)

        if m2_1 and not m2:
            heading = m2_1.group(1)
            command = m2_1.group(2)
            expression = m2_1.group(3)
            if command in linecommands.colors:
                color = linecommands.colors[command]
            else:
                color = Qt.darkRed
            finalcolor = QColor(color)
            finalcolor.setAlpha(0)
            self.layoutchildren[tocheck].addHighlight(
                AnimState("m21", self.active.fontMetrics().width(heading), self.active.fontMetrics().width(":" + command + ":" + expression), color, self.active.fontMetrics().width(heading),
                          self.active.fontMetrics().width(":" + command + ":" + expression), finalcolor))
        elif m2:
            heading = m2.group(1)
            command = m2.group(2)
            expression = m2.group(3)
            if command in linecommands.colors:
                color = linecommands.colors[command]
            else:
                color = Qt.darkRed
            finalcolor = QColor(color)
            finalcolor.setAlpha(0)
            if command in linecommands.commandslist:
                func = linecommands.commandslist[command]
                try:
                    output = func(expression)
                except:
                    output = "INVALID INPUT"
                self.layoutchildren[tocheck].addHighlight(
                    AnimState("m22", self.active.fontMetrics().width(heading), self.active.fontMetrics().width(":" + command + ":" + expression + ":"), color, self.active.fontMetrics().width(heading),
                              self.active.fontMetrics().width(":" + command + ":" + expression + ":"), finalcolor))
                before = self.layoutchildren[tocheck].displayText()[:len(m2.group(1))]
                after = self.layoutchildren[tocheck].displayText()[len(m2.group(1)) + 1 + len(m2.group(2)) + 1 + len(m2.group(3)) + 1:]
                self.layoutchildren[tocheck].setText(before + str(output) + after)

    def strRep(self, string, start, end, replacement):
        before = string[:start]
        after = string[end:]
        string = before + replacement + after  # TODO check if shits pass by reference actually tho
        return string

    def M3Match(self, tocheck):
        string = self.layoutchildren[tocheck].displayText()

        m31 = [j for j in re.finditer(r'<(-[0-9]+)>', string)]

        fadeindex = 1

        temprefgroups = []
        tempreferring = []
        offset = 0

        for m3 in m31:
            num = int(m3.group(1))
            if num>=0:
                continue
            validref = self.validIndex(tocheck + num)
            if validref:
                output = self.layoutchildren[tocheck + num].displayText()  # TODO maybe have this be a realdisplaytext instead
            else:
                continue

            tempreferring.append(num)
            self.layoutchildren[tocheck + num].addRef(tocheck)

            temprefgroups.append((m3.group(0), output, m3.span(0), (m3.span(0)[0] + offset, m3.span(0)[0] + len(output) + offset)))

            initialcolor = QColor("#b4ba8a") if self.layoutchildren[tocheck + num].isReadOnly() else QColor("#8ABAB2")

            finalcolor = QColor(initialcolor)
            finalcolor.setAlpha(0)
            self.layoutchildren[tocheck].addHighlight(AnimState("m3", self.active.fontMetrics().width(string[:m3.span(0)[0]]), self.active.fontMetrics().width(m3.group(0)), initialcolor,
                                                                self.active.fontMetrics().width(string[:m3.span(0)[0] + offset]), self.active.fontMetrics().width(output), finalcolor))

            offset += len(output) - (m3.span(0)[1] - m3.span(0)[0])

        for i in self.layoutchildren[tocheck].referring:
            if i not in tempreferring:
                self.layoutchildren[tocheck + i].remRef(tocheck)
        self.layoutchildren[tocheck].referring = tempreferring.copy()
        self.layoutchildren[tocheck].refgroups = temprefgroups.copy()

        self.layoutchildren[tocheck].refDisplayTextCache = self.layoutchildren[tocheck].refDisplayText()
        self.layoutchildren[tocheck].realDisplayTextCache = self.layoutchildren[tocheck].realDisplayText()

    def textCheck(self, tocheck=-1, recurse=True):

        if (tocheck == -1):
            tocheck = self.activeid

        self.layoutchildren[tocheck].highlights = []

        self.M2Match(tocheck)
        self.M3Match(tocheck)
        self.M1Match(tocheck)

        # TODO maybe make so all the ones use active or get the array thing

        endtocheck = self.getNearestNotReadOnly(tocheck, 1)
        if recurse:
            for i in range(tocheck, endtocheck):
                self.refRecurse(i)

        self.saveSession()

    def updateRefgroup(self, r, index):
        offset = 0
        for s in range(len(r.refgroups)):
            output = self.layoutchildren[index + int(r.refgroups[s][0][1:len(r.refgroups[s][0]) - 1])].realDisplayText()
            r.refgroups[s] = (r.refgroups[s][0], output, r.refgroups[s][2], (r.refgroups[s][2][0] + offset, r.refgroups[s][2][0] + len(output) + offset))
            offset += len(output) - (r.refgroups[s][2][1] - r.refgroups[s][2][0])

    def refTextRep(self, r):
        refdispcache = r.refDisplayTextCache
        newtext = r.refToReal(refdispcache)
        if len(r.refgroups) > 0:
            r.setText(newtext)
            return True
        else:
            return False

    def refRecurse(self, index):
        for r1 in self.layoutchildren[index].referenced:
            r = self.layoutchildren[r1]
            self.updateRefgroup(r, r1)
            anyreplaced = self.refTextRep(r)
            if (anyreplaced):
                self.M1Match(r1)

            self.refRecurse(r1)

    def cursorKey(self, direction):
        cursor = self.layoutchildren[self.activeid].cursorPosition()
        movement = self.getNearestNotReadOnly(self.activeid, direction)

        if self.validIndex(movement):
            check = self.layoutchildren[movement].displayText()
            m = re.match('([A-Z-a-z-0-9]+)::(.*)', check)
            offset = len(m.group(1)) + 2 if m else 0
            self.layoutchildren[movement].setCursorPosition(cursor + offset)
            self.activeCell(movement)

    def insertReference(self, referral):
        ind = self.layoutchildren.index(referral) - self.activeid
        string = self.strRep(self.active.displayText(), self.active.cursorPosition(), self.active.cursorPosition(), "<" + str(ind))
        self.layoutchildren[self.activeid].setText(string)

    def initialize(self, index):
        self.layoutchildren[index].returnPressed.connect(lambda: self.newCell(command=False))
        self.layoutchildren[index].clicked.connect(self.activeCell)

        self.layoutchildren[index].up.connect(lambda: self.cursorKey(-1))
        self.layoutchildren[index].down.connect(lambda: self.cursorKey(1))
        self.layoutchildren[index].textEdited.connect(lambda: self.textCheck())

        self.layoutchildren[index].backspacekey.connect(lambda: self.remCell(command=False, keytype="backspace"))
        self.layoutchildren[index].deletekey.connect(lambda: self.remCell(command=False, keytype="delete"))

        self.layoutchildren[index].identify.connect(self.insertReference)

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
