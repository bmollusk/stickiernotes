from PyQt5 import QtCore, QtGui, QtWidgets
from asteval import Interpreter
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

aeval = Interpreter()
evalcolor = QColor("#FF5742")

def evaluate(expression):
    output = aeval(expression)
    return output
def printexpression(expression):
    print(expression)
    output = "Printed!"
    return output
def splitup(expression):
    return expression.split(" ")


commandslist = {"eval": evaluate, "print": printexpression,"split":splitup}
colors = {"eval": evalcolor}