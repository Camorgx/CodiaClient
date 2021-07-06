import sys
from PyQt5.QtCore import Qt, QPropertyAnimation, pyqtSignal, pyqtProperty, QEasingCurve
from PyQt5.QtGui import QFont, QPalette, QBrush, QColor, QPainterPath, QPainter, QPen
from PyQt5.QtWidgets import QMessageBox, QPushButton, QLabel, QProgressBar, QListWidget, QDesktopWidget

Font = {
    'main': QFont(),
    'status': QFont(),
}

Color = {
    'lightgray': QColor(229, 230, 231),
    'gray': QColor(150, 151, 152),
    'green': QColor(80, 160, 30),
    'red': QColor(160, 0, 30),
    'white': QColor(255, 255, 255),
    'disabled': QColor(120, 120, 120),
    'purple': QColor(128, 0, 128),
    'darkblue': QColor(10, 40, 120)
}

Palette = {}

Palette[QPalette.Text] = {
    "green": QPalette(),
    "red": QPalette(),
    "gray": QPalette(),
    'purple': QPalette(),
    'darkblue': QPalette()
}

Palette[QPalette.Window] = {
    "white": QPalette(),
    "lightgray": QPalette(),
}

Style = {
    "progressBar": "",
}

if sys.platform == 'win32':
    Font['main'].setFamily("Microsoft YaHei")
    Font['main'].setPointSize(10)
    Font['status'].setFamily("KaiTi")
    Font['status'].setPointSize(10)
    Style['progressBar'] = "QProgressBar { max-height: 12px; border: none; border-radius: 6px; text-align: center; background-color: #FFFFFF } QProgressBar::chunk { border: none; border-radius: 6px; background: qlineargradient(spread: pad, x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #05A01E, stop: 1 #75C090) }"
elif sys.platform == 'darwin':
    Font['main'].setFamily("PingFang SC")
    Font['main'].setPointSize(13)
    Font['status'].setFamily(".AppleSystemUIFont")
    Font['status'].setPointSize(13)
else:
    Font['main'].setFamily("Microsoft YaHei")
    Font['main'].setPointSize(13)

greenBrush = QBrush(Color['green'])
greenBrush.setStyle(Qt.SolidPattern)
Palette[QPalette.Text]['green'].setBrush(QPalette.Active, QPalette.Text, greenBrush)
Palette[QPalette.Text]['green'].setBrush(QPalette.Inactive, QPalette.Text, greenBrush)
greenBrush.setColor(Color['disabled'])
Palette[QPalette.Text]['green'].setBrush(QPalette.Disabled, QPalette.Text, greenBrush)

redBrush = QBrush(Color['red'])
redBrush.setStyle(Qt.SolidPattern)
Palette[QPalette.Text]['red'].setBrush(QPalette.Active, QPalette.Text, redBrush)
Palette[QPalette.Text]['red'].setBrush(QPalette.Inactive, QPalette.Text, redBrush)
redBrush.setColor(Color['disabled'])
Palette[QPalette.Text]['red'].setBrush(QPalette.Disabled, QPalette.Text, redBrush)

grayBrush = QBrush(Color['gray'])
grayBrush.setStyle(Qt.SolidPattern)
Palette[QPalette.Text]['gray'].setBrush(QPalette.Active, QPalette.Text, grayBrush)
Palette[QPalette.Text]['gray'].setBrush(QPalette.Inactive, QPalette.Text, grayBrush)
grayBrush.setColor(Color['disabled'])
Palette[QPalette.Text]['gray'].setBrush(QPalette.Disabled, QPalette.Text, grayBrush)

purpleBrush = QBrush(Color['purple'])
purpleBrush.setStyle(Qt.SolidPattern)
Palette[QPalette.Text]['purple'].setBrush(QPalette.Active, QPalette.Text, purpleBrush)
Palette[QPalette.Text]['purple'].setBrush(QPalette.Inactive, QPalette.Text, purpleBrush)
purpleBrush.setColor(Color['disabled'])
Palette[QPalette.Text]['purple'].setBrush(QPalette.Disabled, QPalette.Text, purpleBrush)

