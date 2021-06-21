import datetime

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout
from PyQt5.QtWidgets import QListWidgetItem, QWidget, QListWidget

import functionWindow
from codiaclient.network import *


def functionWindow_init(ui: functionWindow.Ui_functionWindow):
    packlist = get_pack()
    ui.frame_questionlist.hide()
    ui.frame_packlist.show()
    for dic in packlist:
        print(dic)
        additemtopacklist(ui.listWidget_packs, dic)


def getpackwidget(data: dict):
    widget = QWidget()
    layout_main = QHBoxLayout()
    layout_right = QVBoxLayout()
    layout_right_down = QHBoxLayout()
    total = data['codingExercises']['totalCount']
    hasdone = data['codingExercises']['viewerPassedCount']
    if total == hasdone:
        layout_main.addWidget(QLabel('已完成'))
    else:
        layout_main.addWidget(QLabel('未完成'))
    layout_right.addWidget(QLabel(data['name']))
    label_hasdone_total = QLabel('已完成/总计\n' + str(hasdone) + '/' + str(total))
    label_hasdone_total.setAlignment(Qt.AlignRight)
    layout_right_down.addWidget(label_hasdone_total)
    if data['due']:
        time = (datetime.datetime.strptime(data['due'].replace('T', " ")[:-5], "%Y-%m-%d %H:%M:%S")
            + datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
    else:
        time = '无限制'
    layout_right_down.addWidget(QLabel(time))
    layout_right.addLayout(layout_right_down)
    layout_main.addLayout(layout_right)
    widget.setLayout(layout_main)
    return widget


def additemtopacklist(packlist: QListWidget, data: dict):
    item = QListWidgetItem()
    item.setSizeHint(QSize(651, 68))
    widget = getpackwidget(data)
    packlist.addItem(item)
    packlist.setItemWidget(item, widget)