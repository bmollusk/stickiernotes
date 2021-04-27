from PyQt5 import QtCore, QtGui, QtWidgets
from asteval import Interpreter
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from commands_lib.instantanswerparser import query as GoogleQuery

aeval = Interpreter()
evalcolor = QColor("#FF5742")
googlecolor = QColor("#4285F4")

def evaluate(expression):
    output = aeval(expression)
    return output
def printexpression(expression):
    print(expression)
    output = "Printed!"
    return output
def splitup(expression):
    return expression.split(" ")
def instantanswer(expression):
    return GoogleQuery(expression)



commandslist = {"eval": evaluate, "print": printexpression,"split":splitup, "ans":instantanswer}
colors = {"eval": evalcolor, "ans":googlecolor}
