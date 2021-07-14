from datetime import datetime, timedelta
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexer import RegexLexer
from pygments.lexers import CLexer, CppLexer, PythonLexer, jvm, javascript, go, rust
from re import search
from sys import platform

from PyQt5.QtCore import Qt, QSize, QThread, pyqtSignal
from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import QAbstractItemView, QFileDialog
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout
from PyQt5.QtWidgets import QComboBox, QLabel, QListWidgetItem, QTextEdit, QWidget
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox

from codiaclient import net_var
from codiaclient.network import get_pack, show_pack, start_pack, logined, get_exercise
from codiaclient.network import submit, get_data
from codiaclient.report import Error as codiaError, error_translate
from codiaclient.requests import variables as requests_var
from codiaclientgui.utils import QPalette, Font, Palette, Style, ErrorDisplay, NewListWidget, AdjustWindowSize
from mainWindow import Ui_windowMain


variables = {
    "pageNumber": 0,
    "packPerPage": 8,
    "lastPid": None,
    "firstPid": None,
    "hasNext": True,
    "packInfo": {},
    "currentPackRow": 0,
    "currentHistoryRow": 0,
    "exerciseInfo": None,
    "submitHistory": [],
    "testDataCount": 0,
    "workingStatus": {
        "frameExerciseInit": False,
        "frameQuestionInit": False,
    }
}


toDisplay = {
    "CPP": "C++",
    "C": "C",
    "JAVA": "Java",
    "JAVASCRIPT": "JavaScript",
    "GO": "Go",
    "RUST": "Rust",
    "PYTHON": "Python",
    "passed": "通过",
    "compile error": "编译错误",
    "wrong answer": "答案错误",
    "runtime error": "运行时错误",
    "time limit exceeds": "时间超限",
    "memory limit exceeds": "内存超限",
    "": "正在评测"
}
toData = {val: key for key, val in toDisplay.items()}


class EmptyLexer(RegexLexer):
    name = 'Empty'
    tokens = {'root': []}

currentLexer = EmptyLexer()
currentFormatter = HtmlFormatter(noclasses = True, nobackground = True)


def GetLexer(lang: str, callback=None) -> None:
    global currentLexer
    if lang == "C" or lang == toDisplay["C"]: currentLexer = CLexer()
    elif lang == "CPP" or lang == toDisplay["CPP"]: currentLexer = CppLexer()
    elif lang == "PYTHON" or lang == toDisplay["PYTHON"]: currentLexer = PythonLexer()
    elif lang == "JAVA" or lang == toDisplay["JAVA"]: currentLexer = jvm.JavaLexer()
    elif lang == "JAVASCRIPT" or lang == toDisplay["JAVASCRIPT"]: currentLexer = javascript.JavascriptLexer()
    elif lang == "GO" or lang == toDisplay["GO"]: currentLexer = go.GoLexer()
    elif lang == "RUST" or lang == toDisplay["RUST"]: currentLexer = rust.RustLexer()
    else: currentLexer = EmptyLexer()
    callback and callback()


def Str(x) -> str:
    if x: return str(x)
    return ""


class MyThread(QThread):
    infoSignal = pyqtSignal([dict], [list])
    errorSignal = pyqtSignal(codiaError)

    def __init__(self, *args, RunMethod, **kargs):
        super(MyThread, self).__init__(*args, **kargs)
        self.working = True
        self.RunMethod = RunMethod

    def __del__(self):
        self.working = False
        self.wait()

    def run(self):
        try:
            self.Info = self.RunMethod()
        except codiaError as e:
            self.errorSignal.emit(e)
        else:
            self.infoSignal[type(self.Info)].emit(self.Info)


# 代码高亮
def HighlightTextEdit(textEdit: QTextEdit, text=None, lang=None):
    global currentLexer, currentFormatter
    tempLexer = currentLexer
    if lang: GetLexer(lang)
    if text == None: text = textEdit.toPlainText()
    if text:
        pos = textEdit.textCursor().position()
        text = highlight(text, currentLexer, currentFormatter).replace("\r\n", "\n")[:-1]
        textEdit.setHtml(text)
        cursor = textEdit.textCursor()
        # 在文末换行时，下一条语句无法执行，此时若无此语句，光标将跳到文件头。加此语句可使得光标在文件尾。
        cursor.movePosition(QTextCursor.End)
        # 文末换行会出bug，若要解决可以在文末加一空格，在空格前换行即可。
        cursor.setPosition(pos)
        textEdit.setTextCursor(cursor)
    else:
        textEdit.setText("")
    currentLexer = tempLexer

