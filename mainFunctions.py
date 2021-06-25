from datetime import datetime, timedelta
from re import search

from PyQt5.QtCore import Qt, QSize, QThread, pyqtSignal
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout
from PyQt5.QtWidgets import QListWidgetItem, QWidget, QListWidget
from PyQt5.QtWidgets import QMessageBox, QMainWindow, QApplication

from codiaclient import net_var
from codiaclient.network import get_pack, show_pack, start_pack, logined
from codiaclient.report import Error as codiaError, error_translate
from codiaclient.requests import variables as requests_var
from codiaclientgui.utils import QPalette, Font, Palette, Style, Color
from mainWindow import Ui_windowMain

variables = {
    "pageNumber": 0,
    "packPerPage": 8,
    "lastPid": None,
    "firstPid": None,
    "hasNext": True,
    "packInfo": {},
    "currentPackRow": None
}


def frameExerciseInit():
    if not uiMain.listWidgetPack.selectedIndexes():
        QMessageBox.information(None, "提示", "请选择题包。", QMessageBox.Ok)
        return
    uiMain.framePack.hide()
    uiMain.frameExercise.show()
    uiMain.listWidgetExercise.clear()
    exerciseListInfo = show_pack(pid=requests_var["p"])
    presentTime = datetime.now()
    if exerciseListInfo["due"]:
        endTime = datetime.strptime(search(r"^[^.]*", exerciseListInfo["due"].replace("T", " ")).group(),
                                    "%Y-%m-%d %H:%M:%S") + timedelta(hours=8)
        endTimeText = endTime.strftime("%Y-%m-%d %H:%M:%S")
    else:
        endTime = datetime.strptime("2100-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")
        endTimeText = "无限制"
    createdAt = variables["packInfo"]["nodes"][variables["currentPackRow"]]["createdAt"]
    if createdAt:
        beginTime = datetime.strptime(search(r"^[^.]*", createdAt.replace("T", " ")).group(), "%Y-%m-%d %H:%M:%S") \
                    + timedelta(hours=8)
    else:
        beginTime = datetime.strptime("1900-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")
    uiMain.labelDeadline.setText(f"截止时间: {endTimeText}")
    windowMain.setWindowTitle(exerciseListInfo["name"])
    if not (beginTime < presentTime < endTime and (not exerciseListInfo["viewerStatus"]["ongoing"])):
        uiMain.pushButtonExerciseBegin.hide()
    if exerciseListInfo['description']:
        uiMain.textEditExerciseDiscription.setMarkdown(exerciseListInfo['description']['content'])
    else:
        uiMain.textEditExerciseDiscription.setText('本题包未设置题包描述')
    variables['exerciseInfo'] = exerciseListInfo['codingExercises']['nodes']
    if variables['exerciseInfo']:
        for exercise in variables['exerciseInfo']:
            AddItemToQuestionList(exercise)


def AddItemToQuestionList(data: dict):
    item = QListWidgetItem()
    item.setSizeHint(QSize(960, 65))
    widget = GetExerciseWidget(data)
    widget.setCursor(Qt.PointingHandCursor)
    uiMain.listWidgetExercise.addItem(item)
    uiMain.listWidgetExercise.setItemWidget(item, widget)


def GetExerciseWidget(data: dict):
    if data['viewerStatus']['passedCount'] > 0:
        label_status = QLabel('已通过')
        label_status.setPalette(Palette[QPalette.Text]['green'])
    else:
        label_status = QLabel('未通过')
        label_status.setPalette(Palette[QPalette.Text]['red'])
    label_name = QLabel(str(data['title']))
    label_passed = QLabel(f"通过数：{data['viewerStatus']['passedCount']}")
    label_submit = QLabel(f"提交数：{data['viewerStatus']['totalCount']}")
    layout_main = QHBoxLayout()
    layout_right = QVBoxLayout()

    layout_main.addWidget(label_status)
    layout_main.addWidget(label_name)
    layout_right.addWidget(label_submit)
    layout_right.addWidget(label_passed)
    layout_main.addLayout(layout_right)

    layout_main.setStretchFactor(label_status, 1)
    layout_main.setStretchFactor(label_name, 3)
    layout_main.setStretchFactor(layout_right, 2)

    widget = QWidget()
    widget.setLayout(layout_main)
    return widget


def getSelectedPid():
    if uiMain.listWidgetPack.selectedIndexes():
        selected = uiMain.listWidgetPack.selectedIndexes()[0]
        variables["currentPackRow"] = selected.row()
        requests_var["p"] = variables["packInfo"]["nodes"][variables["currentPackRow"]]["id"]


