# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui\uifileconverter.ui'
#
# Created: Wed Jul 11 12:22:50 2018
#      by: pyside-uic 0.2.15 running on PySide 1.2.4
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_UIFileConverterDialog(object):
    def setupUi(self, UIFileConverterDialog):
        UIFileConverterDialog.setObjectName("UIFileConverterDialog")
        UIFileConverterDialog.resize(561, 392)
        self.verticalLayout = QtGui.QVBoxLayout(UIFileConverterDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.frame = QtGui.QFrame(UIFileConverterDialog)
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.horizontalLayout = QtGui.QHBoxLayout(self.frame)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.uiFile_label = QtGui.QLabel(self.frame)
        self.uiFile_label.setObjectName("uiFile_label")
        self.horizontalLayout.addWidget(self.uiFile_label)
        self.uiFile_comboBox = QtGui.QComboBox(self.frame)
        self.uiFile_comboBox.setObjectName("uiFile_comboBox")
        self.horizontalLayout.addWidget(self.uiFile_comboBox)
        self.uiFile_pushButton = QtGui.QPushButton(self.frame)
        self.uiFile_pushButton.setObjectName("uiFile_pushButton")
        self.horizontalLayout.addWidget(self.uiFile_pushButton)
        self.verticalLayout.addWidget(self.frame)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.screen_label = QtGui.QLabel(UIFileConverterDialog)
        self.screen_label.setText("")
        self.screen_label.setObjectName("screen_label")
        self.verticalLayout.addWidget(self.screen_label)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem1)
        self.frame_2 = QtGui.QFrame(UIFileConverterDialog)
        self.frame_2.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtGui.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.frame_2)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem2 = QtGui.QSpacerItem(457, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem2)
        self.quit_pushButton = QtGui.QPushButton(self.frame_2)
        self.quit_pushButton.setObjectName("quit_pushButton")
        self.horizontalLayout_2.addWidget(self.quit_pushButton)
        self.verticalLayout.addWidget(self.frame_2)

        self.retranslateUi(UIFileConverterDialog)
        QtCore.QObject.connect(self.quit_pushButton, QtCore.SIGNAL("clicked()"), UIFileConverterDialog.accept)
        QtCore.QMetaObject.connectSlotsByName(UIFileConverterDialog)

    def retranslateUi(self, UIFileConverterDialog):
        UIFileConverterDialog.setWindowTitle(QtGui.QApplication.translate("UIFileConverterDialog", "UI File Converter", None, QtGui.QApplication.UnicodeUTF8))
        self.uiFile_label.setText(QtGui.QApplication.translate("UIFileConverterDialog", "UI File:", None, QtGui.QApplication.UnicodeUTF8))
        self.uiFile_pushButton.setText(QtGui.QApplication.translate("UIFileConverterDialog", "Generate", None, QtGui.QApplication.UnicodeUTF8))
        self.quit_pushButton.setText(QtGui.QApplication.translate("UIFileConverterDialog", "Quit", None, QtGui.QApplication.UnicodeUTF8))