# 获取题包内容信息的多线程
def ShowPack(pid, InfoRecv=lambda: None, ErrorRecv=lambda: None):
    global threadShowPack # extremely essential!
    threadShowPack = MyThread(RunMethod=lambda: show_pack(pid=pid))
    threadShowPack.infoSignal.connect(InfoRecv)
    threadShowPack.errorSignal.connect(ErrorRecv)
    uiMain.progressBarPack.setValue(90)
    threadShowPack.start()


def frameExerciseInit():
    if variables["workingStatus"]["frameExerciseInit"]:
        return
    if not uiMain.listWidgetPack.selectedIndexes():
        QMessageBox.information(None, "提示", "请选择一个题包", QMessageBox.Ok)
        return

    getSelectedPid()
    uiMain.progressBarPack.setValue(0)
    uiMain.progressBarPack.show()
    variables["workingStatus"]["frameExerciseInit"] = True

    def ErrorRecv(e: codiaError):
        ErrorDisplay(e, error_translate, "获取失败")
        uiMain.progressBarPack.hide()
        variables["workingStatus"]["frameExerciseInit"] = False

    def exerciseListInfoRecv(exerciseListInfo):
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
        if exerciseListInfo["description"]:
            uiMain.textEditExerciseDiscription.setMarkdown(exerciseListInfo["description"]["content"])
        else:
            uiMain.textEditExerciseDiscription.setText("本题包未设置题包描述")
        variables["exerciseListInfo"] = exerciseListInfo["codingExercises"]["nodes"]
        uiMain.listWidgetExercise.clear()
        if variables["exerciseListInfo"]:
            for exercise in variables["exerciseListInfo"]:
                AddItemToQuestionList(exercise)
        uiMain.progressBarPack.hide()
        variables["workingStatus"]["frameExerciseInit"] = False
        uiMain.framePack.hide()
        uiMain.frameExercise.show()

    ShowPack(pid=requests_var["p"], InfoRecv=exerciseListInfoRecv, ErrorRecv=ErrorRecv)


def AddItemToQuestionList(data: dict):
    item = QListWidgetItem()
    from codiaclientgui.utils import screenBASE
    item.setSizeHint(QSize(960 * screenBASE, 65 * screenBASE))
    widget = GetExerciseWidget(data)
    widget.setCursor(Qt.PointingHandCursor)
    uiMain.listWidgetExercise.addItem(item)
    uiMain.listWidgetExercise.setItemWidget(item, widget)


def GetExerciseWidget(data: dict):
    if data["viewerStatus"]["passedCount"] > 0:
        labelExerciseStatus = QLabel("已通过")
        labelExerciseStatus.setPalette(Palette[QPalette.Text]["green"])
    else:
        labelExerciseStatus = QLabel("未通过")
        labelExerciseStatus.setPalette(Palette[QPalette.Text]["red"])
    labelExerciseTitle = QLabel(Str(data["title"]))
    labelExercisePassed = QLabel(f"""通过数：{data["viewerStatus"]["passedCount"]}""")
    labelExerciseSubmit = QLabel(f"""提交数：{data["viewerStatus"]["totalCount"]}""")
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
    if variables["workingStatus"]["frameQuestionInit"]:
        return
    selected = uiMain.listWidgetExercise.currentIndex().row()
    variables["currentExerciseRow"] = selected
    requests_var["e"] = variables["exerciseListInfo"][selected]["id"]


def ExerciseReturn():
    uiMain.frameExercise.hide()
    uiMain.framePack.show()
    uiMain.pushButtonExerciseBegin.show()
    windowMain.setWindowTitle("题包列表")