def getSelectedEid():
    selected = uiMain.listWidgetExercise.selectedIndexes()[0]
    variables['currentExerciseRow'] = selected.row()
    requests_var['e'] = variables['exerciseInfo'][selected.row()]['id']


def ExerciseReturn():
    uiMain.frameExercise.hide()
    uiMain.framePack.show()
    uiMain.pushButtonExerciseBegin.show()


def BeginPack():
    try:
        start_pack(requests_var["p"])
    except codiaError as e:
        errorTranslate = error_translate(e)
        if errorTranslate:
            QMessageBox.critical(None, "错误", errorTranslate, QMessageBox.Ok)
        else:
            QMessageBox.critical(None, "未知错误", str(e), QMessageBox.Ok)
    else:
        QMessageBox.information(None, "消息", "成功开始题包", QMessageBox.Ok)
        uiMain.pushButtonExerciseBegin.hide()
        variables["packInfo"]["nodes"][variables["currentPackRow"]]['ongoing'] = True


# 初始化任务，新建一个做题窗体和对应的ui
def MainInit(callback=None):
    global windowMain, uiMain
    windowMain = QMainWindow()
    windowMain.setFont(Font["main"])
    uiMain = Ui_windowMain()
    uiMain.setupUi(windowMain)
    BeginMain(callback=callback)
    windowMain.show()
    GetPage()


# 初始化任务，为做题窗口信号绑定槽函数
def BeginMain(callback=None):
    QApplication.processEvents()
    nickname = logined()[1]
    if not nickname:
        nickname = "UNDEFINED"
    verified = net_var["me"]["verified"]
    if verified:
        labelStatusbarUser = QLabel(f"当前用户: {nickname}")
    else:
        labelStatusbarUser = QLabel(f"当前用户: {nickname}(未验证)")
        QMessageBox.information(None, "消息", "当前账号功能受限，请尽快完成联系方式验证。", QMessageBox.Ok)
    labelStatusbarUser.setFont(Font["status"])

    uiMain.pushButtonPackNext.clicked.connect(lambda: GetPage(before=variables["lastPid"]))
    uiMain.pushButtonPackPrevious.clicked.connect(lambda: GetPage(after=variables["firstPid"]))
    uiMain.statusbar.addWidget(labelStatusbarUser)
    uiMain.progressBarPack.hide()
    uiMain.progressBarExercise.hide()
    uiMain.progressBarPack.setStyleSheet(Style["progressBar"])
    uiMain.progressBarExercise.setStyleSheet(Style["progressBar"])
    uiMain.listWidgetPack.itemClicked.connect(getSelectedPid)
    uiMain.listWidgetPack.itemDoubleClicked.connect(frameExerciseInit)
    uiMain.pushButtonPackOK.clicked.connect(frameExerciseInit)
    uiMain.pushButtonExerciseReturn.clicked.connect(ExerciseReturn)
    uiMain.pushButtonExerciseBegin.clicked.connect(BeginPack)
    uiMain.listWidgetExercise.itemClicked.connect(getSelectedEid)
    for i in range(0, variables['packPerPage']):
        AddItemToPackList(uiMain.listWidgetPack, colorName=['white', 'lightgray'][i % 2])

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
    for i in range(0, uiMain.listWidgetPack.count()):
        uiMain.listWidgetPack.takeItem(0)
    packList.reverse()
    packList += [None] * (variables['packPerPage'] - len(packList))
    for i in range(0, len(packList)):
        AddItemToPackList(uiMain.listWidgetPack, packList[i], colorName=['white', 'lightgray'][i % 2])


# 获取题包信息的网络通信
class _GetPack(QThread):
    infoSignal = pyqtSignal(dict)
    errorSignal = pyqtSignal(codiaError)

    def __init__(self, before=None, after=None, parent=None):
        super(_GetPack, self).__init__(parent)
        self.working = True
        self.before = before
        self.after = after

    def __del__(self):
        self.working = False
        self.wait()

    def run(self):
        try:
            self.packInfo = get_pack(cnt=variables['packPerPage'], before=self.before, after=self.after)
        except codiaError as e:
            self.errorSignal.emit(e)
        else:
            self.infoSignal.emit(self.packInfo)


# 获取题包信息的多线程准备
def GetPack(before=None, after=None, InfoRecv=lambda: None, ErrorRecv=lambda: None):
    global threadGetPack  # extremely essential!
    threadGetPack = _GetPack(before=before, after=after)
    threadGetPack.infoSignal.connect(InfoRecv)
    threadGetPack.errorSignal.connect(ErrorRecv)
    uiMain.progressBarPack.setValue(30)
    threadGetPack.start()


