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

class _NewPushButton(QLabel):
    clicked = pyqtSignal()
    nowColor = QColor(241, 242, 243)
    def setColor(self, col):
        palette = self.palette()
        palette.setBrush(QPalette.Active, QPalette.Background, QBrush(col))
        self.setPalette(palette)
        self.nowColor = col
    color = pyqtProperty(QColor, fset=setColor)

    def __init__(self, parent):
        super(_NewPushButton, self).__init__(parent)
        self.setStyleSheet("_NewPushButton { border: 1px solid #717273; border-radius: 5px } _NewPushButton:hover { border: 1px solid blue } NewPushButton:disabled { background-color: #f1f2f3 }")
        self.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

    def enterEvent(self, e):
        # print("enterEvent")
        if not self.isEnabled(): return
        self.setAutoFillBackground(True)
        self.enterAnime = QPropertyAnimation(self, b"color")
        self.enterAnime.setDuration(400)
        self.enterAnime.setStartValue(self.nowColor)
        self.enterAnime.setEndValue(QColor(227, 240, 255))
        self.enterAnime.setEasingCurve(QEasingCurve.OutCubic)
        self.enterAnime.start()

    def leaveEvent(self, e):
        # print("leaveEvent")
        if not self.isEnabled(): return
        self.setAutoFillBackground(True)
        self.leaveAnime = QPropertyAnimation(self, b"color")
        self.leaveAnime.setDuration(400)
        self.leaveAnime.setStartValue(self.nowColor)
        self.leaveAnime.setEndValue(QColor(241, 242, 243))
        self.leaveAnime.setEasingCurve(QEasingCurve.OutCubic)
        self.leaveAnime.start()

    def mouseReleaseEvent(self, e):
        # print("mouseReleaseEvent")
        if 0 <= e.x() <= self.width() and 0 <= e.y() <= self.height():
            self.clicked.emit()
            self.enterEvent(e)

    def mousePressEvent(self, e):
        self.setAutoFillBackground(True)
        self.pressedAnime = QPropertyAnimation(self, b"color")
        self.pressedAnime.setDuration(400)
        self.pressedAnime.setStartValue(self.nowColor)
        self.pressedAnime.setEndValue(QColor(207, 220, 235))
        self.pressedAnime.setEasingCurve(QEasingCurve.OutCubic)
        self.pressedAnime.start()

import sys
if sys.platform == 'win32':
    Font['main'].setFamily("Microsoft YaHei")
    Font['main'].setPointSize(10)
    Font['status'].setFamily("KaiTi")
    Font['status'].setPointSize(10)
    Style['progressBar'] = "QProgressBar { border: 1px solid grey; border-radius: 2px; text-align: center; background-color: #FFFFFF;}QProgressBar::chunk { background-color: #30A132; width: 10px;}"
    NewPushButton = _NewPushButton
elif sys.platform == 'darwin':
    Font['main'].setFamily(".AppleSystemUIFont")
    Font['main'].setPointSize(13)
    Font['status'].setFamily(".AppleSystemUIFont")
    Font['status'].setPointSize(13)
    NewPushButton = QPushButton
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
