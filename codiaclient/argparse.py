from .cachectrl import variables as cache_var, cache_load
from .network import variables as net_var
from .report import variables as report_var
from .requests import variables as requests_var

from argparse import ArgumentParser

def filepath(x):
    try: return open(x, encoding = 'utf-8')
    except: raise ValueError

def ArgParser():
    parser = ArgumentParser()
    parser.add_argument("-o", "--open", help = "open code to submit from PATH", metavar = 'PATH', type = filepath)
    parser.add_argument("-e", "--eid", help = "eid of the exercise", metavar = 'EID')
    parser.add_argument("-p", "--pid", help = "pid of the pack", metavar = 'PID')
    parser.add_argument("-l", "--lang", help = "lang of the code", default = 'CPP', metavar = 'LANG', choices = {'CPP', 'C', 'PYTHON'})
    parser.add_argument("-c", "--cookie", help = "cookie of your codia account", metavar = 'COOKIE')
    parser.add_argument("-u", "--username", help = "your codia username")
    parser.add_argument("--passwd", "--password", help = "your codia password")
    parser.add_argument("--no-cache", help = "do not cache or use cached username, password & cookie", action = 'store_true')
    parser.add_argument("--no-report", help = "do not report anything even if error occured", action = 'store_true')
    parser.add_argument("--register", help = "register for an account", action = 'store_true')
    parser.add_argument("--origin", help = "encoding in unicode", action = 'store_true')
    parser.add_argument("--allow-error-deg", help = "allow errors degree", type = int, choices = {0, 1, 2, 3}, default = 2)
    parser.add_argument("-q", "--request-string", help = "your request string", metavar = 'REQ')
    return parser

def ArgInit(args):
    if args.no_cache: cache_var['cacheOn'] = False
    if args.register: net_var['register'] = True
    if cache_var['cacheOn']: cache_load()
    report_var['allow_error_deg'] = args.allow_error_deg
    requests_var['l'] = args.lang
    requests_var['e'] = args.eid
    requests_var['p'] = args.pid
    if args.open:
        requests_var['sc'] = args.open.read()
        args.open.close()
