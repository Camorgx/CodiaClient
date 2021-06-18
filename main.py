import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWidgets import QMessageBox,QLineEdit
import loginWindow
import ResetPassword
from codiaclient.network import *
from codiaclient.report import Error
from codiaclient import client_login
def BeginLogin():
    loginusername = LoginUi.lineEdit.text()
    loginpassword = LoginUi.lineEdit_2.text()
    if not LoginUi.lineEdit.text():
        QMessageBox.information(None, '登录失败', '请输入邮箱或手机号', QMessageBox.Ok)
        return False
    if not LoginUi.lineEdit_2.text():
        QMessageBox.information(None, '登录失败', '请输入密码', QMessageBox.Ok)
        return False
    else:
        try:
            client_login(loginusername, loginpassword)
        except Error as e:
            QMessageBox.information(None, '登录失败', str(e), QMessageBox.Ok)
            return False
        else:
            loginusernickname = logined()
            QMessageBox.information(None, '登录成功', '已登录用户: ' + loginusernickname, QMessageBox.Ok)
            return True
def BeginReset():
    ResetUi.setupUi(ResetWindow)
    if ResetWindowInit():
        ResetWindow.show()
def GetCheck():
    if not ResetUi.alineEdit_Account.text():
        QMessageBox.information(None, '消息', '请输入邮箱或手机号。', QMessageBox.Ok)
def Reset():
    pass
def ResetWindowInit():
    ResetUi.pushButtonGetCheck.clicked.connect(GetCheck)
    ResetUi.pushButton_OK.clicked.connect(Reset)
    if not LoginUi.lineEdit.text():
        QMessageBox.information(None, '消息', '请输入邮箱或手机号。', QMessageBox.Ok)
        return False
    ResetUi.alineEdit_Account.setText(LoginUi.lineEdit.text())
    return True
def BeginTask():
    LoginUi.pushButtonLogin.clicked.connect(BeginLogin)
    LoginUi.lineEdit_2.setEchoMode(QLineEdit.Password)
    LoginUi.pushButtonReset.clicked.connect(BeginReset)
if __name__ == '__main__':
    app = QApplication(sys.argv)
    LoginWindow = QMainWindow()
    LoginUi = loginWindow.Ui_loginWindow()
    LoginUi.setupUi(LoginWindow)
    ResetWindow = QMainWindow()
    ResetUi = ResetPassword.Ui_ResetPassword()
    BeginTask()
    LoginWindow.show()
    sys.exit(app.exec_())