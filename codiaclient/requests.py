from .network import get_exercise, get_data, submit, get_pack, show_pack
from .report import report
import json

variables = {
    'pid': None,
    'eid': None,
    'lang': None,
    'solutioncode': None,
    'username': None
}

class requests:
    queryres = ""
    help_txt = "We haven't provide the help text. If you need, please read the code in 'codiaclient/requests.py' to help understanding."
    def __str__(self):
        return self.queryres

    def show_msg(self, qres):
        if type(qres) != str: qres = str(qres)
        else: pass
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
        else:
            conf[0] = conf[0].replace('get_', 'get')
            if conf[0] == 'exit': exit()
            elif conf[0] in ['h', 'help']:
                if len(conf) == 1: self.show_msg(self.help_txt)
                else: report('Invalid request.', 1)
            elif conf[0] in ['p', 'pid']:
                if len(conf) == 2: variables['pid'] = conf[1]
                elif len(conf) == 1: variables['pid'] = None
                else: report('Invalid request.', 1)
            elif conf[0] in ['e', 'eid']:
                if len(conf) == 2: variables['eid'] = conf[1]
                elif len(conf) == 1: variables['eid'] = None
                else: report('Invalid request.', 1)
            elif conf[0] in ['l', 'lang']:
                if len(conf) == 2: variables['lang'] = conf[1]
                elif len(conf) == 1: variables['lang'] = None
                else: report('Invalid request.', 1)
            elif conf[0] in ['sc', 'solutioncode']:
                if len(conf) == 1: variables['solutioncode'] = None
                else: report('Invalid request.', 1)
            elif conf[0] in ['o', 'open']:
                if len(conf) == 1:
                    with open(conf[1], encoding = 'utf-8') as f: variables['solutioncode'] = f.read()
                else: report('Invalid request.', 1)
            elif conf[0] in ['show']:
                if len(conf) == 1:
                    self.show_msg(json.dumps({
                        "username": username,
                        "pid": pid,
                        "eid": eid,
                        "lang": lang,
                        "solutioncode": solutioncode
                    }))
                elif len(conf) == 2:
                    try: self.show_msg(json.dumps({conf[1]: eval(conf[1])}))
                    except Exception as e: report(e.__repr__(), 1)
                else: report('Invalid request.', 1)
            elif conf[0] in ['ge', 'getex', 'getexercise']:
                if eid:
                    res = get_exercise(eid = eid, pid = pid, lang = lang, feedback = 'json')
                    self.show_msg(res)
                else: report("No eid specified.", 1)
            elif conf[0] in ['gc', 'getc', 'getcode']: # getcode [[N] to [PATH]]
                if len(conf) <= 2:
                    if eid:
                        if len(conf) == 1:
                            res = get_data(eid = eid, pid = pid)
                            self.show_msg(json.dumps(res[0]['solution']['asset']['content']))
                        elif len(conf) == 2:
                            if conf[1] == 'to':
                                res = get_data(eid = eid, pid = pid)
                                try:
                                    with open('./tmp.txt', 'w', encoding = 'utf-8') as f: f.write(res[0]['solution']['asset']['content'])
                                except Exception as e: report(e, 1)
                            else:
                                try: res = get_data(eid = eid, pid = pid, codecnt = int(conf[1]))
                                except ValueError: report('Invalid request: type(codecnt) should be int.', 1)
                                else:
                                    if res == None: report('Invalid request.', 1)
                                    else: self.show_msg(json.dumps(res[0]['solution']['asset']['content']))
                        else: pass
                    else: report("No eid specified.", 1)
                elif len(conf) == 3:
                    if conf[1] == 'to':
                        res = get_data(eid = eid, pid = pid)
                        try:
                            with open(conf[2], 'w', encoding = 'utf-8') as f: f.write(res[0]['solution']['asset']['content'])
                        except Exception as e: report(e, 1)
                    elif conf[2] == 'to':
                        try: res = get_data(eid = eid, pid = pid, codecnt = int(conf[1]))
                        except ValueError: report('Invalid request: type(lastcnt) should be int.', 1)
                        else:
                            try:
                                with open('./tmp.txt', 'w', encoding = 'utf-8') as f: f.write(res[0]['solution']['asset']['content'])
                            except Exception as e: report(e, 1)
                    else: report('Invalid request.', 1)
                elif len(conf) == 4:
                    if conf[2] == 'to':
                        try: res = get_data(eid = eid, pid = pid, codecnt = int(conf[1]))
                        except ValueError: report('Invalid request: type(codecnt) should be int.', 1)
                        else:
                            try:
                                with open(conf[3], 'w', encoding = 'utf-8') as f: f.write(res[0]['solution']['asset']['content'])
                            except Exception as e: report(e, 1)
                    else: report('Invalid request.', 1)
                else: report('Invalid request.', 1)
            elif conf[0] in ['submit']:
                if len(conf) == 1:
                    if eid: res = submit(eid = eid, pid = pid, lang = lang, solutioncode = solutioncode)
                    else: report("No eid specified.", 1)
                else: report('Invalid request.', 1)
            elif conf[0] in ['gp', 'getp', 'getpack']: #getpack [N] [before PID]
                if len(conf) == 1:
                    res = get_pack()
                    self.show_msg(json.dumps(res))
                elif len(conf) == 2:
                    try: res = get_pack(lastcnt = int(conf[1]))
                    except ValueError: report('Invalid request: type(lastcnt) should be int.', 1)
                    else:
                        if res == None: report('Invalid request.', 1)
                        else: self.show_msg(json.dumps(res))
                elif len(conf) == 3:
                    if conf[1] in ['bf', 'before']:
                        res = get_pack(before = conf[2])
                        self.show_msg(json.dumps(res))
                    else: report('Invalid request.', 1)
                elif len(conf) == 4:
                    if conf[2] in ['bf', 'before']:
                        try: res = get_pack(before = conf[3], lastcnt = int(conf[1]))
                        except ValueError: report('Invalid request: type(lastcnt) should be int.', 1)
                        else:
                            if res == None: report('Invalid request.', 1)
                            else: self.show_msg(json.dumps(res))
                    else: report('Invalid request.', 1)
                else: report('Invalid request.', 1)
            elif conf[0] in ['gr', 'getr', 'getres', 'getreport', 'getreports']:
                if len(conf) <= 2:
                    if eid:
                        if len(conf) == 1: res = get_data(eid = eid, pid = pid)
                        elif len(conf) == 2:
                            try: res = get_data(eid = eid, pid = pid, codecnt = int(conf[1]))
                            except ValueError:
                                report('Invalid request: type(codecnt) should be int.', 1)
                                return
                        else: pass
                        res = {x['key']: x['value'] for x in res[0]['submission']['reports']}
                        try: score = res['score'].split('/')
                        except: self.show_msg(json.dumps(res))
                        else:
                            if score[0] == score[1]: self.show_msg(json.dumps({
                                'score': res['score'],
                                'time elapsed': res['time elapsed'],
                                'memory consumed': res['memory consumed']
                            }))
                            else: self.show_msg(json.dumps(res))
                    else: report("No eid specified.", 1)
                else: report('Invalid request.', 1)
            elif conf[0] in ['sp', 'showp', 'showpack']:
                if len(conf) == 1:
                    if pid:
                        res = show_pack(pid)
                        self.show_msg(json.dumps(res))
                    else: report("No pid specified.", 1)
                else: report('Invalid request.', 1)
            else: report('Invalid request.', 1)
