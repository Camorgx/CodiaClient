from datetime import datetime, timedelta
from re import search

from PyQt5.QtCore import Qt, QSize, QThread, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout
from PyQt5.QtWidgets import QListWidgetItem, QWidget, QListWidget
from PyQt5.QtWidgets import QMessageBox, QMainWindow, QApplication

from codiaclient import net_var
from codiaclient.network import get_pack, show_pack, start_pack, logined, get_exercise
from codiaclient.network import submit
from codiaclient.report import Error as codiaError, error_translate
from codiaclient.requests import variables as requests_var
from codiaclientgui.utils import QPalette, Font, Palette, Style, Color, ErrorDisplay
from mainWindow import Ui_windowMain

variables = {
    "pageNumber": 0,
    "packPerPage": 8,
    "lastPid": None,
    "firstPid": None,
    "hasNext": True,
    "packInfo": {},
    "currentPackRow": None,
    "exerciseInfo": None
}

displayLanguage = {
    'CPP': 'C++',
    'C': 'C',
    'JAVA': 'Java',
    'JAVASCRIPT': 'JavaScript',
    'GO': 'Go',
    'RUST': 'Rust',
    'PYTHON': 'Python'
}
dataLanguage = {val: key for key, val in displayLanguage.items()}

# 获取题包内容信息的网络通信
class _ShowPack(QThread):
    infoSignal = pyqtSignal(dict)
    errorSignal = pyqtSignal(codiaError)

    def __init__(self, *args, pid, **kargs):
        super(_ShowPack, self).__init__(*args, **kargs)
        self.working = True
        self.pid = pid

    def __del__(self):
        self.working = False
        self.wait()

    def run(self):
        try:
            self.packInfo = show_pack(pid=self.pid)
        except codiaError as e:
            self.errorSignal.emit(e)
        else:
            self.infoSignal.emit(self.packInfo)


# 获取题包内容信息的多线程准备
def ShowPack(pid, InfoRecv=lambda: None, ErrorRecv=lambda: None):
    global threadShowPack  # extremely essential!
    threadShowPack = _ShowPack(pid=pid)
    threadShowPack.infoSignal.connect(InfoRecv)
    threadShowPack.errorSignal.connect(ErrorRecv)
    uiMain.progressBarPack.setValue(90)
    threadShowPack.start()


def frameExerciseInit():
    global frameExerciseInitWorking
    try:
        if frameExerciseInitWorking:
            return
    except:
        pass
    if not uiMain.listWidgetPack.selectedIndexes():
        QMessageBox.information(None, "提示", "请选择一个题包。", QMessageBox.Ok)
        return
    uiMain.progressBarPack.setValue(0)
    uiMain.progressBarPack.show()
    frameExerciseInitWorking = True

    def ErrorRecv(e: codiaError):
        global frameExerciseInitWorking
        ErrorDisplay(e, error_translate, "获取失败")
        uiMain.progressBarPack.hide()
        frameExerciseInitWorking = False

    def exerciseListInfoRecv(exerciseListInfo):
        global frameExerciseInitWorking
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
        if exerciseListInfo["viewerStatus"]["ongoing"] or not (beginTime < presentTime < endTime):
            uiMain.pushButtonExerciseBegin.hide()
        if exerciseListInfo['description']:
            uiMain.textEditExerciseDiscription.setMarkdown(exerciseListInfo['description']['content'])
        else:
            uiMain.textEditExerciseDiscription.setText('本题包未设置题包描述')
        variables['exerciseListInfo'] = exerciseListInfo['codingExercises']['nodes']
        uiMain.listWidgetExercise.clear()
        if variables['exerciseListInfo']:
            for exercise in variables['exerciseListInfo']:
                AddItemToQuestionList(exercise)
        uiMain.progressBarPack.hide()
        frameExerciseInitWorking = False
        uiMain.framePack.hide()
        uiMain.frameExercise.show()

    ShowPack(pid=requests_var["p"], InfoRecv=exerciseListInfoRecv, ErrorRecv=ErrorRecv)


def AddItemToQuestionList(data: dict):
    item = QListWidgetItem()
    item.setSizeHint(QSize(960, 65))
    widget = GetExerciseWidget(data)
    widget.setCursor(Qt.PointingHandCursor)
    uiMain.listWidgetExercise.addItem(item)
    uiMain.listWidgetExercise.setItemWidget(item, widget)


