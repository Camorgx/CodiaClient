import sys

from PyQt5.QtWidgets import QApplication

from codiaclientgui.utils import AdjustWindowInit
from loginFunctions import LoginInit
from mainFunctions import MainInit

if __name__ == "__main__":
    app = QApplication(sys.argv)
    AdjustWindowInit()
    LoginInit(callback=MainInit)
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
    3. 其他解释
        对于 不会 / 不应该 被主体程序直接调用的元素:
            函数 / 类, 请在名字前加上下划线'_'.
            变量, 请尽量保证其私有性
'''
