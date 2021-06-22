import sys

from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWidgets import QMessageBox, QLineEdit

import MainFunctions
import loginWindow
import functionWindow

from codiaclient import report_var, net_var
from codiaclient.network import *
from codiaclient.network import _acquire_verification
from codiaclient.report import Error as codiaError, error_translate
from codiaclient.utils import cookie_decrypt, cookie_encrypt


# 开始进行登录操作
def BeginLogin():
    loginusername = LoginUi.lineEditLoginUsername.text()
    loginpassword = LoginUi.lineEditLoginPassword.text()
    if not LoginUi.lineEditLoginUsername.text():
        QMessageBox.critical(None, "登录失败", "请输入邮箱或手机号。", QMessageBox.Ok)
        return False
    if not LoginUi.lineEditLoginPassword.text():
        QMessageBox.critical(None, "登录失败", "请输入密码。", QMessageBox.Ok)
        return False
    else:
        try:
            client_login(username = loginusername, password = loginpassword)
        except codiaError as e:
            errorTranslate = error_translate(e)
            if errorTranslate:
                QMessageBox.critical(None, "登录失败", errorTranslate, QMessageBox.Ok)
            else:
                QMessageBox.critical(None, "未知错误", str(e), QMessageBox.Ok)
                raise
            return False
        else:
            from base64 import b64encode
            try:
                with open("config.sav", "wb") as configfile:
                    if LoginUi.checkBox.isChecked():
                        config = json.dumps({
                            "password_store_on": True,
                            "username": LoginUi.lineEditLoginUsername.text(),
                            "password": cookie_encrypt(LoginUi.lineEditLoginPassword.text(), "hdt20040127")
                        }).encode()
                        configfile.write(b64encode(config))
                    else:
                        config = json.dumps({
                            "password_store_on": False,
                            "username": LoginUi.lineEditLoginUsername.text(),
                            "password": None
                        }).encode()
                        configfile.write(b64encode(config))
            except Exception as e:
                QMessageBox.critical(None, "未知错误", str(e), QMessageBox.Ok)
            finally:
                BeginFunction()
                return True

# 打开做题界面
def BeginFunction():
    loginusernickname = logined()[1]
    verified = bool(net_var["me"]["verified"])
    FunctionUi.setupUi(FunctionWindow)
    MainFunctions.functionWindow_init(FunctionUi, loginusernickname, verified)

    from codiaclientgui.utils import Font
    FunctionWindow.setFont(Font["main"])

    LoginWindow.hide()
    FunctionWindow.show()

# 获取重置密码的验证码
def GetCheck():
    if not LoginUi.lineEditResetAccount.text():
        QMessageBox.information(None, "消息", "请输入邮箱或手机号。", QMessageBox.Ok)
    try:
        ret = _acquire_verification(LoginUi.lineEditResetAccount.text())[1]
    except codiaError as e:
        errorTranslate = error_translate(e)
        if errorTranslate:
            QMessageBox.critical(None, "错误", errorTranslate, QMessageBox.Ok)
        else:
            QMessageBox.critical(None, "未知错误", str(e), QMessageBox.Ok)
            raise
    else:
        if not ret:
            QMessageBox.critical(None, "错误", "验证码获取失败, 请重新获取。", QMessageBox.Ok)
        elif ret["status"] == "SUCCESS":
            QMessageBox.information(None, "成功", "验证码获取成功", QMessageBox.Ok)
        else:
            QMessageBox.critical(None, "错误", "验证码获取失败, 请重新获取。", QMessageBox.Ok)


# 打开注册界面
def ShowRegister():
    LoginUi.loginFrame.hide()
    LoginUi.registerFrame.show()
    if LoginUi.lineEditLoginUsername.text():
        LoginUi.lineEditRegisterUsername.setText(LoginUi.lineEditLoginUsername.text())


# 打开重置密码界面
def ShowReset():
    LoginUi.loginFrame.hide()
    LoginUi.resetFrame.show()
    if LoginUi.lineEditLoginUsername.text():
        LoginUi.lineEditResetAccount.setText(LoginUi.lineEditLoginUsername.text())


# 初始化任务，为登陆窗口信号绑定槽函数
def BeginTask():
    report_var["allow_error_deg"] = 1

    from codiaclientgui.utils import Font
    LoginWindow.setFont(Font["main"])

    LoginUi.lineEditLoginPassword.setEchoMode(QLineEdit.Password)
    LoginUi.pushButtonLogin.clicked.connect(BeginLogin)
    LoginUi.pushButtonLoginGoReset.clicked.connect(ShowReset)
    LoginUi.pushButtonLoginGoRegister.clicked.connect(ShowRegister)

    LoginUi.pushButtonRegister.clicked.connect(Register)
    LoginUi.pushButtonRegisterReturn.clicked.connect(ReturnHomeFromReg)
    LoginUi.lineEditRegisterPassword.setEchoMode(QLineEdit.Password)
    LoginUi.lineEditRegisterCheckPassword.setEchoMode(QLineEdit.Password)

    LoginUi.lineEditResetNewPassword.setEchoMode(QLineEdit.Password)
    LoginUi.lineEditResetCheckNewPassword.setEchoMode(QLineEdit.Password)
    LoginUi.pushButtonReset.clicked.connect(Reset)
    LoginUi.pushButtonResetGetCheck.clicked.connect(GetCheck)
    LoginUi.pushButtonResetReturn.clicked.connect(ReturnHomeFromReset)

    LoginUi.loginFrame.show()
    LoginUi.registerFrame.hide()
    LoginUi.resetFrame.hide()