darkblueBrush = QBrush(Color['darkblue'])
darkblueBrush.setStyle(Qt.SolidPattern)
Palette[QPalette.Text]['darkblue'].setBrush(QPalette.Active, QPalette.Text, darkblueBrush)
Palette[QPalette.Text]['darkblue'].setBrush(QPalette.Inactive, QPalette.Text, darkblueBrush)
darkblueBrush.setColor(Color['disabled'])
Palette[QPalette.Text]['darkblue'].setBrush(QPalette.Disabled, QPalette.Text, darkblueBrush)

class MyObject(QLabel):
    defaultColor = Color['white']
    hoverColor = QColor(227, 240, 255)
    pressColor = QColor(213, 224, 240)

    isEnabledChanged = pyqtSignal()
    changeSignal = pyqtSignal()
    enterSignal = pyqtSignal()
    leaveSignal = pyqtSignal()
    pressSignal = pyqtSignal()
    showSignal = pyqtSignal()
    hideSignal = pyqtSignal()
    clicked = pyqtSignal()
    linkedObject = None
    Coloring = QPalette.Window

    def setColor(self, col):
        palette = self.palette()
        palette.setBrush(QPalette.Active, self.Coloring, QBrush(col))
        palette.setBrush(QPalette.Inactive, self.Coloring, QBrush(self.defaultColor))
        self.setPalette(palette)
        self.nowColor = col
    color = pyqtProperty(QColor, fset=setColor)

    def link(self, linkedObject):
        self.linkedObject = linkedObject

    def __init__(self, *arg, **kargs):
        super(MyObject, self).__init__(*arg, **kargs)
        self.Anime = {
            "load": QPropertyAnimation(self, b"color"),
            "enter": QPropertyAnimation(self, b"color"),
            "press": QPropertyAnimation(self, b"color"),
            "leave": QPropertyAnimation(self, b"color")
        }
        self.enterSignal.connect(self.EnterAnime)
        self.leaveSignal.connect(self.LeaveAnime)
        self.pressSignal.connect(self.PressAnime)

    def setEnabled(self, status: bool):
        super(MyObject, self).setEnabled(status)
        self.isEnabledChanged.emit()
        if self.linkedObject and self.linkedObject.isEnabled() != status:
            self.linkedObject.setEnabled(status)
        if not status: self.leaveSignal.emit()

    def enterEvent(self, e):
        self.enterSignal.emit()
        self.linkedObject and self.linkedObject.enterSignal.emit()

    def leaveEvent(self, e):
        self.leaveSignal.emit()
        self.linkedObject and self.linkedObject.leaveSignal.emit()

    def mouseReleaseEvent(self, e):
        if 0 <= e.x() <= self.width() and 0 <= e.y() <= self.height():
            self.clicked.emit()
            self.linkedObject and self.linkedObject.clicked.emit()
            self.enterEvent(e)

    def mousePressEvent(self, e):
        self.pressSignal.emit()
        self.linkedObject and self.linkedObject.pressSignal.emit()

    def showEvent(self, e):
        self.showSignal.emit()
        self.setVisible(True)
        self.linkedObject and self.linkedObject.setVisible(self.isVisible())

    def hideEvent(self, e):
        self.hideSignal.emit()

    def LoadAnime(self):
        if not self.isEnabled(): return
        self.setAutoFillBackground(True)
        self.Anime['load'].setStartValue(self.palette().color(self.Coloring))
        for x in self.Anime: self.Anime[x].stop()
        self.Anime['load'].start()

    def EnterAnime(self):
        if not self.isEnabled(): return
        self.setAutoFillBackground(True)
        self.Anime['enter'].setStartValue(self.nowColor)
        for x in self.Anime: self.Anime[x].stop()
        self.Anime['enter'].start()

    def PressAnime(self):
        if not self.isEnabled(): return
        self.setAutoFillBackground(True)
        self.Anime['press'].setStartValue(self.nowColor)
        for x in self.Anime: self.Anime[x].stop()
        self.Anime['press'].start()

    def LeaveAnime(self):
        # if not self.isEnabled(): return
        self.setAutoFillBackground(True)
        self.Anime['leave'].setStartValue(self.nowColor)
        for x in self.Anime: self.Anime[x].stop()
        self.Anime['leave'].start()