def GetExerciseWidget(data: dict):
    if data['viewerStatus']['passedCount'] > 0:
        labelExerciseStatus = QLabel('已通过')
        labelExerciseStatus.setPalette(Palette[QPalette.Text]['green'])
    else:
        labelExerciseStatus = QLabel('未通过')
        labelExerciseStatus.setPalette(Palette[QPalette.Text]['red'])
    labelExerciseTitle = QLabel(str(data['title']))
    labelExercisePassed = QLabel(f"通过数：{data['viewerStatus']['passedCount']}")
    labelExerciseSubmit = QLabel(f"提交数：{data['viewerStatus']['totalCount']}")
    layoutExerciseMain = QHBoxLayout()
    layoutExerciseRight = QVBoxLayout()

    layoutExerciseRight.addWidget(labelExerciseSubmit)
    layoutExerciseRight.addWidget(labelExercisePassed)
    layoutExerciseMain.addWidget(labelExerciseStatus)
    layoutExerciseMain.addWidget(labelExerciseTitle)
    layoutExerciseMain.addLayout(layoutExerciseRight)

    labelExerciseStatus.setAlignment(Qt.AlignCenter)
    layoutExerciseMain.setStretchFactor(labelExerciseStatus, 1)
    layoutExerciseMain.setStretchFactor(labelExerciseTitle, 5)
    layoutExerciseMain.setStretchFactor(layoutExerciseRight, 3)

    widget = QWidget()
    widget.setLayout(layoutExerciseMain)
    return widget


def getSelectedPid():
    if uiMain.listWidgetPack.selectedIndexes():
        selected = uiMain.listWidgetPack.selectedIndexes()[0]
        variables["currentPackRow"] = selected.row()
        requests_var["p"] = variables["packInfo"]["nodes"][variables["currentPackRow"]]["id"]


def getSelectedEid():
    selected = uiMain.listWidgetExercise.currentIndex().row()
    variables['currentExerciseRow'] = selected
    requests_var['e'] = variables['exerciseListInfo'][selected]['id']


def ExerciseReturn():
    uiMain.frameExercise.hide()
    uiMain.framePack.show()
    uiMain.pushButtonExerciseBegin.show()
    windowMain.setWindowTitle('题包列表')


def BeginPack():
    try:
        start_pack(requests_var["p"])
    except codiaError as e:
        ErrorDisplay(e, error_translate)
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


# 获取题目信息的网络通信
class _GetExercise(QThread):
    infoSignal = pyqtSignal(dict)
    errorSignal = pyqtSignal(codiaError)

    def __init__(self, *args, pid, eid, lang, **kargs):
        super(_GetExercise, self).__init__(*args, **kargs)
        self.working = True
        self.pid = pid
        self.eid = eid
        self.lang = lang

    def __del__(self):
        self.working = False
        self.wait()

    def run(self):
        try:
            self.exerciseInfo = get_exercise(eid=self.eid, pid=self.pid, lang=self.lang)
        except codiaError as e:
            self.errorSignal.emit(e)
        else:
            self.infoSignal.emit(self.exerciseInfo)


# 获取题目信息的多线程准备
def GetExercise(pid, eid, lang, InfoRecv=lambda: None, ErrorRecv=lambda: None):
    global threadGetExercise  # extremely essential!
    threadGetExercise = _GetExercise(eid=eid, pid=pid, lang=lang)
    threadGetExercise.infoSignal.connect(InfoRecv)
    threadGetExercise.errorSignal.connect(ErrorRecv)
    uiMain.progressBarExercise.setValue(90)
    threadGetExercise.start()


