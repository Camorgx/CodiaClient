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
    ret = _acquire_verification(ResetUi.alineEdit_Account.text())[1]
    if not ret:
        QMessageBox.critical(None, '错误', '验证码获取失败,请重新获取。', QMessageBox.Ok)
    elif ret['status'] == 'SUCCESS':
        QMessageBox.information(None,'成功','验证码获取成功',QMessageBox.Ok)
    else:
        QMessageBox.critical(None, '错误', '验证码获取失败,请重新获取。', QMessageBox.Ok)
#信息获取完成，开始重置密码
def Reset():
    if not ResetUi.lineEdit_CheckNum.text():
        QMessageBox.information(None, '消息', '请输入验证码。', QMessageBox.Ok)
        return
    if not ResetUi.lineEdit_NewPassword.text():
        QMessageBox.information(None, '消息', '请输入新密码。', QMessageBox.Ok)
        return
    if (not ResetUi.lineEdit_Check_NewPassword.text()) or (ResetUi.lineEdit_NewPassword.text() != ResetUi.lineEdit_Check_NewPassword.text()):
        QMessageBox.information(None, '消息', '两次输入的密码不相同,请重新输入。', QMessageBox.Ok)
        return
    try:
        change_password(ResetUi.lineEdit_CheckNum.text(),ResetUi.lineEdit_NewPassword.text(),ResetUi.lineEdit_Check_NewPassword.text())
    except Exception as e:
        if 'invalid credential' in str(e):
            QMessageBox.critical(None, '错误', '验证码不正确。', QMessageBox.Ok)
            return
        if 'auth not found' in str(e):
            QMessageBox.critical(None, '错误', '该账户未注册。', QMessageBox.Ok)
        if 'Invalid password' in str(e):
            QMessageBox.critical(None, '错误', '新密码格式不正确。', QMessageBox.Ok)
    else:
        QMessageBox.information(None, '成功', '密码重置成功', QMessageBox.Ok)
#初始化重置密码窗体
def ResetWindowInit():
    ResetUi.pushButtonGetCheck.clicked.connect(GetCheck)
    ResetUi.pushButton_OK.clicked.connect(Reset)
    ResetUi.lineEdit_NewPassword.setEchoMode(QLineEdit.Password)
    ResetUi.lineEdit_Check_NewPassword.setEchoMode(QLineEdit.Password)
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