# 翻页
def GetPage(before=None, after=None):
    uiMain.progressBarPack.setValue(0)
    uiMain.progressBarPack.show()
    if before and after:
        return False
    uiMain.pushButtonPackNext.setEnabled(False)
    uiMain.pushButtonPackPrevious.setEnabled(False)
    uiMain.progressBarPack.setValue(10)

    def PackInfoRecv(packInfo):
        if not packInfo:
            uiMain.progressBarPack.hide()
            return
        variables["packInfo"] = packInfo
        if before:
            variables["pageNumber"] += 1
        elif after:
            variables["pageNumber"] -= 1
        else:
            variables["pageNumber"] = 1
        uiMain.progressBarPack.setValue(100)
        uiMain.progressBarPack.hide()
        UpdatePage()

    def ErrorRecv(e: codiaError):
        errorTranslate = error_translate(e)
        if errorTranslate:
            QMessageBox.critical(None, "获取失败", errorTranslate, QMessageBox.Ok)
        else:
            QMessageBox.critical(None, "未知错误", str(e), QMessageBox.Ok)
        uiMain.progressBarPack.hide()
        try:
            UpdatePage()
        except:
            pass

    GetPack(before=before, after=after, InfoRecv=PackInfoRecv, ErrorRecv=ErrorRecv)


def GetPackWidget(data: dict):
    widget = QWidget()
    layoutPackmain = QHBoxLayout()
    layoutPackRight = QVBoxLayout()
    layoutPackRightUp = QHBoxLayout()
    layoutPackRightDown = QHBoxLayout()
    if data["codingExercises"]:
        total = data["codingExercises"]["totalCount"]
        hasDone = data["codingExercises"]["viewerPassedCount"]
        if total == hasDone:
            labelPackFinish = QLabel("已完成")
            labelPackFinish.setPalette(Palette[QPalette.Text]["green"])
        else:
            labelPackFinish = QLabel("未完成")
            labelPackFinish.setPalette(Palette[QPalette.Text]["red"])
        labelPackHasDoneDivTotal = QLabel(f"已完成/总计: {hasDone}/{total}")
        if data["due"]:
            endTimeText = (
                        datetime.strptime(search(r"^[^.]*", data["due"].replace("T", " ")).group(), "%Y-%m-%d %H:%M:%S")
                        + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
        else:
            endTimeText = "无限制"

        if data["createdAt"]:
            beginTimeText = (datetime.strptime(search(r"^[^.]*", data["createdAt"].replace("T", " ")).group(),
                                               "%Y-%m-%d %H:%M:%S")
                             + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
        else:
            beginTimeText = "无限制"
    else:
        endTimeText = ""
        beginTimeText = ""
        labelPackFinish = QLabel("无权限")
        labelPackFinish.setPalette(Palette[QPalette.Text]["gray"])
        labelPackHasDoneDivTotal = QLabel("")
        widget.setEnabled(False)

    labelPackName = QLabel(data["name"])
    labelPackBegin = QLabel("开始时间")
    labelPackBeginTime = QLabel(beginTimeText)
    labelPackEnd = QLabel("截止时间")
    labelPackEndTime = QLabel(endTimeText)

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
    layoutPackRight.setStretchFactor(layoutPackRightUp, 8)
    layoutPackRight.setStretchFactor(layoutPackRightDown, 8)

    labelPackFinish.setAlignment(Qt.AlignCenter)
    layoutPackmain.addWidget(labelPackFinish)
    layoutPackmain.addLayout(layoutPackRight)
    layoutPackmain.setStretchFactor(labelPackFinish, 1)
    layoutPackmain.setStretchFactor(layoutPackRight, 8)

    widget.setLayout(layoutPackmain)
    return widget


def AddItemToPackList(packList: QListWidget, data: dict = {}, colorName: str = "white"):
    item = QListWidgetItem()
    item.setSizeHint(QSize(960, 65))
    item.setBackground(Color[colorName])
    if not data:
        widget = QWidget()
        widget.setEnabled(False)
    else:
        widget = GetPackWidget(data)
    widget.setCursor(Qt.PointingHandCursor)
    if not widget.isEnabled():
        item.setFlags(item.flags() & ~Qt.ItemIsEnabled & ~Qt.ItemIsSelectable)
    packList.addItem(item)
    packList.setItemWidget(item, widget)