def frameQuestionInit():
    global frameQuestionInitWorking
    try:
        if frameQuestionInitWorking:
            return
    except:
        pass

    if not uiMain.listWidgetExercise.selectedIndexes():
        QMessageBox.information(None, '消息', '请选择一个题目', QMessageBox.Ok)
        return

    frameQuestionInitWorking = True
    uiMain.progressBarExercise.setValue(0)
    uiMain.progressBarExercise.show()

    def ExerciseInfoRecv(questionInfo):
        global frameQuestionInitWorking
        variables['exerciseInfo'] = questionInfo
        windowMain.setWindowTitle(questionInfo['title'])
        uiMain.statusbar.clearMessage()
        if questionInfo['tags']:
            uiMain.statusbar.showMessage("标签：" + ", ".join(questionInfo['tags']))
        else:
            uiMain.statusbar.showMessage('标签：无')
        sampleDataMdText = ""
        for i in range(0, len(questionInfo['sampleData'])):
            sampleDataMdText += f'### 样例{i + 1}\n'
            '''
            sampleDataMdText += """
<table>
<tr><th>输入</th><th width=30></th><th>输出</th></tr>
<tr><td><code style="white-space: pre-line">{}</code></td><td></td><td><code style="white-space: pre-line">{}</code></td></tr>
</table>

""".format(questionInfo['sampleData'][i]['input'], questionInfo['sampleData'][i]['output'])
            '''
            sampleDataMdText += f'#### 输入 \n```\n' + questionInfo['sampleData'][i]['input'] + '\n```\n'
            sampleDataMdText += f'#### 输出 \n```\n' + questionInfo['sampleData'][i]['output'] + '\n```\n'

        mdText = ('### 题目描述 \n' + questionInfo['description-content'] + '\n' +
                  '### 输入描述 \n' + questionInfo['inputDescription-content'] + '\n' +
                  '### 输出描述 \n' + questionInfo['outputDescription-content'] + '\n' +
                  sampleDataMdText)
        uiMain.textEditQuestionDiscription.setMarkdown(mdText)
        uiMain.labelQuestionStatus.setText('通过/尝试： ' +
                                           str(questionInfo['viewerStatus']['passedCount']) + '/' +
                                           str(questionInfo['viewerStatus']['totalCount']))
        uiMain.comboBoxLanguage.clear()
        languages = [displayLanguage[lan] for lan in variables['exerciseInfo']['supportedLanguages']]
        uiMain.comboBoxLanguage.addItems(languages)
        uiMain.labelSubmitStatus.setText(uiMain.labelQuestionStatus.text())
        uiMain.textEditSubmit.setText(variables['exerciseInfo']['codeSnippet'])
        uiMain.progressBarExercise.hide()
        frameQuestionInitWorking = False
        uiMain.frameExercise.hide()
        uiMain.frameQuestion.show()

    def ErrorRecv(e: codiaError):
        global frameQuestionInitWorking
        ErrorDisplay(e, error_translate, "获取失败")
        uiMain.progressBarExercise.hide()
        frameQuestionInitWorking = False

    questionInfo = GetExercise(pid=requests_var['p'], eid=requests_var['e'],
                               lang='CPP', InfoRecv=ExerciseInfoRecv,
                               ErrorRecv=ErrorRecv)


# 初始化任务，为做题窗口信号绑定槽函数
def BeginMain(callback=None):
    QApplication.processEvents()
    nickname = logined()[1]
    if not nickname:
        nickname = "UNDEFINED"
    verified = net_var["me"]["verified"]
    if verified:
        uiMain.statusbar.showMessage(f"当前用户: {nickname}", 0)
    else:
        uiMain.statusbar.showMessage(f"当前用户: {nickname}（未验证）", 0)
        QMessageBox.information(None, "消息", "当前账号功能受限，请尽快完成联系方式验证。", QMessageBox.Ok)

    uiMain.statusbar.setFont(Font["status"])
    uiMain.pushButtonPackNext.clicked.connect(lambda: GetPage(before=variables["lastPid"]))
    uiMain.pushButtonPackPrevious.clicked.connect(lambda: GetPage(after=variables["firstPid"]))
    uiMain.progressBarPack.hide()
    uiMain.progressBarExercise.hide()
    uiMain.frameQuestion.hide()
    uiMain.frameHistory.hide()
    uiMain.frameSubmit.hide()
    uiMain.progressBarPack.setStyleSheet(Style["progressBar"])
    uiMain.progressBarExercise.setStyleSheet(Style["progressBar"])
    uiMain.textEditSubmit.setTabStopWidth(uiMain.textEditSubmit.font().pointSize() * 2)
    codeFont = QFont()
    codeFont.setFamily('Consolas')
    uiMain.textEditSubmit.setFont(codeFont)

    uiMain.listWidgetPack.itemClicked.connect(getSelectedPid)
    uiMain.listWidgetPack.itemDoubleClicked.connect(frameExerciseInit)
    uiMain.pushButtonPackOK.clicked.connect(frameExerciseInit)
    uiMain.pushButtonExerciseReturn.clicked.connect(ExerciseReturn)
    uiMain.pushButtonExerciseBegin.clicked.connect(BeginPack)
    uiMain.listWidgetExercise.itemClicked.connect(getSelectedEid)
    uiMain.listWidgetExercise.itemDoubleClicked.connect(frameQuestionInit)
    uiMain.pushButtonExerciseOK.clicked.connect(frameQuestionInit)
    uiMain.pushButtonQuestionReturn.clicked.connect(QuestionReturn)
    uiMain.pushButtonSubmit.clicked.connect(SubmitInit)
    uiMain.pushButtonSubmitCode.clicked.connect(
        lambda: SubmitCode(uiMain.comboBoxLanguageSubmit.currentText(),
                           uiMain.textEditSubmit.toPlainText()))
    uiMain.pushButtonSubmitBack.clicked.connect(SubmitReturn)
    uiMain.pushButtonSubmitFile.clicked.connect(SubmitFile)
    uiMain.pushButtonReadFromFile.clicked.connect(
        lambda : ReadFromFile(uiMain.comboBoxLanguageSubmit.currentText())
    )

    for i in range(0, variables['packPerPage']):
        AddItemToPackList(uiMain.listWidgetPack, colorName=['white', 'lightgray'][i % 2])

    uiMain.frameExercise.hide()
    uiMain.framePack.show()
    callback and callback()