class _NewPushButtonBorder(MyObject):
    def __init__(self, *args, defaultColor: QColor, hoverColor: QColor, pressColor: QColor, r: float, d: float, actualParent = None, **kargs):
        super(_NewPushButtonBorder, self).__init__(*args, **kargs)
        self.Coloring = QPalette.Base
        self.defaultColor = defaultColor
        self.hoverColor = hoverColor
        self.pressColor = pressColor
        self.link(actualParent)
        self.r = r # 圆角半径
        self.d = d # 边框宽度
        self.Anime['load'].setDuration(1)
        self.Anime['load'].setEndValue(self.defaultColor)
        self.Anime['load'].setEasingCurve(QEasingCurve.OutCubic)
        self.Anime['enter'].setDuration(400)
        self.Anime['enter'].setEndValue(self.hoverColor)
        self.Anime['enter'].setEasingCurve(QEasingCurve.OutCubic)
        self.Anime['press'].setDuration(200)
        self.Anime['press'].setEndValue(self.pressColor)
        self.Anime['press'].setEasingCurve(QEasingCurve.OutCubic)
        self.Anime['leave'].setDuration(400)
        self.Anime['leave'].setEndValue(self.defaultColor)
        self.Anime['leave'].setEasingCurve(QEasingCurve.OutCubic)
        self.showSignal.connect(self.GetBorderPath)
        self.LoadAnime()

    def BorderColor(color: QColor):
        r = color.red() // 2
        g = color.green() // 2
        b = color.blue() // 2
        if b >= g and b >= r: b = color.blue() // 1.6
        elif r >= g and r >= b: r = color.red() // 1.6
        elif g >= b and g >= r: g = color.green() // 1.6
        return QColor(r, g, b)

    def paintEvent(self, e):
        self.nowColor = self.palette().color(QPalette.Base)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setPen(QPen(_NewPushButtonBorder.BorderColor(self.nowColor), self.d))
        painter.setBrush(self.nowColor)
        painter.drawPath(self.borderPath)
        painter.setPen(QPen(QColor(0, 0, 0)))

    def GetBorderPath(self):
        r = self.r
        d = self.d
        x = y = r + d / 2
        path = QPainterPath()
        path.moveTo(y, x - r)
        path.arcTo(y - r, x - r, 2 * r, 2 * r, 90, 90)
        x = x + self.height() - 2 * r - d
        path.lineTo(y - r, x)
        path.arcTo(y - r, x - r, 2 * r, 2 * r, 180, 90)
        y = y + self.width() - 2 * r - d
        path.lineTo(y, x + r)
        path.arcTo(y - r, x - r, 2 * r, 2 * r, 270, 90)
        x = x - self.height() + 2 * r + d
        path.lineTo(y + r, x)
        path.arcTo(y - r, x - r, 2 * r, 2 * r, 0, 90)
        y = y - self.width() + 2 * r + d
        path.lineTo(y, x - r)
        self.borderPath = path

