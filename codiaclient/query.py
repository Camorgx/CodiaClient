from .network import get_exercise, get_data, submit, get_pack, show_pack
from .report import report

variables = {
    'pid': None,
    'eid': None,
    'lang': None,
    'solutioncode': None,
    'username': None
}

class query:
    queryres = ""

    def __str__(self):
        return self.queryres

    def show_msg(self, qres):
        if type(qres) != str: qres = str(qres)
        self.queryres += qres
        self.queryres += '\n'

    def __init__(self, conf: dict):
        p = variables['pid']
        e = variables['eid']
        l = variables['lang']
        sc = variables['solutioncode']
        un = variables['username']

        pid = variables['pid']
        eid = variables['eid']
        lang = variables['lang']
        solutioncode = variables['solutioncode']
        username = variables['username']
        self.queryres = ""
        if len(conf) == 0: pass
        elif len(conf) == 1:
            conf[0] = conf[0].replace('get_', 'get')
            if conf[0] == 'exit': exit()
            elif conf[0] in ['p', 'pid']: variables['pid'] = None
            elif conf[0] in ['e', 'eid']: variables['eid'] = None
            elif conf[0] in ['l', 'lang']: variables['lang'] = None
            elif conf[0] in ['sc', 'solutioncode']: variables['solutioncode'] = None
            elif conf[0] in ['s', 'show']:
                self.show_msg("{}: {}".format("logined as", username))
                self.show_msg("{}: {}".format("pid", pid))
                self.show_msg("{}: {}".format("eid", eid))
                self.show_msg("{}: {}".format("lang", lang))
                self.show_msg("{}: {}".format("solutioncode", solutioncode))
            elif conf[0] in ['getexercise', 'getex']:
                if eid: get_exercise(eid = eid, pid = pid, lang = lang)
                else: report("No eid specified.", 1)
            elif conf[0] in ['getcode', 'getc']:
                if eid:
                    res = get_data(eid = eid, pid = pid)
                    self.show_msg(res[0]['solution']['asset']['content'])
                else: report("No eid specified.", 1)
            elif conf[0] == 'submit':
                if eid: res = submit(eid = eid, pid = pid, lang = lang, solutioncode = solutioncode)
                else: report("No eid specified.", 1)
            elif conf[0] == 'getpack':
                res = get_pack()
                self.show_msg(res)
            elif conf[0] in ['getr', 'getres', 'getreport', 'getreports']:
                if eid:
                    res = get_data(eid = eid, pid = pid)
                    res = {x['key']: x['value'] for x in res[0]['submission']['reports']}
                    score = res['score'].split('/')
                    if score[0] == score[1]: self.show_msg({'score': res['score'], 'time elapsed': res['time elapsed'], 'memory consumed': res['memory consumed']})
                    else: self.show_msg(res)
                else: report("No eid specified.", 1)
            elif conf[0] == 'showpack':
                if pid:
                    res = show_pack(pid)
                    self.show_msg(res)
                else: report("No pid specified.", 1)
            else: report('Invalid input.', 1)

        elif len(conf) == 2:
            if conf[0] in ['p', 'pid']: variables['pid'] = conf[1]
            elif conf[0] in ['e', 'eid']: variables['eid'] = conf[1]
            elif conf[0] in ['l', 'lang']: variables['lang'] = conf[1]
            elif conf[0] in ['o', 'open']:
                with open(conf[1], encoding = 'utf-8') as f: variables['solutioncode'] = f.read()
            elif conf[0] in ['s', 'show']:
                try: self.show_msg("{}: {}".format(conf[1], variables[conf[1]]))
                except KeyError as e: report(e.__repr__(), 1)
            elif conf[0] in ['getcode', 'getc']:
                if eid:
                    res = get_data(eid = eid, pid = pid, codecnt = conf[1])
                    self.show_msg(res[0]['solution']['asset']['content'])
                else: report("No eid specified.", 1)
            elif conf[0] in ['getr', 'getres', 'getreport', 'getreports']:
                if eid:
                    res = get_data(eid = eid, pid = pid, codecnt = conf[1])
                    res = {x['key']: x['value'] for x in res[0]['submission']['reports']}
                    score = res['score'].split('/')
                    if score[0] == score[1]: self.show_msg({'score': res['score'], 'time elapsed': res['time elapsed'], 'memory consumed': res['memory consumed']})
                    else: self.show_msg(res)
                else: report("No eid specified.", 1)
            elif conf[0] == 'getpack':
                res = get_pack(lastcnt = conf[1])
                self.show_msg(res)
            else: report('Invalid input.', 1)

        elif len(conf) == 3:
            if conf[0] in ['getcode', 'getc']:
                if conf[1] == 'to':
                    res = get_data(eid = eid, pid = pid)
                    try:
                        with open(conf[2], 'w', encoding = 'utf-8') as f: f.write(res[0]['solution']['asset']['content'])
                    except Exception as e: report(e, 1)
                elif conf[2] == 'to':
                    res = get_data(eid = eid, pid = pid, codecnt = conf[1])
                    try:
                        with open('./tmp.txt', 'w', encoding = 'utf-8') as f: f.write(res[0]['solution']['asset']['content'])
                    except Exception as e: report(e, 1)
                else: report('Invalid input.', 1)

        elif len(conf) == 4:
            if conf[0] in ['getcode', 'getc']:
                if conf[2] == 'to':
                    res = get_data(eid = eid, pid = pid, codecnt = conf[1])
                    try:
                        with open(conf[3], 'w', encoding = 'utf-8') as f: f.write(res[0]['solution']['asset']['content'])
                    except Exception as e: report(e, 1)
                else: report('Invalid input.', 1)

        else: report('Invalid input.', 1)
