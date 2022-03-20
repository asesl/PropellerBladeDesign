# -*- coding: utf-8 -*-

from __future__ import division

import math
import sys

from os import listdir
from os.path import isfile, join
import pathlib

from PySide import QtCore, QtGui

import FreeCAD as app
import FreeCADGui as gui
import Part

import propeller_generator.propeller_blade as pb

def tr(context, text):
    try:
        _encoding = QtGui.QApplication.UnicodeUTF8
        return QtGui.QApplication.translate(context, text, None, _encoding)
    except AttributeError:
        return QtGui.QApplication.translate(context, text, None)


def say(s):
    app.Console.PrintMessage(str(s) + '\n')


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("PropellerBlade")
        self.dia = Dialog
        self.gridLayoutWidget = QtGui.QWidget(Dialog)
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout = QtGui.QGridLayout(self.gridLayoutWidget)
        #self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")

        self.labelHelp = QtGui.QLabel(self.gridLayoutWidget)
        self.labelHelp.setObjectName('labelHelp')
        self.gridLayout.addWidget(self.labelHelp, 0, 0, 1, 2)

        self.labelSpanLength = QtGui.QLabel(self.gridLayoutWidget)
        self.labelSpanLength.setObjectName('labelSpanLength')
        self.gridLayout.addWidget(self.labelSpanLength, 1, 0)
        fui = gui.UiLoader()
        self.lineEditSpanLength = fui.createWidget('Gui::InputField')
        self.lineEditSpanLength.setObjectName('lineEditSpanLength')
        self.gridLayout.addWidget(self.lineEditSpanLength, 1, 1)

        self.labelGeometryFile = QtGui.QToolButton()
        self.labelGeometryFile.clicked.connect(self.onInputFileButtonClicked)
        self.labelGeometryFile.setObjectName('FileSelectionButton')
        self.gridLayout.addWidget(self.labelGeometryFile, 2, 0)
        self.lineEditGeometryFile = QtGui.QLineEdit(self.gridLayoutWidget)
        self.lineEditGeometryFile.setObjectName('lineEditGeometryFile')
        self.gridLayout.addWidget(self.lineEditGeometryFile, 2, 1)


        self.labelFoilType = QtGui.QLabel(self.gridLayoutWidget)
        self.labelFoilType.setObjectName('labelFoilType')
        self.gridLayout.addWidget(self.labelFoilType, 3, 0)
        self.dropdownFoilType = QtGui.QComboBox()
        airFoilsPath = str(pathlib.Path(__file__).absolute().parents[0]) + "/Air_Foils"
        self.dropdownFoilType.addItems([f for f in listdir(airFoilsPath) if isfile(join(airFoilsPath, f))])
        #self.dropdownFoilType.clicked.connect(self.onInputFileButtonClicked)
        self.dropdownFoilType.setObjectName('FileSelectionButton')
        self.gridLayout.addWidget(self.dropdownFoilType, 3, 1)
        

        self.labelType = QtGui.QLabel(self.gridLayoutWidget)
        self.labelType.setObjectName('labelType')
        self.gridLayout.addWidget(self.labelType, 4, 0)
        self.typesWidget = QtGui.QWidget(self.gridLayoutWidget)
        layoutType = QtGui.QVBoxLayout(self.typesWidget)
        self.radioLeftHand = QtGui.QRadioButton()
        self.radioRightHand = QtGui.QRadioButton()

        layoutType.addWidget(self.radioLeftHand)
        layoutType.addWidget(self.radioRightHand)

        self.radioLeftHand.setChecked(True)
        self.gridLayout.addWidget(self.typesWidget, 4, 1)

        self.buttonBox = QtGui.QDialogButtonBox(self.gridLayoutWidget)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons \
            (QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 5, 1)

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(self.makeSomething)
        self.buttonBox.rejected.connect(self.makeNothing)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(tr('PropellerBlade', 'Propeller Blade Creator'))
        self.labelSpanLength.setText(tr('PropellerBlade', 'Blade Span [mm]'))
        self.labelGeometryFile.setText(tr('PropellerBlade',
                                     'Geometry File Name...'))
        self.labelFoilType.setText(tr('PropellerBlade','Foil Type:'))
        self.labelHelp.setText(tr('PropellerBlade',
                                  'This Macro creates \na single propeller\nblade'))
        self.labelType.setText(tr('PropellerBlade', 'Left or Right Hand'))
        self.radioLeftHand.setText(tr('PropellerBlade', 'Left Handed'))
        self.radioRightHand.setText(tr('PropellerBlade', 'Right Handed'))


    def onInputFileButtonClicked(self):
        filename, filter = QtGui.QFileDialog.getOpenFileName()#parent=self, caption='Open file', dir='.')#, filter='Geometry Files (*.csv)')

        if filename:
            self.lineEditGeometryFile.setText(filename)

    def makeSomething(self):
        say('Accepted! Span Length: {} with Geometry File {}'.format(
           self.lineEditSpanLength.property("text"),
           self.lineEditGeometryFile.text()))

        doc = app.activeDocument()
        if doc is None:
            doc = app.newDocument()

        foil_type = pathlib.Path(self.dropdownFoilType.currentText()).stem
        say("Foil Type: " + foil_type)
        geo_file_name = self.lineEditGeometryFile.text()
        span_length = float(self.lineEditSpanLength.text())
        if self.radioLeftHand.isChecked():
            # Left = -1, Right = 1
            left_or_right = -1
        else:
            left_or_right = 1

        myPropeller = pb.PropellerBlade(foil_type, geo_file_name, span_length, left_or_right, doc)
        myPropeller.make_MavicPro()
        self.dia.close()
        doc.recompute()

    def makeNothing(self):
        say('Rejected!')
        self.dia.close()


def showDialog():
    d = QtGui.QWidget()
    d.ui = Ui_Dialog()
    d.ui.setupUi(d)
   # d.ui.lineEditGeometryFile.setText('2')
    #d.ui.lineEditSpanLength.setProperty('text', '2 m')

    d.resize(500,500)
    d.show()
