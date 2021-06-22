from PyQt5.QtWidgets import QMessageBox, QLineEdit

from loginWindow import Ui_windowLogin

from codiaclient import report_var, net_var
from codiaclient.network import *
from codiaclient.network import _acquire_verification
from codiaclient.report import Error as codiaError, error_translate
from codiaclient.utils import cookie_decrypt, cookie_encrypt

# 开始进行登录操作
def Login(uiLogin: Ui_windowLogin, callback = None):
    loginUsername = uiLogin.lineEditLoginUsername.text()
    loginPassword = uiLogin.lineEditLoginPassword.text()
    if not uiLogin.lineEditLoginUsername.text():
        QMessageBox.critical(None, "登录失败", "请输入邮箱或手机号。", QMessageBox.Ok)
        return False
    if not uiLogin.lineEditLoginPassword.text():
        QMessageBox.critical(None, "登录失败", "请输入密码。", QMessageBox.Ok)
        return False
    else:
        try:
            client_login(username = loginUsername, password = loginPassword)
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
                    if uiLogin.checkBox.isChecked():
                        config = json.dumps({
                            "password_store_on": True,
                            "username": uiLogin.lineEditLoginUsername.text(),
                            "password": cookie_encrypt(uiLogin.lineEditLoginPassword.text(), "hdt20040127")
                        }).encode()
                        configfile.write(b64encode(config))
                    else:
                        config = json.dumps({
                            "password_store_on": False,
                            "username": uiLogin.lineEditLoginUsername.text(),
                            "password": None
                        }).encode()
                        configfile.write(b64encode(config))
            except Exception as e:
                QMessageBox.critical(None, "未知错误", str(e), QMessageBox.Ok)
            finally:
                callback and callback()
                return True

# 获取重置密码的验证码
def AcquireVerification(uiLogin: Ui_windowLogin):
    if not uiLogin.lineEditResetAccount.text():
        QMessageBox.information(None, "消息", "请输入邮箱或手机号。", QMessageBox.Ok)
    try:
        res = _acquire_verification(uiLogin.lineEditResetAccount.text())[1]
    except codiaError as e:
        errorTranslate = error_translate(e)
        if errorTranslate:
            QMessageBox.critical(None, "错误", errorTranslate, QMessageBox.Ok)
        else:
            QMessageBox.critical(None, "未知错误", str(e), QMessageBox.Ok)
            raise
    else:
        if not res:
            QMessageBox.critical(None, "错误", "验证码获取失败, 请重新获取。", QMessageBox.Ok)
        elif res["status"] == "SUCCESS":
            QMessageBox.information(None, "成功", "验证码获取成功", QMessageBox.Ok)
        else:
            QMessageBox.critical(None, "错误", "验证码获取失败, 请重新获取。", QMessageBox.Ok)


# 打开注册界面
def ShowRegister(uiLogin: Ui_windowLogin):
    uiLogin.frameLogin.hide()
    uiLogin.frameRegister.show()
    if uiLogin.lineEditLoginUsername.text():
        uiLogin.lineEditRegisterUsername.setText(uiLogin.lineEditLoginUsername.text())


# 打开重置密码界面
def ShowReset(uiLogin: Ui_windowLogin):
    uiLogin.frameLogin.hide()
    uiLogin.frameReset.show()
    if uiLogin.lineEditLoginUsername.text():
        uiLogin.lineEditResetAccount.setText(uiLogin.lineEditLoginUsername.text())


# 初始化任务，为登陆窗口信号绑定槽函数
def BeginLogin(uiLogin: Ui_windowLogin, callback = None):
    report_var["allow_error_deg"] = 1

    uiLogin.lineEditLoginPassword.setEchoMode(QLineEdit.Password)
    uiLogin.pushButtonLogin.clicked.connect(lambda: Login(uiLogin, callback))
    uiLogin.pushButtonLoginGoReset.clicked.connect(lambda: ShowReset(uiLogin))
    uiLogin.pushButtonLoginGoRegister.clicked.connect(lambda: ShowRegister(uiLogin))

    uiLogin.pushButtonRegister.clicked.connect(lambda: Register(uiLogin))
    uiLogin.pushButtonRegisterReturn.clicked.connect(lambda: ReturnHomeFromReg(uiLogin))
    uiLogin.lineEditRegisterPassword.setEchoMode(QLineEdit.Password)
    uiLogin.lineEditRegisterCheckPassword.setEchoMode(QLineEdit.Password)

    uiLogin.lineEditResetNewPassword.setEchoMode(QLineEdit.Password)
    uiLogin.lineEditResetCheckNewPassword.setEchoMode(QLineEdit.Password)
    uiLogin.pushButtonReset.clicked.connect(lambda: Reset(uiLogin))
    uiLogin.pushButtonResetAcquire.clicked.connect(lambda: AcquireVerification(uiLogin))
    uiLogin.pushButtonResetReturn.clicked.connect(lambda: ReturnHomeFromReset(uiLogin))

    uiLogin.frameLogin.show()
    uiLogin.frameRegister.hide()
    uiLogin.frameReset.hide()


