from datetime import datetime, timedelta
from re import search

from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout
from PyQt5.QtWidgets import QListWidgetItem, QWidget, QListWidget
from PyQt5.QtWidgets import QMessageBox

import functionWindow
from codiaclientgui.utils import Font, Palette
from codiaclient.network import get_pack, show_pack

variables = {
    "page_number": 0,
    "last_pack_pid": None,
    "first_pack_pid": None,
    "has_next": True,
}


def functionWindow_init(UI: functionWindow.Ui_functionWindow, nickname = "UNDEFINED", verified=True):
    if verified:
        status_bar_label = QLabel(f"当前用户: {nickname}")
    else:
        status_bar_label = QLabel(f"当前用户: {nickname}(未验证)")
        QMessageBox.information(None, "消息", "当前账号功能受限，请尽快完成联系方式验证。", QMessageBox.Ok)
    status_bar_label.setFont(Font["status"])
    UI.statusbar.addWidget(status_bar_label)
    UI.pushButton_next.clicked.connect(lambda: nextPage(UI))
    UI.pushButton_last.clicked.connect(lambda: previousPage(UI))
    nextPage(UI)
    UI.exerciseFrame.hide()
    UI.packFrame.show()


def nextPage(UI: functionWindow.Ui_functionWindow):
    UI.pushButton_next.setEnabled(False)
    UI.pushButton_last.setEnabled(False)
    try: pack_list = get_pack(before = variables['last_pack_pid'])
    except codiaError as e:
        errorTranslate = error_translate(e)
        if errorTranslate:
            QMessageBox.critical(None, "获取失败", errorTranslate, QMessageBox.Ok)
        else:
            QMessageBox.critical(None, "未知错误", str(e), QMessageBox.Ok)
            raise
        return False
    variables['page_number'] += 1
    variables['has_next'] = pack_list['pageInfo']['hasPreviousPage']
    pack_list = pack_list['nodes']
    variables['last_pack_pid'] = pack_list[0]['id']
    variables['first_pack_pid'] = pack_list[-1]['id']
    UI.pushButton_next.setEnabled(bool(variables['has_next']))
    UI.pushButton_last.setEnabled(variables['page_number'] != 1)
    UI.label_page.setText('第 {} 页'.format(variables['page_number']))
    for i in range(0, UI.listWidget_packs.count()): UI.listWidget_packs.takeItem(0)
    for dic in pack_list: add_item_to_pack_list(UI.listWidget_packs, dic)


def previousPage(UI: functionWindow.Ui_functionWindow):
    UI.pushButton_next.setEnabled(False)
    UI.pushButton_last.setEnabled(False)
    try: pack_list = get_pack(after = variables['first_pack_pid'])
    except codiaError as e:
        errorTranslate = error_translate(e)
        if errorTranslate:
            QMessageBox.critical(None, "获取失败", errorTranslate, QMessageBox.Ok)
        else:
            QMessageBox.critical(None, "未知错误", str(e), QMessageBox.Ok)
            raise
        return False
    variables['page_number'] -= 1
    variables['has_next'] = pack_list['pageInfo']['hasPreviousPage']
    pack_list = pack_list['nodes']
    variables['last_pack_pid'] = pack_list[0]['id']
    variables['first_pack_pid'] = pack_list[-1]['id']
    UI.pushButton_next.setEnabled(bool(variables['has_next']))
    UI.pushButton_last.setEnabled(variables['page_number'] != 1)
    UI.label_page.setText('第 {} 页'.format(variables['page_number']))
    for i in range(0, UI.listWidget_packs.count()): UI.listWidget_packs.takeItem(0)
    for dic in pack_list: add_item_to_pack_list(UI.listWidget_packs, dic)


def get_pack_widget(data: dict):
    widget = QWidget()
    layout_main = QHBoxLayout()
    layout_right = QVBoxLayout()
    layout_right_up = QHBoxLayout()
    layout_right_down = QHBoxLayout()
    if data["codingExercises"]:
        total = data["codingExercises"]["totalCount"]
        has_done = data["codingExercises"]["viewerPassedCount"]
        if total == has_done:
            label_finish = QLabel("已完成")
            label_finish.setPalette(Palette["green"])
        else:
            label_finish = QLabel("未完成")
            label_finish.setPalette(Palette["red"])
        label_has_done_total = QLabel(f"已完成/总计: {has_done}/{total}")
        if data["due"]:
            end = (datetime.strptime(search(r"^[^.]*", data["due"].replace("T", " ")).group(), "%Y-%m-%d %H:%M:%S")
                   + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
        else:
            end = "无限制"

        if data["createdAt"]:
            start = (datetime.strptime(search(r"^[^.]*", data["createdAt"].replace("T", " ")).group(),
                                       "%Y-%m-%d %H:%M:%S")
                     + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
        else:
            start = "无限制"
    else:
        end = ""
        start = ""
        label_finish = QLabel("无权限")
        label_finish.setPalette(Palette["gray"])
        label_has_done_total = QLabel("")
        widget.setEnabled(False)

    label_name = QLabel(data["name"])
    label_start = QLabel("开始时间")
    label_end = QLabel("截止时间")
    label_start_time = QLabel(start)
    label_end_time = QLabel(end)

    layout_right_up.addWidget(label_name)
    layout_right_up.addWidget(label_start)
    layout_right_up.addWidget(label_end)
    layout_right_up.setStretchFactor(label_name, 4)
    layout_right_up.setStretchFactor(label_start, 4)
    layout_right_up.setStretchFactor(label_end, 4)

    layout_right_down.addWidget(label_has_done_total)
    layout_right_down.addWidget(label_start_time)
    layout_right_down.addWidget(label_end_time)
    layout_right_down.setStretchFactor(label_has_done_total, 4)
    layout_right_down.setStretchFactor(label_start_time, 4)
    layout_right_down.setStretchFactor(label_end_time, 4)

    layout_right.addLayout(layout_right_up)
    layout_right.addLayout(layout_right_down)
    layout_right.setStretchFactor(layout_right_up, 12)
    layout_right.setStretchFactor(layout_right_down, 12)

    layout_main.addWidget(label_finish)
    layout_main.addLayout(layout_right)
    layout_main.setStretchFactor(label_finish, 1)
    layout_main.setStretchFactor(layout_right, 12)

    widget.setLayout(layout_main)
    return widget


def add_item_to_pack_list(pack_list: QListWidget, data: dict):
    item = QListWidgetItem()
    item.setSizeHint(QSize(651, 68))
    widget = get_pack_widget(data)
    pack_list.addItem(item)
    pack_list.setItemWidget(item, widget)
