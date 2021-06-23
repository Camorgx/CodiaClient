import sys

from PyQt5.QtWidgets import QApplication

from mainFunctions import MainInit
from loginFunctions import LoginInit

if __name__ == "__main__":
    app = QApplication(sys.argv)
    LoginInit(callback = MainInit)
    sys.exit(app.exec_())

'''
命名规则:
    1. 变量
        变量命名的基本规则是首字母小写的驼峰命名.
        i. 控件
            type (+ Container) + Name.
            例如:
                uiLogin, windowLogin;
                lineEditLoginUsername, lineEditRegisterPassword
        ii. 其余变量
            name1 + Name2 + ... .
            例如:
                errorTranslate, config
    2. 函数 / 类
        函数 / 类命名的基本规则是首字母大写的驼峰命名.
        Name1 + Name2 + ... .
        例如:
            LoginInit, PasswordStoreRead
'''