# 注册函数
def Register(uiLogin: Ui_windowLogin):
    if not uiLogin.lineEditRegisterUserphone.text():
        QMessageBox.information(None, "消息", "请输入邮箱。", QMessageBox.Ok)
        return
    if not uiLogin.lineEditRegisterUsername.text():
        QMessageBox.information(None, "消息", "请输入用户名。", QMessageBox.Ok)
        return
    if not uiLogin.lineEditRegisterPassword.text():
        QMessageBox.information(None, "消息", "请输入密码。", QMessageBox.Ok)
        return
    if ((not uiLogin.lineEditRegisterCheckPassword.text()) or (not uiLogin.lineEditRegisterPassword.text())
            or (uiLogin.lineEditRegisterPassword.text() != uiLogin.lineEditRegisterCheckPassword.text())):
        QMessageBox.information(None, "消息", "两次输入的密码不相同, 请重新输入。", QMessageBox.Ok)
        return
    try:
        res = register(username = uiLogin.lineEditRegisterUsername.text(), passwd = uiLogin.lineEditRegisterPassword.text(),
                       email = uiLogin.lineEditRegisterUserphone.text())
    except codiaError as e:
        errorTranslate = error_translate(e)
        if errorTranslate:
            QMessageBox.critical(None, "注册失败", errorTranslate, QMessageBox.Ok)
        else:
            QMessageBox.critical(None, "未知错误", str(e), QMessageBox.Ok)
            raise
    else:
        if not res:
            QMessageBox.critical(None, "注册失败", "注册失败，请重试。", QMessageBox.Ok)
        else:
            QMessageBox.information(None, "注册成功", "成功注册了用户" + res["login"], QMessageBox.Ok)
            ReturnHomeFromReg()


# 信息获取完成，开始重置密码
def Reset(uiLogin: Ui_windowLogin):
    if not uiLogin.lineEditResetAccount.text():
        QMessageBox.information(None, "消息", "请输入邮箱或手机号。", QMessageBox.Ok)
        return
    if not uiLogin.lineEditResetCheckNum.text():
        QMessageBox.information(None, "消息", "请输入验证码。", QMessageBox.Ok)
        return
    if not uiLogin.lineEditResetNewPassword.text():
        QMessageBox.information(None, "消息", "请输入新密码。", QMessageBox.Ok)
        return
    if ((not uiLogin.lineEditResetCheckNewPassword.text()) or (not uiLogin.lineEditResetNewPassword.text())
            or (uiLogin.lineEditResetNewPassword.text() != uiLogin.lineEditResetCheckNewPassword.text())):
        QMessageBox.information(None, "消息", "两次输入的密码不相同, 请重新输入。", QMessageBox.Ok)
        return
    try:
        change_password(identifier = uiLogin.lineEditResetAccount.text(), vercode = uiLogin.lineEditResetCheckNum.text(),
                        passwd = uiLogin.lineEditResetNewPassword.text(),
                        passwordconfirm = uiLogin.lineEditResetCheckNewPassword.text())
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
def ReturnHomeFromReg(uiLogin: Ui_windowLogin):
    uiLogin.frameLogin.show()
    uiLogin.frameRegister.hide()


# 从重置密码界面返回主界面
def ReturnHomeFromReset(uiLogin: Ui_windowLogin):
    uiLogin.frameLogin.show()
    uiLogin.frameReset.hide()

# 从缓存中读取`记住密码`相关配置
def PasswordStoreRead(uiLogin: Ui_windowLogin):
    from base64 import b64decode
    try:
        with open("config.sav", "rb") as configfile:
            config = configfile.read()
        config = json.loads(b64decode(config).decode())
        if config["password_store_on"]:
            uiLogin.lineEditLoginUsername.setText(config["username"])
            uiLogin.lineEditLoginPassword.setText(cookie_decrypt(config["password"], "hdt20040127"))
            uiLogin.checkBox.setChecked(True)
        else:
            uiLogin.lineEditLoginUsername.setText(config["username"])
    except FileNotFoundError:
        print("Config file not found")
    except:
        QMessageBox.critical(None, "错误", "缓存文件损坏", QMessageBox.Ok)
