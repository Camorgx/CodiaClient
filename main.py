import sys
from base64 import b64encode,b64decode
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWidgets import QMessageBox, QLineEdit
import loginWindow
from codiaclient.network import *
from codiaclient.network import _acquire_verification
from codiaclient.report import Error as codiaError, error_translate
from codiaclient import client_login
from codiaclient import report_var
from codiaclient.utils import cookie_decrypt, cookie_encrypt

#开始进行登录操作
def BeginLogin():
    loginusername = LoginUi.lineEdit0Username.text()
    loginpassword = LoginUi.lineEdit0Password.text()
    if not LoginUi.lineEdit0Username.text():
        QMessageBox.critical(None, '登录失败', '请输入邮箱或手机号。', QMessageBox.Ok)
        return False
    if not LoginUi.lineEdit0Password.text():
        QMessageBox.critical(None, '登录失败', '请输入密码。', QMessageBox.Ok)
        return False
    else:
        try:
            client_login(username = loginusername, password = loginpassword)
        except codiaError as e:
            errorTranslate = error_translate(e)
            if errorTranslate:
                QMessageBox.critical(None, '登录失败', errorTranslate, QMessageBox.Ok)
            else:
                QMessageBox.critical(None, '未知错误', str(e), QMessageBox.Ok)
                raise
            return False
        else:
            loginusernickname = logined()[1]
            try:
                with open('config.sav', 'wb') as configfile:
                    if LoginUi.checkBox.isChecked():
                        config = json.dumps({
                            'password_store_on': True,
                            'username': LoginUi.lineEdit0Username.text(),
                            'password': cookie_encrypt(LoginUi.lineEdit0Password.text(), 'hdt20040127')
                        }).encode()
                        configfile.write(b64encode(config))
                    else:
                        config = json.dumps({
                            'password_store_on': False,
                            'username': LoginUi.lineEdit0Username.text(),
                            'password': None
                        }).encode()
                        configfile.write(b64encode(config))
            except Exception as e:
                QMessageBox.critical(None, '未知错误', str(e), QMessageBox.Ok)
            QMessageBox.information(None, '登录成功', '已登录用户: ' + loginusernickname, QMessageBox.Ok)
            if not variables['me']['verified']:
                QMessageBox.information(None, '消息', '当前账号功能受限，请尽快完成联系方式验证。', QMessageBox.Ok)
            return True

#获取重置密码的验证码
def GetCheck():
    if not LoginUi.lineEdit2Account.text():
        QMessageBox.information(None, '消息', '请输入邮箱或手机号。', QMessageBox.Ok)
    try:
        ret = _acquire_verification(LoginUi.lineEdit2Account.text())[1]
    except codiaError as e:
        errorTranslate = error_translate(e)
        if errorTranslate:
            QMessageBox.critical(None, '错误', errorTranslate, QMessageBox.Ok)
        else:
            QMessageBox.critical(None, '未知错误', str(e), QMessageBox.Ok)
            raise
    else:
        if not ret:
            QMessageBox.critical(None, '错误', '验证码获取失败,请重新获取。', QMessageBox.Ok)
        elif ret['status'] == 'SUCCESS':
            QMessageBox.information(None, '成功', '验证码获取成功', QMessageBox.Ok)
        else:
            QMessageBox.critical(None, '错误', '验证码获取失败,请重新获取。', QMessageBox.Ok)

#打开注册界面
def ShowRegister():
    LoginUi.loginFrame.hide()
    LoginUi.registerFrame.show()
    if LoginUi.lineEdit0Username.text():
        LoginUi.lineEdit1Username.setText(LoginUi.lineEdit0Username.text())

#打开重置密码界面
def ShowReset():
    LoginUi.loginFrame.hide()
    LoginUi.resetFrame.show()
    if LoginUi.lineEdit0Username.text():
        LoginUi.lineEdit2Account.setText(LoginUi.lineEdit0Username.text())

#初始化任务，为登陆窗口信号绑定槽函数
def TaskInit():
    report_var['allow_error_deg'] = 1
    LoginUi.pushButtonLogin.clicked.connect(BeginLogin)
    LoginUi.lineEdit0Password.setEchoMode(QLineEdit.Password)
    LoginUi.pushButtonGoReset.clicked.connect(ShowReset)
    LoginUi.pushButtonGoRegister.clicked.connect(ShowRegister)

    LoginUi.pushButtonRegister.clicked.connect(Register)
    LoginUi.pushButton1Return.clicked.connect(ReturnHomeFromReg)
    LoginUi.lineEdit1Password.setEchoMode(QLineEdit.Password)
    LoginUi.lineEdit1Checkpassword.setEchoMode(QLineEdit.Password)

    LoginUi.pushButton2GetCheck.clicked.connect(GetCheck)
    LoginUi.pushButtonReset.clicked.connect(Reset)
    LoginUi.lineEdit2NewPassword.setEchoMode(QLineEdit.Password)
    LoginUi.lineEdit2CheckNewPassword.setEchoMode(QLineEdit.Password)
    LoginUi.pushButton2Return.clicked.connect(ReturnHomeFromReset)

    LoginUi.loginFrame.show()
    LoginUi.registerFrame.hide()
    LoginUi.resetFrame.hide()

