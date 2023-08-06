# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'qtpad/gui_search.ui'
#
# Created by: PyQt5 UI code generator 5.11.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(500, 100)
        self.gridLayout = QtWidgets.QGridLayout(Form)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(Form)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.searchFindLine = QtWidgets.QLineEdit(Form)
        self.searchFindLine.setObjectName("searchFindLine")
        self.gridLayout.addWidget(self.searchFindLine, 0, 1, 1, 1)
        self.searchFindButton = QtWidgets.QPushButton(Form)
        self.searchFindButton.setObjectName("searchFindButton")
        self.gridLayout.addWidget(self.searchFindButton, 0, 2, 1, 1)
        self.searchFindAllButton = QtWidgets.QPushButton(Form)
        self.searchFindAllButton.setObjectName("searchFindAllButton")
        self.gridLayout.addWidget(self.searchFindAllButton, 0, 3, 1, 1)
        self.label_2 = QtWidgets.QLabel(Form)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.searchReplaceLine = QtWidgets.QLineEdit(Form)
        self.searchReplaceLine.setObjectName("searchReplaceLine")
        self.gridLayout.addWidget(self.searchReplaceLine, 1, 1, 1, 1)
        self.searchReplaceButton = QtWidgets.QPushButton(Form)
        self.searchReplaceButton.setObjectName("searchReplaceButton")
        self.gridLayout.addWidget(self.searchReplaceButton, 1, 2, 1, 1)
        self.searchReplaceAllButton = QtWidgets.QPushButton(Form)
        self.searchReplaceAllButton.setObjectName("searchReplaceAllButton")
        self.gridLayout.addWidget(self.searchReplaceAllButton, 1, 3, 1, 1)
        self.searchWholeBox = QtWidgets.QCheckBox(Form)
        self.searchWholeBox.setObjectName("searchWholeBox")
        self.gridLayout.addWidget(self.searchWholeBox, 2, 0, 1, 1)
        self.searchCaseBox = QtWidgets.QCheckBox(Form)
        self.searchCaseBox.setObjectName("searchCaseBox")
        self.gridLayout.addWidget(self.searchCaseBox, 2, 1, 1, 1)
        self.searchWrapBox = QtWidgets.QCheckBox(Form)
        self.searchWrapBox.setChecked(True)
        self.searchWrapBox.setObjectName("searchWrapBox")
        self.gridLayout.addWidget(self.searchWrapBox, 2, 2, 1, 2)

        self.retranslateUi(Form)
        self.searchFindLine.returnPressed.connect(self.searchFindButton.click)
        self.searchReplaceLine.returnPressed.connect(self.searchReplaceButton.click)
        QtCore.QMetaObject.connectSlotsByName(Form)
        Form.setTabOrder(self.searchFindLine, self.searchReplaceLine)
        Form.setTabOrder(self.searchReplaceLine, self.searchFindButton)
        Form.setTabOrder(self.searchFindButton, self.searchReplaceButton)
        Form.setTabOrder(self.searchReplaceButton, self.searchReplaceAllButton)
        Form.setTabOrder(self.searchReplaceAllButton, self.searchCaseBox)
        Form.setTabOrder(self.searchCaseBox, self.searchWholeBox)
        Form.setTabOrder(self.searchWholeBox, self.searchWrapBox)
        Form.setTabOrder(self.searchWrapBox, self.searchFindAllButton)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label.setText(_translate("Form", "Find"))
        self.searchFindButton.setText(_translate("Form", "Find next"))
        self.searchFindAllButton.setText(_translate("Form", "Find all"))
        self.label_2.setText(_translate("Form", "Replace with"))
        self.searchReplaceButton.setText(_translate("Form", "Replace"))
        self.searchReplaceAllButton.setText(_translate("Form", "Replace all"))
        self.searchWholeBox.setText(_translate("Form", "Whole words"))
        self.searchCaseBox.setText(_translate("Form", "Case sensitive"))
        self.searchWrapBox.setText(_translate("Form", "Wrap search"))

