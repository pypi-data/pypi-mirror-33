# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'src\abi\tools\ui\uifileconverter.ui'
#
# Created: Thu Jul 12 16:54:59 2018
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
        self.ui_frame = QtWidgets.QFrame(UIFileConverterDialog)
        self.ui_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.ui_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.ui_frame.setObjectName("ui_frame")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.ui_frame)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.uiFile_label = QtWidgets.QLabel(self.ui_frame)
        self.uiFile_label.setObjectName("uiFile_label")
        self.horizontalLayout.addWidget(self.uiFile_label)
        self.uiFile_comboBox = QtWidgets.QComboBox(self.ui_frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiFile_comboBox.sizePolicy().hasHeightForWidth())
        self.uiFile_comboBox.setSizePolicy(sizePolicy)
        self.uiFile_comboBox.setObjectName("uiFile_comboBox")
        self.horizontalLayout.addWidget(self.uiFile_comboBox)
        self.uiFile_pushButton = QtWidgets.QPushButton(self.ui_frame)
        self.uiFile_pushButton.setObjectName("uiFile_pushButton")
        self.horizontalLayout.addWidget(self.uiFile_pushButton)
        self.verticalLayout.addWidget(self.ui_frame)
        self.sideBySide_groupBox = QtWidgets.QGroupBox(UIFileConverterDialog)
        self.sideBySide_groupBox.setCheckable(True)
        self.sideBySide_groupBox.setObjectName("sideBySide_groupBox")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.sideBySide_groupBox)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.outDir_label = QtWidgets.QLabel(self.sideBySide_groupBox)
        self.outDir_label.setObjectName("outDir_label")
        self.horizontalLayout_3.addWidget(self.outDir_label)
        self.outDir_lineEdit = QtWidgets.QLineEdit(self.sideBySide_groupBox)
        self.outDir_lineEdit.setObjectName("outDir_lineEdit")
        self.horizontalLayout_3.addWidget(self.outDir_lineEdit)
        self.outDir_pushButton = QtWidgets.QPushButton(self.sideBySide_groupBox)
        self.outDir_pushButton.setObjectName("outDir_pushButton")
        self.horizontalLayout_3.addWidget(self.outDir_pushButton)
        self.verticalLayout.addWidget(self.sideBySide_groupBox)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.screen_label = QtWidgets.QLabel(UIFileConverterDialog)
        self.screen_label.setText("")
        self.screen_label.setObjectName("screen_label")
        self.verticalLayout.addWidget(self.screen_label)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem1)
        self.quit_frame = QtWidgets.QFrame(UIFileConverterDialog)
        self.quit_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.quit_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.quit_frame.setObjectName("quit_frame")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.quit_frame)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem2 = QtWidgets.QSpacerItem(457, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem2)
        self.quit_pushButton = QtWidgets.QPushButton(self.quit_frame)
        self.quit_pushButton.setObjectName("quit_pushButton")
        self.horizontalLayout_2.addWidget(self.quit_pushButton)
        self.verticalLayout.addWidget(self.quit_frame)

        self.retranslateUi(UIFileConverterDialog)
        QtCore.QObject.connect(self.quit_pushButton, QtCore.SIGNAL("clicked()"), UIFileConverterDialog.close)
        QtCore.QMetaObject.connectSlotsByName(UIFileConverterDialog)

    def retranslateUi(self, UIFileConverterDialog):
        UIFileConverterDialog.setWindowTitle(QtWidgets.QApplication.translate("UIFileConverterDialog", "UI File Converter", None, -1))
        self.uiFile_label.setText(QtWidgets.QApplication.translate("UIFileConverterDialog", "UI File:", None, -1))
        self.uiFile_pushButton.setText(QtWidgets.QApplication.translate("UIFileConverterDialog", "Generate", None, -1))
        self.sideBySide_groupBox.setTitle(QtWidgets.QApplication.translate("UIFileConverterDialog", "side-by-side output", None, -1))
        self.outDir_label.setText(QtWidgets.QApplication.translate("UIFileConverterDialog", "Output directory:", None, -1))
        self.outDir_pushButton.setText(QtWidgets.QApplication.translate("UIFileConverterDialog", "...", None, -1))
        self.quit_pushButton.setText(QtWidgets.QApplication.translate("UIFileConverterDialog", "Quit", None, -1))