class _NewPushButton(MyObject):
    showed = False
    def __init__(self, *args, defaultColor: QColor = MyObject.defaultColor, hoverColor: QColor = MyObject.hoverColor, pressColor: QColor = MyObject.pressColor, r = None, d = None, **kargs):
        super(_NewPushButton, self).__init__(*args, **kargs)
        self.r = r
        self.d = d
        self.defaultColor = defaultColor
        self.hoverColor = hoverColor
        self.pressColor = pressColor
        self.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        # self.setFrameShadow(QFrame.Raised)
        # self.setFrameShape(QFrame.NoFrame)
        self.Anime['load'].setDuration(400)
        self.Anime['load'].setEndValue(self.defaultColor)
        self.Anime['load'].setEasingCurve(QEasingCurve.OutCubic)
        self.Anime['press'].setDuration(200)
        self.Anime['press'].setEndValue(self.pressColor)
        self.Anime['press'].setEasingCurve(QEasingCurve.OutCubic)
        self.Anime['enter'].setDuration(400)
        self.Anime['enter'].setEndValue(self.hoverColor)
        self.Anime['enter'].setEasingCurve(QEasingCurve.OutCubic)
        self.Anime['leave'].setDuration(400)
        self.Anime['leave'].setEndValue(self.defaultColor)
        self.Anime['leave'].setEasingCurve(QEasingCurve.OutCubic)
        self.showSignal.connect(self.LoadAnime)
        self.hideSignal.connect(self.HideAnime)

    def HideAnime(self):
        if not self.showed: return
        self.linkedObject.hide()
        self.leaveSignal.emit()
        self.linkedObject and self.linkedObject.leaveSignal.emit()

    def LoadAnime(self):
        if not self.isEnabled(): return
        if self.showed:
            self.linkedObject.show()
            return
        self.showed = True
        # print(self.objectName(), "show")

        if not self.r: self.r = self.height() / 2 - 1
        if not self.d: self.d = 1.5
        self.link(_NewPushButtonBorder(r = self.r, d = self.d, defaultColor = self.defaultColor, hoverColor = self.hoverColor, pressColor = self.pressColor, parent = self.parent(), actualParent = self))
        self.linkedObject.setGeometry(self.x(), self.y(), self.width(), self.height())
        self.linkedObject.show()
        self.setGeometry(self.x() + self.r, self.y() + self.d * 2, self.width() - self.r * 2, self.height() - self.d * 4)
        self.raise_()
        super(_NewPushButton, self).LoadAnime()

class _NewProgressBar(QProgressBar):
    def setValue(self, value):
        QPropertyAnimation(self, b"value")
        for x in self.Anime: self.Anime[x].stop()
        self.Anime['progress'].setStartValue(self.value())
        self.Anime['progress'].setEndValue(value)
        if self.value() != value:
            self.Anime['progress'].start()

    def hide(self):
        super(_NewProgressBar, self).hide()
        for x in self.Anime: self.Anime[x].stop()
        super(_NewProgressBar, self).setValue(0)
        self.Anime['progress'].setDuration(1500)

    def __init__(self, *args, **kargs):
        super(_NewProgressBar, self).__init__(*args, **kargs)
        self.Anime = {
            "progress": QPropertyAnimation(self, b"value")
        }
        self.Anime['progress'].setDuration(1500)
        self.Anime['progress'].setEasingCurve(QEasingCurve.OutQuart)

class _NewListWidget(QListWidget):
    def addItem(self, item):
        item.setBackground(Color[['white', 'lightgray'][self.count() % 2]])
        super(_NewListWidget, self).addItem(item)
    def __init__(self, *args, **kargs):
        super(_NewListWidget, self).__init__(*args, **kargs)

if sys.platform == 'win32':
    NewPushButton = _NewPushButton
elif sys.platform == 'darwin':
    NewPushButton = QPushButton
else:
    NewPushButton = _NewPushButton
NewProgressBar = _NewProgressBar
NewListWidget = _NewListWidget

def ErrorDisplay(error, _ErrorTranslate, knownErrorInfo: str = "错误", unknownErrorInfo: str = "未知错误"):
    errorTranslate = _ErrorTranslate(error)
    if errorTranslate:
        QMessageBox.critical(None, knownErrorInfo, errorTranslate, QMessageBox.Ok)
    else:
        QMessageBox.critical(None, unknownErrorInfo, str(error), QMessageBox.Ok)

def AdjustWindowSize(window):
    screen = QDesktopWidget().screenGeometry()
    from math import sqrt
    BASE = sqrt((screen.width() * screen.height()) / (1920 * 1080))
    stack = window.children()
    while len(stack):
        x = stack.pop()
        stack.extend(x.children())
        try:
            x.setGeometry(x.x() * BASE, x.y() * BASE, x.width() * BASE, x.height() * BASE)
        except:
            pass
    window.setFixedSize(window.width() * BASE, window.height() * BASE)
    window.setWindowFlags(window.windowFlags() & ~Qt.WindowMaximizeButtonHint)
    size = window.geometry()
    window.move((screen.width() - size.width()) / 2,
              (screen.height() - size.height()) / 2)

