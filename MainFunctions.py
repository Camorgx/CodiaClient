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
from codiaclientgui.utils import Font, Palette

variables = {
    "page_number": 0,
    "last_pack_pid": None,
    "first_pack_pid": None,
    "has_next": True,
}

# 打开做题界面
def MainInit(callback = None):
    global windowMain
    windowMain = QMainWindow()
    uiMain = Ui_windowMain()
    loginUserNickname = logined()[1]
    verified = bool(net_var["me"]["verified"])
    uiMain.setupUi(windowMain)
    BeginMain(uiMain, loginUserNickname, verified)

    from codiaclientgui.utils import Font
    windowMain.setFont(Font["main"])

    windowMain.show()
    callback and callback()

def BeginMain(uiMain: Ui_windowMain, nickname = "UNDEFINED", verified = True):
    if verified:
        labelStatusbarUser = QLabel(f"当前用户: {nickname}")
    else:
        labelStatusbarUser = QLabel(f"当前用户: {nickname}(未验证)")
        QMessageBox.information(None, "消息", "当前账号功能受限，请尽快完成联系方式验证。", QMessageBox.Ok)
    labelStatusbarUser.setFont(Font["status"])
    uiMain.statusbar.addWidget(labelStatusbarUser)
    uiMain.pushButtonPackNext.clicked.connect(lambda: NextPage(uiMain))
    uiMain.pushButtonPackPrevious.clicked.connect(lambda: PreviousPage(uiMain))
    NextPage(uiMain)
    uiMain.frameExercise.hide()
    uiMain.framePack.show()

# 在翻页后更新页面
def UpdatePage(uiMain: Ui_windowMain, packInfo):
    variables["has_next"] = packInfo["pageInfo"]["hasPreviousPage"]
    packList = packInfo["nodes"]
    variables["last_pack_pid"] = packList[0]["id"]
    variables["first_pack_pid"] = packList[-1]["id"]
    uiMain.pushButtonPackNext.setEnabled(variables["has_next"])
    uiMain.pushButtonPackPrevious.setEnabled(variables["page_number"] > 1)
    uiMain.labelPackPage.setText("第 {} 页".format(variables["page_number"]))
    for i in range(0, uiMain.listWidgetPack.count()): uiMain.listWidgetPack.takeItem(0)
    for dic in packList: AddItemToPackList(uiMain.listWidgetPack, dic)

# 下一页，时间更早
def NextPage(uiMain: Ui_windowMain):
    uiMain.pushButtonPackNext.setEnabled(False)
    uiMain.pushButtonPackPrevious.setEnabled(False)
    try: packInfo = get_pack(before = variables["last_pack_pid"])
    except codiaError as e:
        errorTranslate = error_translate(e)
        if errorTranslate: QMessageBox.critical(None, "获取失败", errorTranslate, QMessageBox.Ok)
        else: QMessageBox.critical(None, "未知错误", str(e), QMessageBox.Ok)
        return False
    variables["page_number"] += 1
    UpdatePage(uiMain, packInfo)

# 上一页，时间更近
def PreviousPage(uiMain: Ui_windowMain):
    uiMain.pushButtonPackNext.setEnabled(False)
    uiMain.pushButtonPackPrevious.setEnabled(False)
    try: packInfo = get_pack(after = variables["first_pack_pid"])
    except codiaError as e:
        errorTranslate = error_translate(e)
        if errorTranslate: QMessageBox.critical(None, "获取失败", errorTranslate, QMessageBox.Ok)
        else: QMessageBox.critical(None, "未知错误", str(e), QMessageBox.Ok)
        return False
    variables["page_number"] -= 1
    UpdatePage(uiMain, packInfo)

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
