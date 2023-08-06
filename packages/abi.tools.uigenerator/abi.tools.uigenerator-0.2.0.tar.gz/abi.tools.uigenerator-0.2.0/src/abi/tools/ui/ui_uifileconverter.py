# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'src\abi\tools\ui\uifileconverter.ui'
#
# Created: Thu Jul 12 16:57:36 2018
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
        self.ui_frame = QtGui.QFrame(UIFileConverterDialog)
        self.ui_frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.ui_frame.setFrameShadow(QtGui.QFrame.Raised)
        self.ui_frame.setObjectName("ui_frame")
        self.horizontalLayout = QtGui.QHBoxLayout(self.ui_frame)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.uiFile_label = QtGui.QLabel(self.ui_frame)
        self.uiFile_label.setObjectName("uiFile_label")
        self.horizontalLayout.addWidget(self.uiFile_label)
        self.uiFile_comboBox = QtGui.QComboBox(self.ui_frame)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiFile_comboBox.sizePolicy().hasHeightForWidth())
        self.uiFile_comboBox.setSizePolicy(sizePolicy)
        self.uiFile_comboBox.setObjectName("uiFile_comboBox")
        self.horizontalLayout.addWidget(self.uiFile_comboBox)
        self.uiFile_pushButton = QtGui.QPushButton(self.ui_frame)
        self.uiFile_pushButton.setObjectName("uiFile_pushButton")
        self.horizontalLayout.addWidget(self.uiFile_pushButton)
        self.verticalLayout.addWidget(self.ui_frame)
        self.sideBySide_groupBox = QtGui.QGroupBox(UIFileConverterDialog)
        self.sideBySide_groupBox.setCheckable(True)
        self.sideBySide_groupBox.setObjectName("sideBySide_groupBox")
        self.horizontalLayout_3 = QtGui.QHBoxLayout(self.sideBySide_groupBox)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.outDir_label = QtGui.QLabel(self.sideBySide_groupBox)
        self.outDir_label.setObjectName("outDir_label")
        self.horizontalLayout_3.addWidget(self.outDir_label)
        self.outDir_lineEdit = QtGui.QLineEdit(self.sideBySide_groupBox)
        self.outDir_lineEdit.setObjectName("outDir_lineEdit")
        self.horizontalLayout_3.addWidget(self.outDir_lineEdit)
        self.outDir_pushButton = QtGui.QPushButton(self.sideBySide_groupBox)
        self.outDir_pushButton.setObjectName("outDir_pushButton")
        self.horizontalLayout_3.addWidget(self.outDir_pushButton)
        self.verticalLayout.addWidget(self.sideBySide_groupBox)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.screen_label = QtGui.QLabel(UIFileConverterDialog)
        self.screen_label.setText("")
        self.screen_label.setObjectName("screen_label")
        self.verticalLayout.addWidget(self.screen_label)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem1)
        self.quit_frame = QtGui.QFrame(UIFileConverterDialog)
        self.quit_frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.quit_frame.setFrameShadow(QtGui.QFrame.Raised)
        self.quit_frame.setObjectName("quit_frame")
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.quit_frame)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem2 = QtGui.QSpacerItem(457, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem2)
        self.quit_pushButton = QtGui.QPushButton(self.quit_frame)
        self.quit_pushButton.setObjectName("quit_pushButton")
        self.horizontalLayout_2.addWidget(self.quit_pushButton)
        self.verticalLayout.addWidget(self.quit_frame)

        self.retranslateUi(UIFileConverterDialog)
        QtCore.QObject.connect(self.quit_pushButton, QtCore.SIGNAL("clicked()"), UIFileConverterDialog.close)
        QtCore.QMetaObject.connectSlotsByName(UIFileConverterDialog)

    def retranslateUi(self, UIFileConverterDialog):
        UIFileConverterDialog.setWindowTitle(QtGui.QApplication.translate("UIFileConverterDialog", "UI File Converter", None, QtGui.QApplication.UnicodeUTF8))
        self.uiFile_label.setText(QtGui.QApplication.translate("UIFileConverterDialog", "UI File:", None, QtGui.QApplication.UnicodeUTF8))
        self.uiFile_pushButton.setText(QtGui.QApplication.translate("UIFileConverterDialog", "Generate", None, QtGui.QApplication.UnicodeUTF8))
        self.sideBySide_groupBox.setTitle(QtGui.QApplication.translate("UIFileConverterDialog", "side-by-side output", None, QtGui.QApplication.UnicodeUTF8))
        self.outDir_label.setText(QtGui.QApplication.translate("UIFileConverterDialog", "Output directory:", None, QtGui.QApplication.UnicodeUTF8))
        self.outDir_pushButton.setText(QtGui.QApplication.translate("UIFileConverterDialog", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.quit_pushButton.setText(QtGui.QApplication.translate("UIFileConverterDialog", "Quit", None, QtGui.QApplication.UnicodeUTF8))

