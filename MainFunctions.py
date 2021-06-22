import datetime

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout
from PyQt5.QtWidgets import QListWidgetItem, QWidget, QListWidget
from PyQt5 import QtGui

import functionWindow
from codiaclient.network import *


def functionWindow_init(ui: functionWindow.Ui_functionWindow):
    packlist = get_pack(lastcnt = 12)
    ui.frame_questionlist.hide()
    ui.frame_packlist.show()
    for dic in packlist:
        add_item_to_pack_list(ui.listWidget_packs, dic)


def getpackwidget(data: dict):
    widget = QWidget()
    layout_main = QHBoxLayout()
    layout_right = QVBoxLayout()
    layout_right_up = QHBoxLayout()
    layout_right_down = QHBoxLayout()
    total = data['codingExercises']['totalCount']
    hasdone = data['codingExercises']['viewerPassedCount']
    if total == hasdone:
        label_finish = QLabel('已完成')
        greenPalette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(80, 160, 30))
        brush.setStyle(Qt.SolidPattern)
        greenPalette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Text, brush)
        label_finish.setPalette(greenPalette)
    else:
        label_finish = QLabel('未完成')
        redPalette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(160, 0, 30))
        brush.setStyle(Qt.SolidPattern)
        redPalette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Text, brush)
        label_finish.setPalette(redPalette)
    layout_main.addWidget(label_finish)
    layout_main.setStretchFactor(label_finish, 1)
    label_name = QLabel(data['name'])
    label_start = QLabel('开始时间')
    label_end = QLabel('截止时间')
    label_hasdone_total = QLabel('已完成/总计： {}/{}'.format(hasdone, total))
    layout_right_up.addWidget(label_name)
    layout_right_up.addWidget(label_start)
    layout_right_up.addWidget(label_end)
    layout_right_up.setStretchFactor(label_name, 4)
    layout_right_up.setStretchFactor(label_start, 4)
    layout_right_up.setStretchFactor(label_end, 4)
    layout_right_down.addWidget(label_hasdone_total)
    layout_right_down.setStretchFactor(label_hasdone_total, 4)
    if data['due']:
        end = (datetime.datetime.strptime(data['due'].replace('T', " ")[:-5], "%Y-%m-%d %H:%M:%S")
                + datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
    else:
        end = '无限制'
    if data['createdAt']:
        start = (datetime.datetime.strptime(data['createdAt'].replace('T', " ")[:-5], "%Y-%m-%d %H:%M:%S")
                 + datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
    else:
        start = '无限制'
    label_start_time = QLabel(start)
    label_end_time = QLabel(end)
    layout_right_down.addWidget(label_start_time)
    layout_right_down.addWidget(label_end_time)
    layout_right_down.setStretchFactor(label_start_time, 4)
    layout_right_down.setStretchFactor(label_end_time, 4)
    layout_right.addLayout(layout_right_up)
    layout_right.addLayout(layout_right_down)
    layout_main.addLayout(layout_right)
    layout_main.setStretchFactor(label_finish, 1)
    layout_main.setStretchFactor(layout_right, 12)
    layout_right.setStretchFactor(layout_right_up, 12)
    layout_right.setStretchFactor(layout_right_down, 12)
    widget.setLayout(layout_main)
    return widget


def add_item_to_pack_list(packlist: QListWidget, data: dict):
    item = QListWidgetItem()
    item.setSizeHint(QSize(651, 68))
    widget = getpackwidget(data)
    packlist.addItem(item)
    packlist.setItemWidget(item, widget)
    # print(show_pack(data['id']))