def BeginPack():
    try:
        start_pack(requests_var["p"])
    except codiaError as e:
        ErrorDisplay(e, error_translate)
    else:
        QMessageBox.information(None, "消息", "成功开始题包", QMessageBox.Ok)
        uiMain.pushButtonExerciseBegin.hide()
        variables["packInfo"]["nodes"][variables["currentPackRow"]]["ongoing"] = True


# 初始化任务，新建一个做题窗体和对应的ui
def MainInit(callback=None):
    global windowMain, uiMain
    windowMain = QMainWindow()
    windowMain.setFont(Font["main"])
    uiMain = Ui_windowMain()
    uiMain.setupUi(windowMain)
    AdjustWindowSize(windowMain)
    BeginMain(callback=callback)
    windowMain.show()
    GetPage()


# 获取题目信息的多线程
def GetExercise(pid, eid, lang, InfoRecv=lambda: None, ErrorRecv=lambda: None):
    global threadGetExercise # extremely essential!
    threadGetExercise = MyThread(RunMethod=lambda: get_exercise(eid=eid, pid=pid, lang=lang))
    threadGetExercise.infoSignal.connect(InfoRecv)
    threadGetExercise.errorSignal.connect(ErrorRecv)
    uiMain.progressBarExercise.setValue(90)
    threadGetExercise.start()


