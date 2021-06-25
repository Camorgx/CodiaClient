# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainWindow.ui'
#
# Created by: PyQt5 UI code generator 5.15.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_windowMain(object):
    def setupUi(self, windowMain):
        windowMain.setObjectName("windowMain")
        windowMain.resize(1080, 768)
        windowMain.setMinimumSize(QtCore.QSize(1080, 768))
        windowMain.setMaximumSize(QtCore.QSize(1280, 768))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("favicon.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        windowMain.setWindowIcon(icon)
        windowMain.setDockNestingEnabled(False)
        self.centralwidget = QtWidgets.QWidget(windowMain)
        self.centralwidget.setObjectName("centralwidget")
        self.framePack = QtWidgets.QFrame(self.centralwidget)
        self.framePack.setGeometry(QtCore.QRect(0, 0, 1080, 768))
        self.framePack.setMinimumSize(QtCore.QSize(1080, 768))
        self.framePack.setMaximumSize(QtCore.QSize(1280, 768))
        self.framePack.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.framePack.setFrameShadow(QtWidgets.QFrame.Raised)
        self.framePack.setObjectName("framePack")
        self.listWidgetPack = QtWidgets.QListWidget(self.framePack)
        self.listWidgetPack.setGeometry(QtCore.QRect(28, 30, 1024, 540))
        self.listWidgetPack.setMaximumSize(QtCore.QSize(1280, 768))
        self.listWidgetPack.setObjectName("listWidgetPack")
        self.pushButtonPackOK = NewPushButton(self.framePack)
        self.pushButtonPackOK.setGeometry(QtCore.QRect(250, 660, 120, 32))
        self.pushButtonPackOK.setObjectName("pushButtonPackOK")
        self.pushButtonPackNext = NewPushButton(self.framePack)
        self.pushButtonPackNext.setGeometry(QtCore.QRect(930, 660, 120, 32))
        self.pushButtonPackNext.setObjectName("pushButtonPackNext")
        self.pushButtonPackPrevious = NewPushButton(self.framePack)
        self.pushButtonPackPrevious.setGeometry(QtCore.QRect(770, 660, 120, 32))
        self.pushButtonPackPrevious.setObjectName("pushButtonPackPrevious")
        self.labelPackPage = QtWidgets.QLabel(self.framePack)
        self.labelPackPage.setGeometry(QtCore.QRect(50, 660, 120, 32))
        self.labelPackPage.setAlignment(QtCore.Qt.AlignCenter)
        self.labelPackPage.setObjectName("labelPackPage")
        self.progressBarPack = QtWidgets.QProgressBar(self.framePack)
        self.progressBarPack.setGeometry(QtCore.QRect(40, 610, 1000, 20))
        self.progressBarPack.setProperty("value", 20)
        self.progressBarPack.setTextVisible(False)
        self.progressBarPack.setObjectName("progressBarPack")
        self.frameExercise = QtWidgets.QFrame(self.centralwidget)
        self.frameExercise.setGeometry(QtCore.QRect(0, 0, 1080, 768))
        self.frameExercise.setMinimumSize(QtCore.QSize(1080, 768))
        self.frameExercise.setMaximumSize(QtCore.QSize(1280, 768))
        self.frameExercise.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frameExercise.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frameExercise.setObjectName("frameExercise")
        self.pushButtonExerciseOK = NewPushButton(self.frameExercise)
        self.pushButtonExerciseOK.setGeometry(QtCore.QRect(250, 660, 120, 32))
        self.pushButtonExerciseOK.setObjectName("pushButtonExerciseOK")
        self.pushButtonExerciseReturn = NewPushButton(self.frameExercise)
        self.pushButtonExerciseReturn.setGeometry(QtCore.QRect(410, 660, 120, 32))
        self.pushButtonExerciseReturn.setObjectName("pushButtonExerciseReturn")
        self.listWidgetExercise = QtWidgets.QListWidget(self.frameExercise)
        self.listWidgetExercise.setGeometry(QtCore.QRect(28, 30, 1024, 540))
        self.listWidgetExercise.setObjectName("listWidgetExercise")
        self.pushButtonExerciseBegin = NewPushButton(self.frameExercise)
        self.pushButtonExerciseBegin.setGeometry(QtCore.QRect(50, 660, 120, 32))
        self.pushButtonExerciseBegin.setObjectName("pushButtonExerciseBegin")
        self.labelDeadline = QtWidgets.QLabel(self.frameExercise)
        self.labelDeadline.setGeometry(QtCore.QRect(770, 660, 280, 32))
        self.labelDeadline.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.labelDeadline.setIndent(10)
        self.labelDeadline.setObjectName("labelDeadline")
        self.progressBarExercise = QtWidgets.QProgressBar(self.frameExercise)
        self.progressBarExercise.setGeometry(QtCore.QRect(40, 610, 1000, 20))
        self.progressBarExercise.setProperty("value", 20)
        self.progressBarExercise.setTextVisible(False)
        self.progressBarExercise.setObjectName("progressBarExercise")
        windowMain.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(windowMain)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1080, 26))
        self.menubar.setObjectName("menubar")
        windowMain.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(windowMain)
        self.statusbar.setObjectName("statusbar")
        windowMain.setStatusBar(self.statusbar)

        self.retranslateUi(windowMain)
        QtCore.QMetaObject.connectSlotsByName(windowMain)

    def retranslateUi(self, windowMain):
        _translate = QtCore.QCoreApplication.translate
        windowMain.setWindowTitle(_translate("windowMain", "题包列表"))
        self.pushButtonPackOK.setText(_translate("windowMain", "确认"))
        self.pushButtonPackNext.setText(_translate("windowMain", "下一页"))
        self.pushButtonPackPrevious.setText(_translate("windowMain", "上一页"))
        self.labelPackPage.setText(_translate("windowMain", "第 1 页"))
        self.pushButtonExerciseOK.setText(_translate("windowMain", "确认"))
        self.pushButtonExerciseReturn.setText(_translate("windowMain", "返回"))
        self.pushButtonExerciseBegin.setText(_translate("windowMain", "开始题包"))
        self.labelDeadline.setText(_translate("windowMain", "截止日期：无限制"))
from codiaclientgui.utils import NewPushButton
