import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWidgets import QMessageBox, QLineEdit
import loginWindow
import ResetPassword
import registerWindow
from codiaclient.network import *
from codiaclient.network import _acquire_verification
from codiaclient.report import Error
from codiaclient import client_login
from codiaclient import report_var

#开始进行登录操作
def BeginLogin():
    loginusername = LoginUi.lineEdit.text()
    loginpassword = LoginUi.lineEdit_2.text()
    if not LoginUi.lineEdit.text():
        QMessageBox.information(None, '登录失败', '请输入邮箱或手机号。', QMessageBox.Ok)
        return False
    if not LoginUi.lineEdit_2.text():
        QMessageBox.information(None, '登录失败', '请输入密码。', QMessageBox.Ok)
        return False
    else:
        try:
            client_login(username=loginusername, password=loginpassword)
        except Error as e:
            if 'Connect timeout' in str(e):
                QMessageBox.information(None, '登录失败', '网络连接超时。', QMessageBox.Ok)
            elif 'Connection error' in str(e):
                QMessageBox.information(None, '登录失败', '网络连接错误。', QMessageBox.Ok)
            elif 'invalid username or password' in str(e):
                QMessageBox.information(None, '登录失败', '用户名不存在或密码错误。', QMessageBox.Ok)
            elif 'Login failed' in str(e):
                QMessageBox.information(None, '登录失败', '登录失败，请重试。', QMessageBox.Ok)
            else:
                QMessageBox.information(None, '未知错误', str(e), QMessageBox.Ok)
                raise
            return False
        else:
            loginusernickname = logined()[1]
            QMessageBox.information(None, '登录成功', '已登录用户: ' + loginusernickname, QMessageBox.Ok)
            return True

#初始化重置密码窗口并打开
def BeginReset():
    ResetUi.setupUi(ResetWindow)
    if ResetWindowInit():
        ResetWindow.show()

#获取重置密码的验证码
def GetCheck():
    if not ResetUi.alineEdit_Account.text():
        QMessageBox.information(None, '消息', '请输入邮箱或手机号。', QMessageBox.Ok)
    try:
        ret = _acquire_verification(ResetUi.alineEdit_Account.text())[1]
    except Error as e:
        if 'Connect timeout' in str(e):
            QMessageBox.critical(None, '错误', '网络连接超时。', QMessageBox.Ok)
        elif 'Connection error' in str(e):
            QMessageBox.critical(None, '错误', '网络连接错误。', QMessageBox.Ok)
    if not ret:
        QMessageBox.critical(None, '错误', '验证码获取失败,请重新获取。', QMessageBox.Ok)
    elif ret['status'] == 'SUCCESS':
        QMessageBox.information(None, '成功', '验证码获取成功', QMessageBox.Ok)
    else:
        QMessageBox.critical(None, '错误', '验证码获取失败,请重新获取。', QMessageBox.Ok)

# 信息获取完成，开始重置密码
def Reset():
    if not ResetUi.alineEdit_Account.text():
        QMessageBox.information(None, '消息', '请输入邮箱或手机号。', QMessageBox.Ok)
        return
    if not ResetUi.lineEdit_CheckNum.text():
        QMessageBox.information(None, '消息', '请输入验证码。', QMessageBox.Ok)
        return
    if not ResetUi.lineEdit_NewPassword.text():
        QMessageBox.information(None, '消息', '请输入新密码。', QMessageBox.Ok)
        return
    if ((not ResetUi.lineEdit_Check_NewPassword.text()) or (not ResetUi.lineEdit_NewPassword.text())
            or (ResetUi.lineEdit_NewPassword.text() != ResetUi.lineEdit_Check_NewPassword.text())):
        QMessageBox.information(None, '消息', '两次输入的密码不相同,请重新输入。', QMessageBox.Ok)
        return
    try:
        change_password(identifier=ResetUi.alineEdit_Account.text(), vercode=ResetUi.lineEdit_CheckNum.text(),
                        passwd=ResetUi.lineEdit_NewPassword.text(), passwordconfirm=ResetUi.lineEdit_Check_NewPassword.text())
    except Exception as e:
        if 'Connect timeout' in str(e):
            QMessageBox.critical(None, '错误', '网络连接超时。', QMessageBox.Ok)
        elif 'Connection error' in str(e):
            QMessageBox.critical(None, '错误', '网络连接错误。', QMessageBox.Ok)
        if 'invalid credential' in str(e):
            QMessageBox.critical(None, '错误', '验证码不正确。', QMessageBox.Ok)
            return
        if 'auth not found' in str(e):
            QMessageBox.critical(None, '错误', '该账户未注册。', QMessageBox.Ok)
            return
        if 'Invalid password' in str(e):
            QMessageBox.critical(None, '错误', '新密码格式不正确。', QMessageBox.Ok)
            return
        else:
            QMessageBox.critical(None, '未知错误', str(e), QMessageBox.Ok)
            raise
    else:
        QMessageBox.information(None, '成功', '密码重置成功。', QMessageBox.Ok)
        ResetWindow.close()


