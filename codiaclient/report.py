variables = {
    'allow_error_deg': 2
}
_error_deg_text = ["Info", "Warning", "Error", "Fatal"]


class Error(Exception):
    def __init__(self, deg, text):
        self.deg = deg
        self.text = text

    def __str__(self):
        return '{}: {}'.format(self.deg, self.text)


from sys import stderr


def report(text, deg=0, filestream=stderr, end='\n'):
    if deg <= variables['allow_error_deg']:
        filestream.write("{}: {}".format(_error_deg_text[deg], text) + end)
    else:
        raise Error(_error_deg_text[deg], text)


# 错误解释
def error_translate(e: Error):
    if 'Connect timeout' in str(e):
        return '网络连接超时。'
    elif 'Connection error' in str(e):
        return '网络连接错误。'
    elif 'email has been used' in str(e):
        return '该邮箱已被使用。'
    elif 'invalid password' in str(e):
        return '密码不合法。'
    elif 'user exists' in str(e):
        return '用户名已存在。'
    elif 'invalid username or password' in str(e):
        return '用户名不存在或密码错误。'
    elif 'Login failed' in str(e):
        return '登录失败，请重试。'
    elif 'invalid credential' in str(e):
        return '验证码不正确。'
    elif 'Identifier error' in str(e):
        return '邮箱/手机号不合法。'
    elif 'auth not found' in str(e):
        return '该账户未注册。'
    elif 'Invalid password' in str(e):
        return '新密码格式不正确。'
    else:
        return False
