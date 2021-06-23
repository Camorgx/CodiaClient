from datetime import datetime, timedelta
from re import search

from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout
from PyQt5.QtWidgets import QListWidgetItem, QWidget, QListWidget
from PyQt5.QtWidgets import QMessageBox

from mainWindow import Ui_windowMain

from codiaclient import net_var
from codiaclient.network import get_pack, show_pack, logined
from codiaclient.report import Error as codiaError, error_translate as ErrorTranslate
from codiaclientgui.utils import Font, Palette

variables = {
    "pageNumber": 0,
    "lastPid": None,
    "firstPid": None,
    "hasNext": True,
    "packInfo": {},
}

# 初始化任务，新建一个做题窗体和对应的ui
def MainInit(callback = None):
    global windowMain, uiMain
    windowMain = QMainWindow()
    windowMain.setFont(Font["main"])
    uiMain = Ui_windowMain()
    uiMain.setupUi(windowMain)
    BeginMain(callback = callback)
    #注意此处（下面）的顺序
    GetPage(callback = UpdatePage)
    windowMain.show()

# 初始化任务，为做题窗口信号绑定槽函数
def BeginMain(callback = None):
    nickname = logined()[1]
    if not nickname: nickname = "UNDEFINED"
    verified = net_var["me"]["verified"]
    if verified:
        labelStatusbarUser = QLabel(f"当前用户: {nickname}")
    else:
        labelStatusbarUser = QLabel(f"当前用户: {nickname}(未验证)")
        QMessageBox.information(None, "消息", "当前账号功能受限，请尽快完成联系方式验证。", QMessageBox.Ok)
    labelStatusbarUser.setFont(Font["status"])

    uiMain.pushButtonPackNext.clicked.connect(lambda: GetPage(before = variables["lastPid"], callback = UpdatePage))
    uiMain.pushButtonPackPrevious.clicked.connect(lambda: GetPage(after = variables["firstPid"], callback = UpdatePage))
    uiMain.statusbar.addWidget(labelStatusbarUser)

    uiMain.frameExercise.hide()
    uiMain.framePack.show()
    callback and callback()

# 在翻页后更新页面
def UpdatePage():
    variables["hasNext"] = variables["packInfo"]["pageInfo"]["hasPreviousPage"]
    packList = variables["packInfo"]["nodes"]
    variables["lastPid"] = packList[0]["id"]
    variables["firstPid"] = packList[-1]["id"]
    uiMain.pushButtonPackNext.setEnabled(variables["hasNext"])
    uiMain.pushButtonPackPrevious.setEnabled(variables["pageNumber"] > 1)
    uiMain.labelPackPage.setText("第 {} 页".format(variables["pageNumber"]))
    for i in range(0, uiMain.listWidgetPack.count()): uiMain.listWidgetPack.takeItem(0)
    for dic in packList: AddItemToPackList(uiMain.listWidgetPack, dic)

import threading
# 翻页
def GetPage(before = None, after = None, callback = None):
    if before and after: return False
    uiMain.pushButtonPackNext.setEnabled(False)
    uiMain.pushButtonPackPrevious.setEnabled(False)
    try: variables["packInfo"] = get_pack(before = before, after = after)
    except codiaError as e:
        errorTranslate = error_translate(e)
        if errorTranslate: QMessageBox.critical(None, "获取失败", errorTranslate, QMessageBox.Ok)
        else: QMessageBox.critical(None, "未知错误", str(e), QMessageBox.Ok)
        return False
    # def GetPack():
    #     try: variables["packInfo"] = get_pack(before = before, after = after)
    #     except codiaError as e:
    #         errorTranslate = error_translate(e)
    #         if errorTranslate: QMessageBox.critical(None, "获取失败", errorTranslate, QMessageBox.Ok)
    #         else: QMessageBox.critical(None, "未知错误", str(e), QMessageBox.Ok)
    #         return False
    # tr = threading.Thread(target = GetPack)
    # tr.start()
    # # QMessageBox.information(None, "消息", "测试", QMessageBox.Ok)
    # tr.join()
    if before: variables["pageNumber"] += 1
    elif after: variables["pageNumber"] -= 1
    else: variables["pageNumber"] = 1
    callback and callback()

