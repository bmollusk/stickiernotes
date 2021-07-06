from PyQt5 import QtCore, QtGui, QtWidgets
from asteval import Interpreter
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from PyQt5.QtGui import QColor
from PyQt5.QtNetwork import QNetworkAccessManager
from commands_lib.instantanswerparser import query as GoogleQuery

def instant(func):
    def wrapper(*args,**kwargs):
        expression = kwargs['expression'] if 'expression' in kwargs else args[1]
        output = func(args[0],expression)
        args[0].commandfinished.emit(output)
    return wrapper

def onenter(func):
    def wrapper(*args,**kwargs):
        loading = kwargs['loading'] if 'loading' in kwargs else args[2]
        if loading:
            args[0].commandfinished.emit([])
        else:
            expression = kwargs['expression'] if len(args) == 1 else args[1]
            func(args[0], expression)
    return wrapper

class CommandHandler(QObject):
    def __init__(self):
        super().__init__()
        self.commandslist = {"eval": self.evaluate, "print": self.printexpression,"split":self.splitup, "ans":self.instantanswer}

        evalcolor = QColor("#FF5742")
        googlecolor = QColor("#4285F4")
        self.colors = {"eval": evalcolor, "ans":googlecolor}

        self.aeval = Interpreter()
        self.network = QNetworkAccessManager()

    commandfinished = pyqtSignal(object)

    @instant
    def evaluate(self, expression):  # TODO make the amount of fields variable
        output = self.aeval(expression)
        return output

    @instant
    def printexpression(self, expression):
        print(self, expression)
        output = "Printed!"
        return output

    @instant
    def splitup(self, expression):
        return expression.split(" ")

    @onenter
    def instantanswer(self, expression):
        GoogleQuery(self, expression)