def ReadFromFile(lang: str):
    fileWindow = QFileDialog()
    if lang == 'C++':
        fileWindow.setNameFilter('C++ 源文件(*.cpp *.cc *.C *.cxx *.c++)')
    elif lang == 'C':
        fileWindow.setNameFilter('C 源文件(*.c)')
    elif lang == 'Python':
        fileWindow.setNameFilter('Python 源文件(*.py)')
    elif lang == 'Java':
        fileWindow.setNameFilter('Java 源文件(*.java)')
    elif lang == 'JavaScript':
        fileWindow.setNameFilter('JavaScript 源文件(*.js)')
    elif lang == 'Go':
        fileWindow.setNameFilter('Go 源文件(*.go)')
    elif lang == 'Rust':
        fileWindow.setNameFilter('Rust 源文件(*.rs)')
    else:
        QMessageBox.critical(None, '错误', '未知错误。', QMessageBox.Ok)
    fileWindow.setDirectory('./')
    if fileWindow.exec_():
        fileChosen = fileWindow.selectedFiles()[0]
    else:
        QMessageBox.information(None, '提示', '请选择一个文件。', QMessageBox.Ok)
        return None
    with open(fileChosen, "r") as inputCode:
        codeSubmit = inputCode.read()
    uiMain.textEditSubmit.setText(codeSubmit)
    return codeSubmit


def SubmitFile():
    codeSubmit = ReadFromFile(uiMain.comboBoxLanguage.currentText())
    if codeSubmit:
        SubmitCode(uiMain.comboBoxLanguage.currentText(), codeSubmit)


def SubmitReturn():
    uiMain.frameSubmit.hide()
    uiMain.frameQuestion.show()


def SubmitCode(lang: str, code: str):
    try:
        submit_result = submit(requests_var['e'], requests_var['p'], dataLanguage[lang], code)
    except codiaError as e:
        ErrorDisplay(e, error_translate, "提交失败")
    else:
        if submit_result:
            QMessageBox.information(None, '提交成功', '提交成功，请在历史记录中查看评测结果', QMessageBox.Ok)
            uiMain.frameSubmit.hide()
            uiMain.frameQuestion.show()
        else:
            QMessageBox.critical(None, '提交失败', '请检查语言选择是否正确。', QMessageBox.Ok)


def SubmitInit():
    languages = [displayLanguage[lang] for lang in variables['exerciseInfo']['supportedLanguages']]
    uiMain.comboBoxLanguageSubmit.clear()
    uiMain.comboBoxLanguageSubmit.addItems(languages)
    uiMain.frameQuestion.hide()
    uiMain.frameSubmit.show()


def QuestionReturn():
    uiMain.statusbar.clearMessage()
    uiMain.statusbar.showMessage("当前用户:" + net_var['me']['nickname'])
    uiMain.frameQuestion.hide()
    uiMain.frameExercise.show()
    windowMain.setWindowTitle(variables['packInfo']['nodes'][variables['currentPackRow']]['name'])


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

    def __init__(self, *args, before=None, after=None, **kargs):
        super(_GetPack, self).__init__(*args, **kargs)
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
    uiMain.progressBarPack.setValue(90)
    threadGetPack.start()


# 翻页
def GetPage(before=None, after=None):
    if before and after:
        return False 
    uiMain.progressBarPack.setValue(0)
    uiMain.progressBarPack.show()
    uiMain.pushButtonPackNext.setEnabled(False)
    uiMain.pushButtonPackPrevious.setEnabled(False)

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
        uiMain.progressBarPack.hide()
        UpdatePage()

    def ErrorRecv(e: codiaError):
        ErrorDisplay(e, error_translate, "获取失败")
        uiMain.progressBarPack.hide()
        try:
            UpdatePage()
        except:
            pass

    GetPack(before=before, after=after, InfoRecv=PackInfoRecv, ErrorRecv=ErrorRecv)


def GetPackWidget(data: dict):
    widget = QWidget()
    layoutPackMain = QHBoxLayout()
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
    layoutPackMain.addWidget(labelPackFinish)
    layoutPackMain.addLayout(layoutPackRight)
    layoutPackMain.setStretchFactor(labelPackFinish, 1)
    layoutPackMain.setStretchFactor(layoutPackRight, 8)

    widget.setLayout(layoutPackMain)
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
