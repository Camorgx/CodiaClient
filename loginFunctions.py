from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QMessageBox, QLineEdit

from loginWindow import Ui_windowLogin

from codiaclient import report_var as reportVar
from codiaclient.network import *
from codiaclient.network import _acquire_verification as AcquireVerification
from codiaclient.report import Error as codiaError, error_translate as ErrorTranslate
from codiaclient.utils import cookie_decrypt as Decrypt, cookie_encrypt as Encrypt
from codiaclientgui.utils import Font

# 初始化任务，新建一个登录窗体和对应的ui
def LoginInit(callback = None):
    global windowLogin, uiLogin
    windowLogin = QMainWindow()
    windowLogin.setFont(Font["main"])
    uiLogin = Ui_windowLogin()
    uiLogin.setupUi(windowLogin)
    PasswordStoreRead()
    windowLogin.show()
    BeginLogin(callback = callback)

# 初始化任务，为登陆窗口信号绑定槽函数
def BeginLogin(callback = None):
    reportVar["allow_error_deg"] = 1

    uiLogin.pushButtonLogin.clicked.connect(lambda: Login(callback))
    uiLogin.pushButtonLoginGoReset.clicked.connect(ShowReset)
    uiLogin.pushButtonLoginGoRegister.clicked.connect(ShowRegister)
    uiLogin.lineEditLoginPassword.setEchoMode(QLineEdit.Password)

    uiLogin.pushButtonRegister.clicked.connect(Register)
    uiLogin.pushButtonRegisterReturn.clicked.connect(RegisterReturn)
    uiLogin.lineEditRegisterPassword.setEchoMode(QLineEdit.Password)
    uiLogin.lineEditRegisterCheckPassword.setEchoMode(QLineEdit.Password)

    uiLogin.pushButtonReset.clicked.connect(Reset)
    uiLogin.pushButtonResetAcquire.clicked.connect(AcquireVerification)
    uiLogin.pushButtonResetReturn.clicked.connect(ResetReturn)
    uiLogin.lineEditResetNewPassword.setEchoMode(QLineEdit.Password)
    uiLogin.lineEditResetCheckNewPassword.setEchoMode(QLineEdit.Password)

    uiLogin.frameLogin.show()
    uiLogin.frameRegister.hide()
    uiLogin.frameReset.hide()

# 开始进行登录操作
def Login(callback = None):
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
            errorTranslate = ErrorTranslate(e)
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
                            "password": Encrypt(uiLogin.lineEditLoginPassword.text(), "hdt20040127")
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
                windowLogin.close()
                return True

# 获取重置密码的验证码
def AcquireVerification():
    if not uiLogin.lineEditResetAccount.text():
        QMessageBox.information(None, "消息", "请输入邮箱或手机号。", QMessageBox.Ok)
    try:
        res = _AcquireVerification(uiLogin.lineEditResetAccount.text())[1]
    except codiaError as e:
        errorTranslate = ErrorTranslate(e)
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
def ShowRegister():
    uiLogin.frameLogin.hide()
    uiLogin.frameRegister.show()
    if uiLogin.lineEditLoginUsername.text():
        uiLogin.lineEditRegisterUsername.setText(uiLogin.lineEditLoginUsername.text())


# 打开重置密码界面
def ShowReset():
    uiLogin.frameLogin.hide()
    uiLogin.frameReset.show()
    if uiLogin.lineEditLoginUsername.text():
        uiLogin.lineEditResetAccount.setText(uiLogin.lineEditLoginUsername.text())


# 注册函数
def Register():
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
        errorTranslate = ErrorTranslate(e)
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
            RegisterReturn()


# 信息获取完成，开始重置密码
def Reset():
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
        errorTranslate = ErrorTranslate(e)
        if errorTranslate:
            QMessageBox.critical(None, "错误", errorTranslate, QMessageBox.Ok)
        else:
            QMessageBox.critical(None, "未知错误", str(e), QMessageBox.Ok)
            raise
    else:
        QMessageBox.information(None, "成功", "密码重置成功。", QMessageBox.Ok)
        ResetReturn()


# 从注册界面返回主界面
def RegisterReturn():
    uiLogin.frameLogin.show()
    uiLogin.frameRegister.hide()


# 从重置密码界面返回主界面
def ResetReturn():
    uiLogin.frameLogin.show()
    uiLogin.frameReset.hide()

# 从缓存中读取`记住密码`相关配置
def PasswordStoreRead():
    from base64 import b64decode
    try:
        with open("config.sav", "rb") as configfile:
            config = configfile.read()
        config = json.loads(b64decode(config).decode())
        if config["password_store_on"]:
            uiLogin.lineEditLoginUsername.setText(config["username"])
            uiLogin.lineEditLoginPassword.setText(Decrypt(config["password"], "hdt20040127"))
            uiLogin.checkBox.setChecked(True)
        else:
            uiLogin.lineEditLoginUsername.setText(config["username"])
    except FileNotFoundError:
        print("Config file not found")
    except:
        QMessageBox.critical(None, "错误", "缓存文件损坏", QMessageBox.Ok)
