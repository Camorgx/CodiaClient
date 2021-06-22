# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'functionWindow.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_functionWindow(object):
    def setupUi(self, functionWindow):
        functionWindow.setObjectName("functionWindow")
        functionWindow.resize(1000, 720)
        functionWindow.setMaximumSize(QtCore.QSize(1000, 720))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("favicon.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        functionWindow.setWindowIcon(icon)
        functionWindow.setDockNestingEnabled(False)
        self.centralwidget = QtWidgets.QWidget(functionWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.packFrame = QtWidgets.QFrame(self.centralwidget)
        self.packFrame.setGeometry(QtCore.QRect(0, 0, 1000, 720))
        self.packFrame.setMaximumSize(QtCore.QSize(1000, 720))
        self.packFrame.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.packFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.packFrame.setObjectName("packFrame")
        self.listWidget_packs = QtWidgets.QListWidget(self.packFrame)
        self.listWidget_packs.setGeometry(QtCore.QRect(0, 0, 750, 600))
        self.listWidget_packs.setObjectName("listWidget_packs")
        self.pushButton_pack_OK = QtWidgets.QPushButton(self.packFrame)
        self.pushButton_pack_OK.setGeometry(QtCore.QRect(810, 240, 113, 32))
        self.pushButton_pack_OK.setObjectName("pushButton_pack_OK")
        self.pushButton_next = QtWidgets.QPushButton(self.packFrame)
        self.pushButton_next.setGeometry(QtCore.QRect(810, 330, 113, 32))
        self.pushButton_next.setObjectName("pushButton_next")
        self.pushButton_last = QtWidgets.QPushButton(self.packFrame)
        self.pushButton_last.setGeometry(QtCore.QRect(810, 420, 113, 32))
        self.pushButton_last.setObjectName("pushButton_last")
        self.label_page = QtWidgets.QLabel(self.packFrame)
        self.label_page.setGeometry(QtCore.QRect(810, 150, 113, 32))
        self.label_page.setAlignment(QtCore.Qt.AlignCenter)
        self.label_page.setObjectName("label_page")
        self.exerciseFrame = QtWidgets.QFrame(self.centralwidget)
        self.exerciseFrame.setGeometry(QtCore.QRect(0, 0, 1000, 720))
        self.exerciseFrame.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.exerciseFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.exerciseFrame.setObjectName("exerciseFrame")
        self.pushButton_questionlist_OK = QtWidgets.QPushButton(self.exerciseFrame)
        self.pushButton_questionlist_OK.setGeometry(QtCore.QRect(810, 240, 113, 32))
        self.pushButton_questionlist_OK.setObjectName("pushButton_questionlist_OK")
        self.pushButton_questionlist_Back = QtWidgets.QPushButton(self.exerciseFrame)
        self.pushButton_questionlist_Back.setGeometry(QtCore.QRect(810, 420, 113, 32))
        self.pushButton_questionlist_Back.setObjectName("pushButton_questionlist_Back")
        self.listWidget_questions = QtWidgets.QListWidget(self.exerciseFrame)
        self.listWidget_questions.setGeometry(QtCore.QRect(0, 0, 750, 600))
        self.listWidget_questions.setObjectName("listWidget_questions")
        self.pushButton_Beginpack = QtWidgets.QPushButton(self.exerciseFrame)
        self.pushButton_Beginpack.setGeometry(QtCore.QRect(810, 150, 113, 32))
        self.pushButton_Beginpack.setObjectName("pushButton_Beginpack")
        self.exerciseFrame.raise_()
        self.packFrame.raise_()
        functionWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(functionWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1000, 24))
        self.menubar.setObjectName("menubar")
        functionWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(functionWindow)
        self.statusbar.setObjectName("statusbar")
        functionWindow.setStatusBar(self.statusbar)

        self.retranslateUi(functionWindow)
        QtCore.QMetaObject.connectSlotsByName(functionWindow)

    def retranslateUi(self, functionWindow):
        _translate = QtCore.QCoreApplication.translate
        functionWindow.setWindowTitle(_translate("functionWindow", "题包列表"))
        self.pushButton_pack_OK.setText(_translate("functionWindow", "确认"))
        self.pushButton_next.setText(_translate("functionWindow", "下一页"))
        self.pushButton_last.setText(_translate("functionWindow", "上一页"))
        self.label_page.setText(_translate("functionWindow", "第 1 页"))
        self.pushButton_questionlist_OK.setText(_translate("functionWindow", "确认"))
        self.pushButton_questionlist_Back.setText(_translate("functionWindow", "返回"))
        self.pushButton_Beginpack.setText(_translate("functionWindow", "开始题包"))