#注册函数
def Register():
    if not LoginUi.lineEdit1Userphone.text():
        QMessageBox.information(None, '消息', '请输入邮箱。', QMessageBox.Ok)
        return
    if not LoginUi.lineEdit1Username.text():
        QMessageBox.information(None, '消息', '请输入用户名。', QMessageBox.Ok)
        return
    if not LoginUi.lineEdit1Password.text():
        QMessageBox.information(None, '消息', '请输入密码。', QMessageBox.Ok)
        return
    if ((not LoginUi.lineEdit1Checkpassword.text()) or (not LoginUi.lineEdit1Password.text())
            or (LoginUi.lineEdit1Password.text() != LoginUi.lineEdit1Checkpassword.text())):
        QMessageBox.information(None, '消息', '两次输入的密码不相同,请重新输入。', QMessageBox.Ok)
        return
    try:
        ret = register(username = LoginUi.lineEdit1Username.text(),passwd = LoginUi.lineEdit1Password.text(),
                 email = LoginUi.lineEdit1Userphone.text())
    except codiaError as e:
        errorTranslate = error_translate(e)
        if errorTranslate:
            QMessageBox.critical(None, '注册失败', errorTranslate, QMessageBox.Ok)
        else:
            QMessageBox.critical(None, '未知错误', str(e), QMessageBox.Ok)
            raise
    else:
        if not ret:
            QMessageBox.critical(None, '注册失败', '注册失败，请重试。', QMessageBox.Ok)
        else:
            QMessageBox.information(None, '注册成功', '成功注册了用户' + ret['login'], QMessageBox.Ok)
            ReturnHomeFromReg()

# 信息获取完成，开始重置密码
def Reset():
    if not LoginUi.lineEdit2Account.text():
        QMessageBox.information(None, '消息', '请输入邮箱或手机号。', QMessageBox.Ok)
        return
    if not LoginUi.lineEdit2CheckNum.text():
        QMessageBox.information(None, '消息', '请输入验证码。', QMessageBox.Ok)
        return
    if not LoginUi.lineEdit2NewPassword.text():
        QMessageBox.information(None, '消息', '请输入新密码。', QMessageBox.Ok)
        return
    if ((not LoginUi.lineEdit2CheckNewPassword.text()) or (not LoginUi.lineEdit2NewPassword.text())
            or (LoginUi.lineEdit2NewPassword.text() != LoginUi.lineEdit2CheckNewPassword.text())):
        QMessageBox.information(None, '消息', '两次输入的密码不相同,请重新输入。', QMessageBox.Ok)
        return
    try:
        change_password(identifier=LoginUi.lineEdit2Account.text(), vercode=LoginUi.lineEdit2CheckNum.text(),
                        passwd=LoginUi.lineEdit2NewPassword.text(), passwordconfirm=LoginUi.lineEdit2CheckNewPassword.text())
    except codiaError as e:
        errorTranslate = error_translate(e)
        if errorTranslate:
            QMessageBox.critical(None, '错误', errorTranslate, QMessageBox.Ok)
        else:
            QMessageBox.critical(None, '未知错误', str(e), QMessageBox.Ok)
            raise
    else:
        QMessageBox.information(None, '成功', '密码重置成功。', QMessageBox.Ok)
        ReturnHomeFromReset()

#从注册界面返回主界面
def ReturnHomeFromReg():
    LoginUi.loginFrame.show()
    LoginUi.registerFrame.hide()

#从重置密码界面返回主界面
def ReturnHomeFromReset():
    LoginUi.loginFrame.show()
    LoginUi.resetFrame.hide()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    LoginWindow = QMainWindow()
    LoginUi = loginWindow.Ui_loginWindow()
    LoginUi.setupUi(LoginWindow)
    try:
        with open('config.sav', 'rb') as configfile:
            config = configfile.read()
        config = json.loads(b64decode(config).decode())
        if config['password_store_on']:
            LoginUi.lineEdit0Username.setText(config['username'])
            LoginUi.lineEdit0Password.setText(cookie_decrypt(config['password'], 'hdt20040127'))
            LoginUi.checkBox.setChecked(True)
        else:
            LoginUi.lineEdit0Username.setText(config['username'])
    except FileNotFoundError:
        print('Config file not found')
    except:
        QMessageBox.critical(None, '错误', '缓存文件损坏', QMessageBox.Ok)
    TaskInit()
    LoginWindow.show()
    sys.exit(app.exec_())

'''
我修改了你的命名。
命名规则如下：
比较容易混淆的，在其类型后标注其隶属窗体：
    0代表主窗体
    1代表注册窗体
    2代表重置密码窗体
'''