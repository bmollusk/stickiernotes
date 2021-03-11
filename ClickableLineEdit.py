from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtCore import Qt, QVariantAnimation, QEasingCurve
from PyQt5.QtGui import QPainter, QBrush, QPen, QColor, QFontMetrics
import re
import linecommands


class ClickableLineEdit(QLineEdit):
    def __init__(self, parent=None, grandparent=None):
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
        self.grandparent = grandparent
        self.setStyleSheet(stylesheet)
        self.anim = QLineAnimation(self)
        self.anim.valueChanged.connect(self.updateSelf)

        self.anim2 = QLineAnimation(self)
        self.anim2.valueChanged.connect(self.updateSelf2)#???

        self.anim3 = QLineAnimation(self)
        self.anim3.valueChanged.connect(self.updateSelf3)  # ???

        self.fadestate = 0
        self.fades = []
        #self.latest = -1
        self.latestspan = ()

        self.fade = None

        self.command = False
        #The current margins
        self.value = 0
        self.permvalue=self.value

        self.refgroups = []

        self.referenced = []
        self.referring = []
        #TODO why these shits in different forms

        self.validity = []

        self.ctrl = False

        self.active = False
    clicked = pyqtSignal()
    identify = pyqtSignal(object)

    def mousePressEvent(self, event):
        if self.grandparent.layoutchildren[self.grandparent.activeid].ctrl and self.grandparent.layoutchildren[self.grandparent.activeid]!=self:
            #self.grandparent.layoutchildren[self.grandparent.activeid].ctrl = False
            self.identify.emit(self)
        else:
            self.clicked.emit()
        QLineEdit.mousePressEvent(self, event)

    up = pyqtSignal()
    down = pyqtSignal()
    backspacekey = pyqtSignal()
    deletekey = pyqtSignal()


    def keyPressEvent(self, event):

        if event.key() == Qt.Key_Backspace:
            self.backspacekey.emit()
            self.command = False
            return
        elif event.key() == Qt.Key_Delete:
            self.deletekey.emit()
            self.command = False
            return
        super(ClickableLineEdit, self).keyPressEvent(event)

        # print("event", event.key())
        if (event.key() == Qt.Key_Up):
            # print("up")
            self.up.emit()
            return
        elif (event.key() == Qt.Key_Down):
            # print("down")
            self.down.emit()
            return
        elif (event.key()== Qt.Key_Control):
            self.ctrl = True

        return
    def keyReleaseEvent(self, event):
        super(ClickableLineEdit, self).keyReleaseEvent(event)
        if(event.key()==Qt.Key_Control):
            self.ctrl = False
    def getNormText(self):
        #TODO figure out if you need to check if the current cell is active and just return the actual normal text there or nah
        chopped = []
        # DONETODO rn this is a bunch of ifs, which is bad, make this not a bunch of ifs
        for i in range(0, len(self.refgroups)):
            if i == 0 and i == len(self.refgroups) - 1:
                before = self.displayText()[:self.refgroups[i][2][0]]
                chopped.append(before)
                output = self.refgroups[i][1]
                chopped.append(output)
                after = self.displayText()[self.refgroups[i][2][1]:]
                chopped.append(after)
            elif i == 0:
                before = self.displayText()[:self.refgroups[i][2][0]]
                chopped.append(before)
                output = self.refgroups[i][1]
                chopped.append(output)
                after = self.displayText()[self.refgroups[i][2][1]:self.refgroups[i + 1][2][0]]
                chopped.append(after)
            elif i == len(self.refgroups) - 1:
                # before = self.displayText()[self.refgroups[i - 1][2][1]:self.refgroups[i][2][0]]
                # chopped.append(before)
                output = self.refgroups[i][1]
                chopped.append(output)
                after = self.displayText()[self.refgroups[i][2][1]:]
                chopped.append(after)
            else:
                # before=self.displayText()[self.refgroups[i-1][2][1]:self.refgroups[i][2][0]]
                # chopped.append(before)
                output = self.refgroups[i][1]
                chopped.append(output)
                after = self.displayText()[self.refgroups[i][2][1]:self.refgroups[i + 1][2][0]]
                chopped.append(after)
        return chopped
    def realDisplayText(self):
        if len(self.refgroups)>0 and self.active:
            return "".join(self.getNormText())
        else:
            return self.displayText()
    def refDisplayText(self):
        if len(self.refgroups)>0 and not self.active:
            return "".join(self.getRefText())
        else:
            return self.displayText()
    def getRefText(self):
        chopped = []
        # TODO rn this is a bunch of ifs, which is bad, make this not a bunch of ifs
        for i in range(0, len(self.refgroups)):
            if i == 0 and i == len(self.refgroups) - 1:
                before = self.displayText()[:self.refgroups[i][3][0]]
                chopped.append(before)
                output = str(self.refgroups[i][0])
                chopped.append(output)
                after = self.displayText()[self.refgroups[i][3][1]:]
                chopped.append(after)
            elif i == 0:
                before = self.displayText()[:self.refgroups[i][3][0]]
                chopped.append(before)
                output = str(self.refgroups[i][0])
                chopped.append(output)
                after = self.displayText()[self.refgroups[i][3][1]:self.refgroups[i + 1][3][0]]
                chopped.append(after)
            elif i == len(self.refgroups) - 1:
                # before = self.displayText()[self.refgroups[i - 1][3][1]:self.refgroups[i][3][0]-1]
                # chopped.append(before)
                output = str(self.refgroups[i][0])
                chopped.append(output)
                after = self.displayText()[self.refgroups[i][3][1]:]
                chopped.append(after)
            else:
                # before = self.displayText()[self.refgroups[i - 1][3][1]:self.refgroups[i][3][0]-1]
                # chopped.append(before)
                output = str(self.refgroups[i][0])
                chopped.append(output)
                after = self.displayText()[self.refgroups[i][3][1]:self.refgroups[i + 1][3][0]]
                chopped.append(after)
        return chopped
    def focusOutEvent(self, event):
        super(ClickableLineEdit, self).focusOutEvent(event)

        check = self.displayText()
        m = re.match('([A-Z-a-z-0-9]+)::(.*)', check)
        self.active = False
        if m:
            command = m.group(1)
            #print(command)
            #charlength=self.fontMetrics().boundingRect(command+"::").width()

            charlength=self.fontMetrics().width(command+"::")

            #charlength = len(command) + 2

            # self.setTextMargins(-5*charlength, 0, 0, 0)
            #self.doAnim(-5 * charlength)  # DONETODO make this more accurate to spacing

            self.doAnim(self.getTextMargins()[0],-1*charlength)
        if(len(self.refgroups)>0):
            chopped = self.getNormText()
            newstr="".join(chopped)
            self.setText(newstr)

    def getLineTextMargins(self):
        self.getTextMargins()

    def setLineTextMargins(self, margins):
        self.setTextMargins(margins)

    def focusInEvent(self, event):
        super(ClickableLineEdit, self).focusInEvent(event)
        # self.setTextMargins(0, 0, 0, 0)
        self.doAnim(self.getTextMargins()[0],0)
        self.active = True #TODO remove redundant uses?
        if (len(self.refgroups) > 0):
            chopped = self.getRefText()
            newstr = "".join(chopped)
            self.setText(newstr)



    # def commandDone(self):
    #      #DONETODO fix this shit bruv it only kinda works
    #     text=self.displayText()
    #     self.setTextMargins(-10, 0, 10, 0)
    #     print("cunt",text)
    def doAnim(self, start, end):
        self.anim.setStartValue(start)
        self.anim.setEndValue(end)
        self.anim.setDuration(100)
        self.anim.setEasingCurve(QEasingCurve.InOutQuad)
        self.anim.start()

    def doAnim2(self, start, end):
        self.anim2.setStartValue(start)
        self.anim2.setEndValue(end)
        self.anim2.setDuration(200)
        self.anim2.setEasingCurve(QEasingCurve.InOutQuad)
        self.anim2.start()

    def doAnim3(self, start, end):
        self.anim3.setStartValue(start)
        self.anim3.setEndValue(end)
        self.anim3.setDuration(300)
        self.anim3.setEasingCurve(QEasingCurve.InOutQuad)
        self.anim3.start()

    def updateSelf(self, value):
        #print("br",value)
        check = self.displayText()
        m = re.match('([A-Z-a-z-0-9]+)::(.*)', check)
        if m:
            command = m.group(1)
            #charlength = len(command) + 2
            charlength = self.fontMetrics().width(command + "::")
            if(value==-1*charlength):
                self.value = 1 #TODO make this not hardcoded either
            else:
                self.value = self.permvalue+value
        self.update()
        self.setTextMargins(value, 0, 0, 0)

    def updateSelf2(self,value):
        self.fades[2].setAlpha(value)
        self.update()

    def updateSelf3(self,value):
        self.fade.setAlpha(value)
        self.update()

    def addRef(self,reference):
        if reference not in self.referenced:
            self.referenced.append(reference)
    def remRef(self,reference):
        if reference in self.referenced:
            self.referenced.remove(reference)

    def paintEvent(self, event):
        painter = QPainter(self)
        inputcolor = QColor("#1D3A5A")
        outputcolor = QColor("#264965")
        if(self.isReadOnly()):
            painter.setPen(QPen(outputcolor, 16, Qt.SolidLine))
        else:
            painter.setPen(QPen(inputcolor, 16, Qt.SolidLine))
        painter.drawLine(0, 8, 1000000, 8)  # TODO make this not work retardedly, along with the other paints
        #print("painted",self.value)

        check = self.displayText()

        m = re.match('([A-Z-a-z-0-9]+)::(.*)', check)

        painter.setPen(Qt.transparent) #see above todo

        #print(self.command)
        if m and not self.command:
            self.command = True
            command = m.group(1)
            #charlength = len(command) + 2
            charlength = self.fontMetrics().width(command + "::")
            # self.setTextMargins(-5*charlength, 0, 0, 0)
            self.value=1*charlength#DONETODO make this more accurate to spacing
            self.permvalue=self.value
        elif not m and not self.command:
            self.value=0
            self.permvalue=self.value
        check = self.displayText()
        m = re.match('([A-Z-a-z-0-9]+)::(.*)', check)#TODO figure out why this happens twice
        if m:
            command = m.group(1)
            if command in linecommands.colors:
                painter.setBrush(linecommands.colors[command])
            else:
                painter.setBrush(Qt.darkRed)

        painter.drawRect(-10,-50,12+self.value,100)#TODO make all of the paints less hardcoded


        m2_1 = re.match(r'(.*):([A-Z-a-z-0-9]+):(.*)\s{0,}', check)#TODO figure out if you want to highlight spaces or naw
        m2 = re.match('(.*):([A-Z-a-z-0-9]+):(.*):', check)

        if m2_1 and not m2:
            heading = m2_1.group(1)
            command = m2_1.group(2)
            #charlength = len(command) + 2
            ivalue = self.fontMetrics().width(heading)
            fvalue = self.fontMetrics().width(command+m2_1.group(3))
            if command in linecommands.colors:
                color = linecommands.colors[command]
            else:
                color = Qt.darkRed
            painter.setBrush(color)
            painter.drawRect(ivalue,-50,12+fvalue,100)
            self.fades = [ivalue,fvalue,QColor(color)]
        elif len(self.fades)==4 and isinstance(self.fades[3],str):
            self.fadestate = 1
            value = self.fades.pop()
            self.fades[1] = self.fontMetrics().width(value)
            self.doAnim2(self.fades[2].alpha(), 0)
        if(self.fadestate==1):#TODO make fadestate into a boolean
            painter.setBrush(self.fades[2].lighter())
            painter.drawRect(self.fades[0],-50,10+self.fades[1],100)
            if(self.fades[2].alpha()==0):
                self.fades = []
                self.fadestate = 0

        #it checks for an incomplete reference, and only highlights it then, but once it's done it does a one time animation where it does a glow
        #and then from then on it uses the reference groups for the spans for animations

        if self.active:
            color = QColor("#8ABAB2")
            for r in self.refgroups:
                heading = self.displayText()[:r[2][0]]
                reference = self.displayText()[r[2][0]:r[2][1]]
                ivalue = self.fontMetrics().width(heading)
                fvalue = self.fontMetrics().width(reference)
                painter.setBrush(color)
                painter.drawRect(ivalue, -50, 2+fvalue, 100)
            self.fade = QColor(color)
        elif self.fade != None:
            self.fadestate = 2
            self.doAnim3(self.fade.alpha(),0)
        if self.fadestate==2:
            for r in self.refgroups:
                heading = self.displayText()[:r[3][0]]
                reference = self.displayText()[r[3][0]:r[3][1]]
                ivalue = self.fontMetrics().width(heading)
                fvalue = self.fontMetrics().width(reference)
                painter.setBrush(self.fade.darker())
                painter.drawRect(ivalue, -50, 5+fvalue, 100)
            if (self.fade.alpha() == 0):
                self.fade = None
                self.fadestate = 0




        #print(self.fades)
        m3_1 = re.match(r'(.*)<(-[0-9]+)([^>]+|$)', check)
        if m3_1:
            heading = m3_1.group(1)
            reference = m3_1.group(2)
            ivalue = self.fontMetrics().width(heading)
            fvalue = self.fontMetrics().width(reference)
            color = QColor("#878785")
            painter.setBrush(color)
            painter.drawRect(ivalue, -50, 12+fvalue, 100)
            self.fades = [ivalue, fvalue, QColor(color)]
            self.latestspan = m3_1.span(2)#TODO make this not in the cosmetic section plz

            #print("m31 match!!")
        elif len(self.fades) == 4 and isinstance(self.fades[3],bool):
            self.fadestate = 3

            # self.validity = self.fades[3:]
            # self.fades = self.fades[:3]
            # try:
            #     value = self.validity[self.latest]
            # except:
            #     value = "AAAAAAAAAAAAA

            value = self.fades.pop()
            #print("fade 4")
            if value:
                self.fades[2] = QColor("#33A67C")
            else:
                self.fades[2] = QColor("#BF2533")
            self.doAnim2(self.fades[2].alpha(), 0)
        if (self.fadestate == 3):  # TODO make fadestate into a boolean
            painter.setBrush(self.fades[2].lighter())
            painter.drawRect(self.fades[0], -50, 20+self.fades[1], 100)
            if (self.fades[2].alpha() == 0):
                #print("faded away")
                self.fades = []
                self.fadestate = 0
                self.validity = []
                self.latest = -1
                self.latestspan = ()
            #print("fade away")


        super(ClickableLineEdit, self).paintEvent(event)



class QLineAnimation(QVariantAnimation):
    def __init__(self, line, parent=None):
        super().__init__(parent)
        self.line = line

    def updateCurrentValue(self, value):
        super(QLineAnimation, self).updateCurrentValue(value)
        if not value == 0:
            #print("uh", value)
            pass
