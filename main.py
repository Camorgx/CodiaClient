import sys

from PyQt5.QtWidgets import QApplication, QMainWindow

from mainFunctions import MainInit
from loginFunctions import PasswordStoreRead, BeginLogin
from loginWindow import Ui_windowLogin
from mainWindow import Ui_windowMain

def LoginInit():
    global windowLogin
    windowLogin = QMainWindow()
    from codiaclientgui.utils import Font
    windowLogin.setFont(Font["main"])
    uiLogin = Ui_windowLogin()
    uiLogin.setupUi(windowLogin)
    PasswordStoreRead(uiLogin)
    BeginLogin(uiLogin = uiLogin, callback = lambda: MainInit(callback = lambda: windowLogin.close()))
    windowLogin.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    LoginInit()
    sys.exit(app.exec_())

'''
命名规则如下:
对于此窗体 (Login) 比较容易混淆的, 在其类型后标注其隶属窗体:
    0 代表主窗体
    1 代表注册窗体
    2 代表重置密码窗体

控件名称采用 type (+ id) + Name, 例如:
    lineEditLoginUsername, pushButtonLogin

'''
