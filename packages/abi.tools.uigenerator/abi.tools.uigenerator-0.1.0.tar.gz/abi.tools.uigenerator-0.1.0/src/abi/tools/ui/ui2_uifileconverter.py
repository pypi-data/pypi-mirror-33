# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui\uifileconverter.ui'
#
# Created: Wed Jul 11 11:29:31 2018
#      by: pyside2-uic  running on PySide2 5.11.0a1
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_UIFileConverterDialog(object):
    def setupUi(self, UIFileConverterDialog):
        UIFileConverterDialog.setObjectName("UIFileConverterDialog")
        UIFileConverterDialog.resize(561, 392)
        self.verticalLayout = QtWidgets.QVBoxLayout(UIFileConverterDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.frame = QtWidgets.QFrame(UIFileConverterDialog)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.frame)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.uiFile_label = QtWidgets.QLabel(self.frame)
        self.uiFile_label.setObjectName("uiFile_label")
        self.horizontalLayout.addWidget(self.uiFile_label)
        self.uiFile_comboBox = QtWidgets.QComboBox(self.frame)
        self.uiFile_comboBox.setObjectName("uiFile_comboBox")
        self.horizontalLayout.addWidget(self.uiFile_comboBox)
        self.uiFile_pushButton = QtWidgets.QPushButton(self.frame)
        self.uiFile_pushButton.setObjectName("uiFile_pushButton")
        self.horizontalLayout.addWidget(self.uiFile_pushButton)
        self.verticalLayout.addWidget(self.frame)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.screen_label = QtWidgets.QLabel(UIFileConverterDialog)
        self.screen_label.setText("")
        self.screen_label.setObjectName("screen_label")
        self.verticalLayout.addWidget(self.screen_label)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem1)
        self.frame_2 = QtWidgets.QFrame(UIFileConverterDialog)
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.frame_2)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem2 = QtWidgets.QSpacerItem(457, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem2)
        self.quit_pushButton = QtWidgets.QPushButton(self.frame_2)
        self.quit_pushButton.setObjectName("quit_pushButton")
        self.horizontalLayout_2.addWidget(self.quit_pushButton)
        self.verticalLayout.addWidget(self.frame_2)

        self.retranslateUi(UIFileConverterDialog)
        QtCore.QObject.connect(self.quit_pushButton, QtCore.SIGNAL("clicked()"), UIFileConverterDialog.accept)
        QtCore.QMetaObject.connectSlotsByName(UIFileConverterDialog)

    def retranslateUi(self, UIFileConverterDialog):
        UIFileConverterDialog.setWindowTitle(QtWidgets.QApplication.translate("UIFileConverterDialog", "UI File Converter", None, -1))
        self.uiFile_label.setText(QtWidgets.QApplication.translate("UIFileConverterDialog", "UI File:", None, -1))
        self.uiFile_pushButton.setText(QtWidgets.QApplication.translate("UIFileConverterDialog", "Generate", None, -1))
        self.quit_pushButton.setText(QtWidgets.QApplication.translate("UIFileConverterDialog", "Quit", None, -1))