# 初始化重置密码窗体
def ResetWindowInit():
    ResetUi.pushButtonGetCheck.clicked.connect(GetCheck)
    ResetUi.pushButton_OK.clicked.connect(Reset)
    ResetUi.lineEdit_NewPassword.setEchoMode(QLineEdit.Password)
    ResetUi.lineEdit_Check_NewPassword.setEchoMode(QLineEdit.Password)
    if LoginUi.lineEdit.text():
        ResetUi.alineEdit_Account.setText(LoginUi.lineEdit.text())
    return True

#初始化任务，为登陆窗口信号绑定槽函数
def BeginTask():
    LoginUi.pushButtonLogin.clicked.connect(BeginLogin)
    LoginUi.lineEdit_2.setEchoMode(QLineEdit.Password)
    LoginUi.pushButtonReset.clicked.connect(BeginReset)
    report_var['allow_error_deg'] = 0
    LoginUi.pushButtonRegister.clicked.connect(BeginRegister)

def BeginRegister():
    RegisterUi.setupUi(RegisterWindow)
    if LoginUi.lineEdit.text():
        RegisterUi.lineEdit_userphone .setText(LoginUi.lineEdit.text())
    RegisterUi.pushButton.clicked.connect(Register)
    RegisterWindow.show()

def Register():
    if not RegisterUi.lineEdit_userphone.text():
        QMessageBox.information(None, '消息', '请输入邮箱。', QMessageBox.Ok)
        return
    if not RegisterUi.lineEdit_username.text():
        QMessageBox.information(None, '消息', '请输入用户名。', QMessageBox.Ok)
        return
    if not RegisterUi.lineEdit_password.text():
        QMessageBox.information(None, '消息', '请输入密码。', QMessageBox.Ok)
        return
    if ((not RegisterUi.lineEdit_checkpassword.text()) or (not RegisterUi.lineEdit_password.text())
            or (RegisterUi.lineEdit_password.text() != RegisterUi.lineEdit_checkpassword.text())):
        QMessageBox.information(None, '消息', '两次输入的密码不相同,请重新输入。', QMessageBox.Ok)
        return
    try:
        ret = register(username=RegisterUi.lineEdit_username.text(),passwd=RegisterUi.lineEdit_password.text(),
                 email=RegisterUi.lineEdit_userphone.text())
    except Error as e:
        if 'Connect timeout' in str(e):
            QMessageBox.critical(None, '注册失败', '网络连接超时。', QMessageBox.Ok)
        elif 'Connection error' in str(e):
            QMessageBox.critical(None, '注册失败', '网络连接错误。', QMessageBox.Ok)
        elif 'email has been used' in str(e):
            QMessageBox.critical(None, '注册失败', '该邮箱已被使用。', QMessageBox.Ok)
        elif 'invalid password' in str(e):
            QMessageBox.critical(None, '注册失败', '密码不合法。', QMessageBox.Ok)
        elif 'user exists' in str(e):
            QMessageBox.critical(None, '注册失败', '用户名已存在。', QMessageBox.Ok)
        else:
            QMessageBox.critical(None, '未知错误', str(e), QMessageBox.Ok)
    else:
        if not ret:
            QMessageBox.critical(None, '注册失败', '注册失败，请重试。', QMessageBox.Ok)
        else:
            QMessageBox.information(None, '注册成功', '成功注册了用户' + ret['login'], QMessageBox.Ok)
            RegisterWindow.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    LoginWindow = QMainWindow()
    LoginUi = loginWindow.Ui_loginWindow()
    LoginUi.setupUi(LoginWindow)
    ResetWindow = QMainWindow()
    ResetUi = ResetPassword.Ui_ResetPassword()
    RegisterWindow = QMainWindow()
    RegisterUi = registerWindow.Ui_registerWindow()
    BeginTask()
    LoginWindow.show()
    sys.exit(app.exec_())
