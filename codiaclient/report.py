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
def report(text, deg = 0, filestream = stderr, end = '\n'):
    if deg <= variables['allow_error_deg']: filestream.write("{}: {}".format(_error_deg_text[deg], text) + end)
    else: raise Error(_error_deg_text[deg], text)