def GetPackWidget(data: dict):
    widget = QWidget()
    layoutPackmain = QHBoxLayout()
    layoutPackRight = QVBoxLayout()
    layoutPackRightUp = QHBoxLayout()
    layoutPackRightDown = QHBoxLayout()
    if data["codingExercises"]:
        total = data["codingExercises"]["totalCount"]
        has_done = data["codingExercises"]["viewerPassedCount"]
        if total == has_done:
            labelPackFinish = QLabel("已完成")
            labelPackFinish.setPalette(Palette["green"])
        else:
            labelPackFinish = QLabel("未完成")
            labelPackFinish.setPalette(Palette["red"])
        labelPackHasDoneDivTotal = QLabel(f"已完成/总计: {has_done}/{total}")
        if data["due"]:
            endTime = (datetime.strptime(search(r"^[^.]*", data["due"].replace("T", " ")).group(), "%Y-%m-%d %H:%M:%S")
                + timedelta(hours = 8)).strftime("%Y-%m-%d %H:%M:%S")
        else: endTime = "无限制"

        if data["createdAt"]:
            beginTime = (datetime.strptime(search(r"^[^.]*", data["createdAt"].replace("T", " ")).group(), "%Y-%m-%d %H:%M:%S")
                  + timedelta(hours = 8)).strftime("%Y-%m-%d %H:%M:%S")
        else: beginTime = "无限制"
    else:
        endTime = ""
        beginTime = ""
        labelPackFinish = QLabel("无权限")
        labelPackFinish.setPalette(Palette["gray"])
        labelPackHasDoneDivTotal = QLabel("")
        widget.setEnabled(False)

    labelPackName = QLabel(data["name"])
    labelPackBegin = QLabel("开始时间")
    labelPackBeginTime = QLabel(beginTime)
    labelPackEnd = QLabel("截止时间")
    labelPackEndTime = QLabel(endTime)

    layoutPackRightUp.addWidget(labelPackName)
    layoutPackRightUp.addWidget(labelPackBegin)
    layoutPackRightUp.addWidget(labelPackEnd)
    layoutPackRightUp.setStretchFactor(labelPackName, 4)
    layoutPackRightUp.setStretchFactor(labelPackBegin, 4)
    layoutPackRightUp.setStretchFactor(labelPackEnd, 4)

    layoutPackRightDown.addWidget(labelPackHasDoneDivTotal)
    layoutPackRightDown.addWidget(labelPackBeginTime)
    layoutPackRightDown.addWidget(labelPackEndTime)
    layoutPackRightDown.setStretchFactor(labelPackHasDoneDivTotal, 4)
    layoutPackRightDown.setStretchFactor(labelPackBeginTime, 4)
    layoutPackRightDown.setStretchFactor(labelPackEndTime, 4)

    layoutPackRight.addLayout(layoutPackRightUp)
    layoutPackRight.addLayout(layoutPackRightDown)
    layoutPackRight.setStretchFactor(layoutPackRightUp, 12)
    layoutPackRight.setStretchFactor(layoutPackRightDown, 12)

    layoutPackmain.addWidget(labelPackFinish)
    layoutPackmain.addLayout(layoutPackRight)
    layoutPackmain.setStretchFactor(labelPackFinish, 1)
    layoutPackmain.setStretchFactor(layoutPackRight, 12)

    widget.setLayout(layoutPackmain)
    return widget


def AddItemToPackList(packList: QListWidget, data: dict):
    item = QListWidgetItem()
    item.setSizeHint(QSize(1060, 69))
    widget = GetPackWidget(data)
    packList.addItem(item)
    packList.setItemWidget(item, widget)