def frameQuestionInit():
    if variables["workingStatus"]["frameQuestionInit"]:
        return
    if not uiMain.listWidgetExercise.selectedIndexes():
        QMessageBox.information(None, "消息", "请选择一个题目", QMessageBox.Ok)
        return

    getSelectedEid()
    variables["workingStatus"]["frameQuestionInit"] = True
    uiMain.progressBarExercise.setValue(0)
    uiMain.progressBarExercise.show()

    def ExerciseInfoRecv(questionInfo):
        variables["exerciseInfo"] = questionInfo
        windowMain.setWindowTitle(questionInfo["title"])
        uiMain.statusbar.clearMessage()
        if questionInfo["tags"]:
            uiMain.statusbar.showMessage("标签：" + ", ".join(questionInfo["tags"]))
        else:
            uiMain.statusbar.showMessage("标签：无")

        sampleDataMdText = ""
        for i in range(0, len(questionInfo["sampleData"])):
            sampleDataMdText += f"### 样例{i + 1}\n"
            sampleDataMdText += f"#### 输入 \n```\n" + Str(questionInfo["sampleData"][i]["input"]) + "\n```\n"
            sampleDataMdText += f"#### 输出 \n```\n" + Str(questionInfo["sampleData"][i]["output"]) + "\n```\n"

        mdText = ""
        if questionInfo["description-content"]:
            mdText += "### 题目描述 \n" + Str(questionInfo["description-content"]) + "\n"
        if questionInfo["inputDescription-content"]:
            mdText += "### 题目描述 \n" + Str(questionInfo["inputDescription-content"]) + "\n"
        if questionInfo["outputDescription-content"]:
            mdText += "### 题目描述 \n" + Str(questionInfo["outputDescription-content"]) + "\n"
        mdText += sampleDataMdText
        uiMain.textEditQuestionDiscription.setMarkdown(mdText)

        passDivTotal = f"""{questionInfo["viewerStatus"]["passedCount"]}/{questionInfo["viewerStatus"]["totalCount"]}"""
        uiMain.labelQuestionStatus.setText(f"通过/尝试： {passDivTotal}")

        uiMain.comboBoxLanguage.clear()
        uiMain.comboBoxLanguage.addItem("请选择提交语言")
        for lang in variables["exerciseInfo"]["supportedLanguages"]:
            uiMain.comboBoxLanguage.addItem(toDisplay[lang])

        uiMain.labelSubmitStatus.setText(uiMain.labelQuestionStatus.text())

        code = variables["exerciseInfo"]["codeSnippet"]
        if not code:
            uiMain.textEditSubmit.setText("")
        else:
            HighlightTextEdit(textEdit=uiMain.textEditSubmit, text=code)

        def TryHighlight():
            uiMain.textEditSubmit.textChanged.disconnect() # 否则将无限循环。
            HighlightTextEdit(textEdit=uiMain.textEditSubmit)
            uiMain.textEditSubmit.textChanged.connect(TryHighlight)

        uiMain.textEditSubmit.textChanged.connect(TryHighlight)

        uiMain.progressBarExercise.hide()
        variables["workingStatus"]["frameQuestionInit"] = False
        uiMain.frameExercise.hide()
        uiMain.frameQuestion.show()

    def ErrorRecv(e: codiaError):
        ErrorDisplay(e, error_translate, "获取失败")
        uiMain.progressBarExercise.hide()
        variables["workingStatus"]["frameQuestionInit"] = False

    GetExercise(pid=requests_var["p"], eid=requests_var["e"],
                lang="CPP", InfoRecv=ExerciseInfoRecv,
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
        QMessageBox.information(None, "消息", "当前账号功能受限，请尽快完成联系方式验证", QMessageBox.Ok)

    uiMain.statusbar.setFont(Font["status"])
    uiMain.pushButtonPackNext.clicked.connect(lambda: GetPage(before=variables["lastPid"]))
    uiMain.pushButtonPackPrevious.clicked.connect(lambda: GetPage(after=variables["firstPid"]))
    uiMain.progressBarPack.hide()
    uiMain.progressBarExercise.hide()
    uiMain.progressBarSubmit.hide()
    uiMain.progressBarHistory.hide()
    uiMain.frameQuestion.hide()
    uiMain.frameHistory.hide()
    uiMain.frameSubmit.hide()
    uiMain.frameExercise.hide()
    uiMain.frameCode.hide()
    uiMain.frameTestData.hide()
    uiMain.progressBarPack.setStyleSheet(Style["progressBar"])
    uiMain.progressBarExercise.setStyleSheet(Style["progressBar"])
    uiMain.progressBarSubmit.setStyleSheet(Style["progressBar"])
    uiMain.progressBarHistory.setStyleSheet(Style["progressBar"])
    if platform == "win32":
        uiMain.textEditCode.setTabStopWidth(uiMain.textEditSubmit.font().pointSize() * 4)
        uiMain.textEditSubmit.setTabStopWidth(uiMain.textEditSubmit.font().pointSize() * 4)
    else:
        uiMain.textEditCode.setTabStopWidth(uiMain.textEditSubmit.font().pointSize() * 2)
        uiMain.textEditSubmit.setTabStopWidth(uiMain.textEditSubmit.font().pointSize() * 2)

    # uiMain.listWidgetPack.itemClicked.connect(getSelectedPid)
    uiMain.listWidgetPack.itemDoubleClicked.connect(frameExerciseInit)
    uiMain.pushButtonPackOK.clicked.connect(frameExerciseInit)
    uiMain.pushButtonExerciseReturn.clicked.connect(ExerciseReturn)
    uiMain.pushButtonExerciseBegin.clicked.connect(BeginPack)
    # uiMain.listWidgetExercise.itemClicked.connect(getSelectedEid)
    uiMain.listWidgetExercise.itemDoubleClicked.connect(frameQuestionInit)
    uiMain.listWidgetPackHistory.itemDoubleClicked.connect(frameTestDataInit)
    uiMain.pushButtonExerciseOK.clicked.connect(frameQuestionInit)
    uiMain.pushButtonQuestionReturn.clicked.connect(QuestionReturn)
    uiMain.pushButtonSubmit.clicked.connect(SubmitInit)
    uiMain.pushButtonSubmitCode.clicked.connect(
        lambda: SubmitCode(uiMain.comboBoxLanguageSubmit.currentText(),
                           uiMain.textEditSubmit.toPlainText()))
    uiMain.pushButtonSubmitBack.clicked.connect(SubmitReturn)
    uiMain.pushButtonSubmitFile.clicked.connect(SubmitFile)
    uiMain.pushButtonReadFromFile.clicked.connect(
        lambda: ReadFromFile(uiMain.comboBoxLanguageSubmit.currentText())
    )
    uiMain.pushButtonHistory.clicked.connect(frameHistoryInit)
    uiMain.pushButtonHistoryBack.clicked.connect(HistoryReturn)
    uiMain.pushButtonCodeBack.clicked.connect(CodeReturn)
    uiMain.pushButtonTestDataBack.clicked.connect(TestDataReturn)
    uiMain.pushButtonShowCode.clicked.connect(ShowCode)
    uiMain.pushButtonShowTestData.clicked.connect(ShowTestData)
    uiMain.pushButtonSubmitCodeDetails.clicked.connect(frameTestDataInit)
    uiMain.comboBoxLanguageSubmit.currentIndexChanged.connect(
        lambda: GetLexer(lang=uiMain.comboBoxLanguageSubmit.currentText(),
                         callback=lambda: HighlightTextEdit(textEdit=uiMain.textEditSubmit))
    )

    uiMain.listWidgetPackHistory.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
    uiMain.listWidgetExercise.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
    uiMain.listWidgetData.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
    uiMain.listWidgetPack.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
    uiMain.listWidgetPack.setPalette(Palette[QPalette.Text]["black"])
    uiMain.listWidgetExercise.setPalette(Palette[QPalette.Text]["black"])
    uiMain.listWidgetPackHistory.setPalette(Palette[QPalette.Text]["black"])
    uiMain.listWidgetData.setPalette(Palette[QPalette.Text]["black"])

    for i in range(0, variables["packPerPage"]):
        AddItemToPackList(uiMain.listWidgetPack)

    uiMain.framePack.show()
    callback and callback()


def frameCodeInit():
    code = variables["submitHistory"][variables["currentHistoryRow"]]["solution"]["asset"]["content"]
    if not code:
        uiMain.textEditCode.setText("")
    else:
        HighlightTextEdit(textEdit=uiMain.textEditCode, text=code,
            lang=variables["submitHistory"][variables["currentHistoryRow"]]["solution"]['lang'])


def frameTestDataInit():
    if not uiMain.listWidgetPackHistory.selectedItems():
        QMessageBox.information(None, "提示", "请选中一条历史记录", QMessageBox.Ok)
        return
    variables["currentHistoryRow"] = uiMain.listWidgetPackHistory.selectedIndexes()[0].row()
    testData = variables["submitHistory"][variables["currentHistoryRow"]]["submission"]["reports"]
    index = 1
    for data in testData:
        if data["key"] == "score":
            variables["testDataCount"] = int(data["value"].split("/")[1])
    uiMain.listWidgetData.clear()
    for data in testData:
        if (data["key"] != "score" and data["key"] != "time elapsed"
                and data["key"] != "memory consumed" and data["key"] != "error"):
            AddItemToTestDataList(index, data["value"])
            index += 1
    uiMain.frameHistory.hide()
    uiMain.frameTestData.show()


def AddItemToTestDataList(index: int, status: str):
    item = QListWidgetItem()
    from codiaclientgui.utils import screenBASE
    item.setSizeHint(QSize(960 * screenBASE, 65 * screenBASE))
    widget = GetTestDataWidGet(index, status)
    uiMain.listWidgetData.addItem(item)
    uiMain.listWidgetData.setItemWidget(item, widget)


def GetTestDataWidGet(index: int, status: str):
    mainLayout = QHBoxLayout()
    statusLabel = QLabel()
    testDataLabel = QLabel()
    getScoreLabel = QLabel()

    statusLabel.setText(toDisplay[status])
    SetStatusColor(statusLabel)
    testDataLabel.setText(f"测试点 {index}")
    if status == "passed":
        getScoreLabel.setText("得分：%.1f" % (100 / variables["testDataCount"]))
    else:
        getScoreLabel.setText("得分：0")

    mainLayout.addWidget(testDataLabel)
    mainLayout.addWidget(statusLabel)
    mainLayout.addWidget(getScoreLabel)

    mainLayout.setStretchFactor(testDataLabel, 1)
    mainLayout.setStretchFactor(statusLabel, 2)
    mainLayout.setStretchFactor(getScoreLabel, 1)

    widget = QWidget()
    widget.setLayout(mainLayout)
    widget.setCursor(Qt.PointingHandCursor)
    return widget


def ShowCode():
    frameCodeInit()
    uiMain.frameTestData.hide()
    uiMain.frameCode.show()


def ShowTestData():
    uiMain.frameCode.hide()
    uiMain.frameTestData.show()


def CodeReturn():
    uiMain.frameCode.hide()
    uiMain.frameHistory.show()


def TestDataReturn():
    uiMain.frameTestData.hide()
    uiMain.frameHistory.show()


def HistoryReturn():
    uiMain.frameHistory.hide()
    uiMain.frameQuestion.show()


def GetHistory(eid, pid, cnt, InfoRecv=lambda: None, ErrorRecv=lambda: None):
    global threadGetHistory # extremely essential!
    threadGetHistory = MyThread(RunMethod=lambda: get_data(eid=eid, pid=pid, cnt=cnt))
    threadGetHistory.infoSignal[list].connect(InfoRecv)
    threadGetHistory.errorSignal.connect(ErrorRecv)
    try:
        uiMain.progressBarHistory.Anime["progress"].setDuration(1500 * (cnt // 100 + 1))
    except:
        pass
    uiMain.progressBarHistory.setValue(90)
    threadGetHistory.start()


def frameHistoryInit():
    totalCount = variables["exerciseListInfo"][variables["currentExerciseRow"]]["viewerStatus"]["totalCount"]
    if totalCount == 0:
        QMessageBox.information(None, "提示", "本题无提交记录", QMessageBox.Ok)
        return
    uiMain.progressBarHistory.setValue(0)
    uiMain.listWidgetPackHistory.clear()
    uiMain.progressBarHistory.show()
    uiMain.frameQuestion.hide()
    uiMain.frameHistory.show()

    def historyInfoRecv(historyInfo):
        uiMain.progressBarHistory.setValue(95)
        historyInfo.reverse()
        variables["submitHistory"] = historyInfo
        uiMain.listWidgetPackHistory.clear()
        for data in historyInfo:
            AddItemToHistoryList(data)
        uiMain.progressBarHistory.hide()

    def ErrorRecv(e: codiaError):
        ErrorDisplay(e, error_translate, "获取失败")
        uiMain.progressBarHistory.hide()

    GetHistory(eid=requests_var["e"], pid=requests_var["p"], cnt=totalCount, InfoRecv=historyInfoRecv,
               ErrorRecv=ErrorRecv)


def AddItemToHistoryList(data: dict):
    item = QListWidgetItem()
    from codiaclientgui.utils import screenBASE
    item.setSizeHint(QSize(960 * screenBASE, 65 * screenBASE))
    widget = GetHistoryWidget(data)
    if not widget.isEnabled():
        item.setFlags(item.flags() & ~Qt.ItemIsSelectable)
    uiMain.listWidgetPackHistory.addItem(item)
    uiMain.listWidgetPackHistory.setItemWidget(item, widget)


def GetHistoryWidget(data: dict):
    mainLayout = QHBoxLayout()
    elapseLayout = QVBoxLayout()
    statusLabel = QLabel()
    languageLabel = QLabel()
    timeLabel = QLabel()
    codeLengthLabel = QLabel()
    timeElapsedLabel = QLabel()
    spaceElapsedLabel = QLabel()
    scoreLabel = QLabel()

    if data["scoreRate"] == 1:
        statusLabel.setText("通过")
        statusLabel.setPalette(Palette[QPalette.Text]["green"])
    else:
        errorType = ""
        for i in data["submission"]["reports"]:
            if i["key"] == "error":
                errorType = i["value"]
        if not errorType:
            for i in data["submission"]["reports"]:
                if (i["value"] != "passed" and i["key"] != "memory consumed"
                        and i["key"] != "time elapsed" and i["key"] != "score"):
                    errorType = i["value"]
                    break
        statusLabel.setText(toDisplay[errorType])
        SetStatusColor(statusLabel)
    languageLabel.setText(toDisplay[data["solution"]["lang"]])
    try:
        scoreLabel.setText("得分：%.1f" % (data["scoreRate"] * 100))
    except:
        pass
    timeLabel.setText("提交时间：" +
                      (datetime.strptime(search(r"^[^.]*", data["time"].replace("T", " ")).group(),
                                         "%Y-%m-%d %H:%M:%S") + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S"))
    codeLengthLabel.setText("代码长度：" + Str(len(data["solution"]["asset"]["content"])) + " B")
    for i in data["submission"]["reports"]:
        if i["key"] == "memory consumed":
            spaceElapsedLabel.setText("空间消耗：" + i["value"])
        elif i["key"] == "time elapsed":
            timeElapsedLabel.setText("时间消耗：" + i["value"])
    statusLabel.setAlignment(Qt.AlignCenter)

    elapseLayout.addWidget(timeElapsedLabel)
    elapseLayout.addWidget(spaceElapsedLabel)
    mainLayout.addWidget(statusLabel)
    mainLayout.addWidget(languageLabel)
    mainLayout.addWidget(timeLabel)
    mainLayout.addWidget(codeLengthLabel)
    mainLayout.addLayout(elapseLayout)
    mainLayout.addWidget(scoreLabel)

    mainLayout.setStretchFactor(statusLabel, 2)
    mainLayout.setStretchFactor(languageLabel, 1)
    mainLayout.setStretchFactor(timeLabel, 4)
    mainLayout.setStretchFactor(codeLengthLabel, 2)
    mainLayout.setStretchFactor(elapseLayout, 3)
    mainLayout.setStretchFactor(scoreLabel, 2)

    widget = QWidget()
    widget.setLayout(mainLayout)
    widget.setCursor(Qt.PointingHandCursor)
    if not data["submission"]["reports"]:
        widget.setEnabled(False)
    return widget


def SetStatusColor(statusLabel: QLabel):
    if statusLabel.text() == "答案错误":
        statusLabel.setPalette(Palette[QPalette.Text]["red"])
    elif statusLabel.text() == "运行时错误":
        statusLabel.setPalette(Palette[QPalette.Text]["purple"])
    elif statusLabel.text() == "超时":
        statusLabel.setPalette(Palette[QPalette.Text]["darkblue"])
    elif statusLabel.text() == "通过":
        statusLabel.setPalette(Palette[QPalette.Text]["green"])
    else:
        statusLabel.setPalette(Palette[QPalette.Text]["gray"])


def ReadFromFile(lang: str):
    # if lang == "请选择提交语言":
    #     QMessageBox.information(None, "提示", "请选择一种提交语言", QMessageBox.Ok)
    #     return
    fileWindow = QFileDialog()
    if lang == "C++":
        fileWindow.setNameFilter("C++ 源文件(*.cpp *.cc *.C *.cxx *.c++)")
    elif lang == "C":
        fileWindow.setNameFilter("C 源文件(*.c)")
    elif lang == "Python":
        fileWindow.setNameFilter("Python 源文件(*.py)")
    elif lang == "Java":
        fileWindow.setNameFilter("Java 源文件(*.java)")
    elif lang == "JavaScript":
        fileWindow.setNameFilter("JavaScript 源文件(*.js)")
    elif lang == "Go":
        fileWindow.setNameFilter("Go 源文件(*.go)")
    elif lang == "Rust":
        fileWindow.setNameFilter("Rust 源文件(*.rs)")
    # else:
    #     QMessageBox.critical(None, "错误", "未知错误", QMessageBox.Ok)
    # fileWindow.setDirectory("./")
    if fileWindow.exec_():
        fileChosen = fileWindow.selectedFiles()[0]
    else:
        QMessageBox.information(None, "提示", "请选择一个文件", QMessageBox.Ok)
        return None
    with open(fileChosen, "r") as inputCode:
        codeSubmit = inputCode.read()
    uiMain.textEditSubmit.setText(codeSubmit)
    return codeSubmit


def SubmitFile():
    if uiMain.comboBoxLanguage.currentText() == "请选择提交语言":
        QMessageBox.information(None, "提示", "请选择一种提交语言", QMessageBox.Ok)
        return
    codeSubmit = ReadFromFile(uiMain.comboBoxLanguage.currentText())
    if codeSubmit:
        SubmitCode(uiMain.comboBoxLanguage.currentText(), codeSubmit)


def SubmitReturn():
    uiMain.frameSubmit.hide()
    uiMain.frameQuestion.show()


def Submit(pid, eid, lang, code, InfoRecv=lambda: None, ErrorRecv=lambda: None):
    global threadSubmit # extremely essential!
    threadSubmit = MyThread(RunMethod=lambda: submit(eid=eid, pid=pid, lang=lang, solutioncode=code))
    threadSubmit.infoSignal.connect(InfoRecv)
    threadSubmit.errorSignal.connect(ErrorRecv)
    uiMain.progressBarSubmit.setValue(90)
    threadSubmit.start()


def SubmitCode(lang: str, code: str):
    if lang == "请选择提交语言":
        QMessageBox.information(None, "提示", "请选择一种提交语言", QMessageBox.Ok)
        return

    uiMain.progressBarSubmit.setValue(0)
    uiMain.progressBarSubmit.show()

    def ErrorRecv(e: codiaError):
        ErrorDisplay(e, error_translate, "获取失败")
        uiMain.progressBarSubmit.hide()

    def submitInfoRecv(submitInfo):
        if submitInfo:
            QMessageBox.information(None, "提交成功", "提交成功，请在历史记录中查看评测结果", QMessageBox.Ok)
            variables["exerciseListInfo"][variables["currentExerciseRow"]]["viewerStatus"]["totalCount"] += 1
            uiMain.frameSubmit.hide()
            uiMain.frameQuestion.show()
        else:
            QMessageBox.critical(None, "提交失败", "请检查语言选择是否正确", QMessageBox.Ok)
        uiMain.progressBarSubmit.hide()

    Submit(pid=requests_var["p"], eid=requests_var["e"], lang=toData[lang], code=code, InfoRecv=submitInfoRecv,
           ErrorRecv=ErrorRecv)


def SubmitInit():
    languages = [toDisplay[lang] for lang in variables["exerciseInfo"]["supportedLanguages"]]
    uiMain.comboBoxLanguageSubmit.clear()
    if uiMain.comboBoxLanguage.currentText() == "请选择提交语言":
        uiMain.comboBoxLanguageSubmit.addItem("请选择提交语言")
    uiMain.comboBoxLanguageSubmit.addItems(languages)
    if uiMain.comboBoxLanguage.currentText() != "请选择提交语言":
        uiMain.comboBoxLanguageSubmit.setCurrentIndex(uiMain.comboBoxLanguage.currentIndex() - 1)
    uiMain.frameQuestion.hide()
    uiMain.frameSubmit.show()


def QuestionReturn():
    uiMain.statusbar.clearMessage()
    uiMain.statusbar.showMessage("当前用户:" + net_var["me"]["nickname"])
    uiMain.frameQuestion.hide()
    uiMain.frameExercise.show()
    windowMain.setWindowTitle(variables["packInfo"]["nodes"][variables["currentPackRow"]]["name"])


# 在翻页后更新页面
def UpdatePage():
    variables["hasNext"] = variables["packInfo"]["pageInfo"]["hasPreviousPage"]
    packList = variables["packInfo"]["nodes"]
    variables["firstPid"] = packList[0]["id"]
    variables["lastPid"] = packList[-1]["id"]
    uiMain.pushButtonPackNext.setEnabled(variables["hasNext"] or not variables["pageNumber"])
    uiMain.pushButtonPackPrevious.setEnabled(variables["pageNumber"] > 1)
    uiMain.labelPackPage.setText("第 {} 页".format(variables["pageNumber"]))
    for i in range(0, uiMain.listWidgetPack.count()):
        uiMain.listWidgetPack.takeItem(0)
    packList += [None] * (variables["packPerPage"] - len(packList))
    for i in range(0, variables["packPerPage"]):
        AddItemToPackList(uiMain.listWidgetPack, packList[i])


# 获取题包信息的多线程
def GetPack(before=None, after=None, InfoRecv=lambda: None, ErrorRecv=lambda: None):
    global threadGetPack # extremely essential!
    threadGetPack = MyThread(RunMethod=lambda: get_pack(cnt=variables["packPerPage"], before=before, after=after))
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
        variables["packInfo"]["nodes"].reverse()
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


def AddItemToPackList(packList: NewListWidget, data: dict = {}):
    item = QListWidgetItem()
    from codiaclientgui.utils import screenBASE
    item.setSizeHint(QSize(960 * screenBASE, 65 * screenBASE))
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
