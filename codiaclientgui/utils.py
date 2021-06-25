import sys
from PyQt5.QtCore import Qt, QPropertyAnimation, pyqtSignal, QRect, pyqtProperty, QObject, QEasingCurve
from PyQt5.QtGui import QFont, QPalette, QBrush, QColor, QPainterPath, QPainter
from PyQt5.QtWidgets import QApplication, QPushButton, QLabel, QFrame

Font = {
    'main': QFont(),
    'status': QFont(),
}

Palette = {
    "green": QPalette(),
    "red": QPalette(),
    "gray": QPalette(),
}

Style = {
    "progressBar": "",
}

import sys
if sys.platform == 'win32':
    Font['main'].setFamily("Microsoft YaHei")
    Font['main'].setPointSize(10)
    Font['status'].setFamily("KaiTi")
    Font['status'].setPointSize(10)
    Style['progressBar'] = "QProgressBar { border: 1px solid grey; border-radius: 2px; text-align: center; background-color: #FFFFFF;}QProgressBar::chunk { background-color: #30A132; width: 10px;}"
elif sys.platform == 'darwin':
    Font['main'].setFamily(".AppleSystemUIFont")
    Font['main'].setPointSize(13)
    Font['status'].setFamily(".AppleSystemUIFont")
    Font['status'].setPointSize(13)
else:
    Font['main'].setFamily("Microsoft YaHei")
    Font['main'].setPointSize(13)

greenBrush = QBrush(QColor(80, 160, 30))
greenBrush.setStyle(Qt.SolidPattern)
Palette['green'].setBrush(QPalette.Active, QPalette.Text, greenBrush)
greenBrush = QBrush(QColor(80, 160, 30))
greenBrush.setStyle(Qt.SolidPattern)
Palette['green'].setBrush(QPalette.Inactive, QPalette.Text, greenBrush)
greenBrush = QBrush(QColor(120, 120, 120))
greenBrush.setStyle(Qt.SolidPattern)
Palette['green'].setBrush(QPalette.Disabled, QPalette.Text, greenBrush)

redBrush = QBrush(QColor(160, 0, 30))
redBrush.setStyle(Qt.SolidPattern)
Palette['red'].setBrush(QPalette.Active, QPalette.Text, redBrush)
redBrush = QBrush(QColor(160, 0, 30))
redBrush.setStyle(Qt.SolidPattern)
Palette['red'].setBrush(QPalette.Inactive, QPalette.Text, redBrush)
redBrush = QBrush(QColor(120, 120, 120))
redBrush.setStyle(Qt.SolidPattern)
Palette['red'].setBrush(QPalette.Disabled, QPalette.Text, redBrush)

grayBrush = QBrush(QColor(150, 151, 152))
grayBrush.setStyle(Qt.SolidPattern)
Palette['gray'].setBrush(QPalette.Active, QPalette.Text, grayBrush)
grayBrush = QBrush(QColor(150, 151, 152))
grayBrush.setStyle(Qt.SolidPattern)
Palette['gray'].setBrush(QPalette.Inactive, QPalette.Text, grayBrush)
grayBrush = QBrush(QColor(120, 120, 120))
grayBrush.setStyle(Qt.SolidPattern)
Palette['gray'].setBrush(QPalette.Disabled, QPalette.Text, grayBrush)

class NewPushButton(QLabel):
    mouseHovered = pyqtSignal()
    mouseLeft = pyqtSignal()
    clicked = pyqtSignal()
    nowColor = QColor(241, 242, 243)
    def setColor(self, col):
        palette = self.palette()
        palette.setColor(QPalette.Background, col)
        self.setPalette(palette)
        self.nowColor = col
    color = pyqtProperty(QColor, fset=setColor)

    def __init__(self, parent):
        super(NewPushButton, self).__init__(parent)
        # self.setFrameShadow(QFrame.Raised)
        # self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("NewPushButton { border: 1px solid gray; border-radius: 5px } NewPushButton::hover { border: 1px solid blue }")
        self.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.mouseHovered.connect(self.hoveredAnimeStart)
        self.mouseLeft.connect(self.leftAnimeStart)

    def hoveredAnimeStart(self):
        if not self.isEnabled(): return
        self.setAutoFillBackground(True)
        self.hoveredAnime = QPropertyAnimation(self, b"color")
        self.hoveredAnime.setDuration(400)
        self.hoveredAnime.setStartValue(self.nowColor)
        self.hoveredAnime.setEndValue(QColor(227, 240, 255))
        self.hoveredAnime.setEasingCurve(QEasingCurve.OutCubic)
        self.hoveredAnime.start()

    def leftAnimeStart(self):
        if not self.isEnabled(): return
        self.setAutoFillBackground(True)
        self.leftAnime = QPropertyAnimation(self, b"color")
        self.leftAnime.setDuration(400)
        self.leftAnime.setStartValue(self.nowColor)
        self.leftAnime.setEndValue(QColor(241, 242, 243))
        self.leftAnime.setEasingCurve(QEasingCurve.OutCubic)
        self.leftAnime.start()

    def enterEvent(self, e):
        # print("enterEvent")
        self.mouseHovered.emit()

    def leaveEvent(self, e):
        # print("leaveEvent")
        self.mouseLeft.emit()

    def mouseReleaseEvent(self, e):
        # print("mouseReleaseEvent")
        if 0 <= e.x() <= self.width() and 0 <= e.y() <= self.height():
            self.clicked.emit()
        self.mouseHovered.emit()

    def mousePressEvent(self, e):
        self.setAutoFillBackground(True)
        self.pressedAnime = QPropertyAnimation(self, b"color")
        self.pressedAnime.setDuration(400)
        self.pressedAnime.setStartValue(self.nowColor)
        self.pressedAnime.setEndValue(QColor(207, 220, 235))
        self.pressedAnime.setEasingCurve(QEasingCurve.OutCubic)
        self.pressedAnime.start()