# 注册函数
def Register():
    if not LoginUi.lineEditRegisterUserphone.text():
        QMessageBox.information(None, "消息", "请输入邮箱。", QMessageBox.Ok)
        return
    if not LoginUi.lineEditRegisterUsername.text():
        QMessageBox.information(None, "消息", "请输入用户名。", QMessageBox.Ok)
        return
    if not LoginUi.lineEditRegisterPassword.text():
        QMessageBox.information(None, "消息", "请输入密码。", QMessageBox.Ok)
        return
    if ((not LoginUi.lineEditRegisterCheckPassword.text()) or (not LoginUi.lineEditRegisterPassword.text())
            or (LoginUi.lineEditRegisterPassword.text() != LoginUi.lineEditRegisterCheckPassword.text())):
        QMessageBox.information(None, "消息", "两次输入的密码不相同, 请重新输入。", QMessageBox.Ok)
        return
    try:
        ret = register(username = LoginUi.lineEditRegisterUsername.text(), passwd = LoginUi.lineEditRegisterPassword.text(),
                       email = LoginUi.lineEditRegisterUserphone.text())
    except codiaError as e:
        errorTranslate = error_translate(e)
        if errorTranslate:
            QMessageBox.critical(None, "注册失败", errorTranslate, QMessageBox.Ok)
        else:
            QMessageBox.critical(None, "未知错误", str(e), QMessageBox.Ok)
            raise
    else:
        if not ret:
            QMessageBox.critical(None, "注册失败", "注册失败，请重试。", QMessageBox.Ok)
        else:
            QMessageBox.information(None, "注册成功", "成功注册了用户" + ret["login"], QMessageBox.Ok)
            ReturnHomeFromReg()


# 信息获取完成，开始重置密码
def Reset():
    if not LoginUi.lineEditResetAccount.text():
        QMessageBox.information(None, "消息", "请输入邮箱或手机号。", QMessageBox.Ok)
        return
    if not LoginUi.lineEditResetCheckNum.text():
        QMessageBox.information(None, "消息", "请输入验证码。", QMessageBox.Ok)
        return
    if not LoginUi.lineEditResetNewPassword.text():
        QMessageBox.information(None, "消息", "请输入新密码。", QMessageBox.Ok)
        return
    if ((not LoginUi.lineEditResetCheckNewPassword.text()) or (not LoginUi.lineEditResetNewPassword.text())
            or (LoginUi.lineEditResetNewPassword.text() != LoginUi.lineEditResetCheckNewPassword.text())):
        QMessageBox.information(None, "消息", "两次输入的密码不相同, 请重新输入。", QMessageBox.Ok)
        return
    try:
        change_password(identifier = LoginUi.lineEditResetAccount.text(), vercode = LoginUi.lineEditResetCheckNum.text(),
                        passwd = LoginUi.lineEditResetNewPassword.text(),
                        passwordconfirm = LoginUi.lineEditResetCheckNewPassword.text())
    except codiaError as e:
        errorTranslate = error_translate(e)
        if errorTranslate:
            QMessageBox.critical(None, "错误", errorTranslate, QMessageBox.Ok)
        else:
            QMessageBox.critical(None, "未知错误", str(e), QMessageBox.Ok)
            raise
    else:
        QMessageBox.information(None, "成功", "密码重置成功。", QMessageBox.Ok)
        ReturnHomeFromReset()


# 从注册界面返回主界面
def ReturnHomeFromReg():
    LoginUi.loginFrame.show()
    LoginUi.registerFrame.hide()


# 从重置密码界面返回主界面
def ReturnHomeFromReset():
    LoginUi.loginFrame.show()
    LoginUi.resetFrame.hide()


# 从缓存中读取`记住密码`相关配置
def PasswordStoreRead():
    from base64 import b64decode
    try:
        with open("config.sav", "rb") as configfile:
            config = configfile.read()
        config = json.loads(b64decode(config).decode())
        if config["password_store_on"]:
            LoginUi.lineEditLoginUsername.setText(config["username"])
            LoginUi.lineEditLoginPassword.setText(cookie_decrypt(config["password"], "hdt20040127"))
            LoginUi.checkBox.setChecked(True)
        else:
            LoginUi.lineEditLoginUsername.setText(config["username"])
    except FileNotFoundError:
        print("Config file not found")
    except:
        QMessageBox.critical(None, "错误", "缓存文件损坏", QMessageBox.Ok)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    LoginWindow = QMainWindow()
    LoginUi = loginWindow.Ui_loginWindow()
    LoginUi.setupUi(LoginWindow)
    FunctionWindow = QMainWindow()
    FunctionUi = functionWindow.Ui_functionWindow()
    PasswordStoreRead()
    BeginTask()
    LoginWindow.show()
    sys.exit(app.exec_())

'''
命名规则如下:
对于此窗体 (Login) 比较容易混淆的, 在其类型后标注其隶属窗体:
    0 代表主窗体
    1 代表注册窗体
    2 代表重置密码窗体

容器名称采用 name + Type, 例如:
    loginWindow, packFrame
其余控件名称采用 type (+ id) + Name, 例如:
    lineEditLoginUsername, pushButtonLogin

'''
