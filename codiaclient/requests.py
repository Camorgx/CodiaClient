import json

from .network import variables as net_var, get_exercise, get_data, submit, get_pack, show_pack, start_pack
from .report import report
from .utils import AliasesDict

aliases = {
    'p': 'pid',
    'e': 'eid',
    'l': 'lang',
    'sc': 'solutioncode',
}

variables = AliasesDict({
    'pid': None,
    'eid': None,
    'lang': None,
    'solutioncode': None
}, aliases)


class Requests:
    queryres = ""
    help_txt = "We haven't provide the help text. If you need, please read the code in 'codiaclient/requests.py' to help understanding."

    def show_msg(self, qres):
        if type(qres) != str:
            qres = str(qres)
        else:
            pass
        self.queryres += qres
        self.queryres += '\n'

    def __init__(self, conf: dict):
        variables.update(net_var['me'])
        self.queryres = ""
        if len(conf) == 0:
            pass
        else:
            conf[0] = conf[0].replace('get_', 'get')
            if conf[0] == 'exit':
                exit()
            elif conf[0] in ['h', 'help']:
                if len(conf) == 1:
                    self.show_msg(self.help_txt)
                else:
                    report('Invalid request.', 1)
            elif conf[0] in variables or conf[0] in aliases:
                if len(conf) == 2:
                    variables[conf[0]] = conf[1]
                else:
                    report('Use `show VAR` to show the variables.', 1)
            elif conf[0] in ['del', 'reset']:
                if len(conf) == 2:
                    if conf[1] in variables or conf[1] in aliases:
                        variables[conf[1]] = None
                    else:
                        report('Variable `{}` doesn\'t exist.'.format(conf[1]), 1)
                elif len(conf) == 1:
                    for x in variables:
                        variables[x] = None
                else:
                    report('Invalid request.', 1)
            elif conf[0] in ['o', 'open']:
                if len(conf) >= 2:
                    path = ' '.join(conf[1:])
                    while path[:1] == ' ': path = path[1:]
                    while path[-1:] == ' ': path = path[:-1]
                    if path[:1] == '\"': path = path[1:]
                    if path[-1:] == '\"': path = path[:-1]
                    try:
                        with open(path, encoding='utf-8') as f:
                            variables['sc'] = f.read()
                    except OSError as e:
                        report(e, 1)
                else:
                    report('Invalid request.', 1)
            elif conf[0] in ['show']:
                if len(conf) == 1:
                    self.show_msg(json.dumps(variables))
                elif len(conf) == 2:
                    try:
                        self.show_msg(json.dumps({conf[1]: variables[conf[1]]}))
                    except Exception as e:
                        report(e.__repr__(), 1)
                else:
                    report('Invalid request.', 1)
            elif conf[0] in ['ge', 'getex', 'getexercise']:
                if variables['e']:
                    res = get_exercise(eid=variables['e'], pid=variables['p'], lang=variables['l'], feedback='json')
                    self.show_msg(res)
                else:
                    report("No eid specified.", 1)
            elif conf[0] in ['gc', 'getc', 'getcode']:  # getcode [[N] to [PATH]]
                if len(conf) <= 2:
                    if variables['e']:
                        if len(conf) == 1:
                            res = get_data(eid=variables['e'], pid=variables['p'])
                            self.show_msg(json.dumps(res[0]['solution']['asset']['content']))
                        elif len(conf) == 2:
                            if conf[1] == 'to':
                                res = get_data(eid=variables['e'], pid=variables['p'])
                                try:
                                    with open('./tmp.txt', 'w', encoding='utf-8') as f:
                                        f.write(res[0]['solution']['asset']['content'])
                                except Exception as e:
                                    report(e, 1)
                            else:
                                try:
                                    res = get_data(eid=variables['e'], pid=variables['p'], codecnt=int(conf[1]))
                                except ValueError:
                                    report('Invalid request: type(codecnt) should be int.', 1)
                                else:
                                    if res == None:
                                        report('Invalid request.', 1)
                                    else:
                                        self.show_msg(json.dumps(res[0]['solution']['asset']['content']))
                        else:
                            pass
                    else:
                        report("No eid specified.", 1)
                elif len(conf) == 3:
                    if conf[1] == 'to':
                        res = get_data(eid=variables['e'], pid=variables['p'])
                        try:
                            with open(conf[2], 'w', encoding='utf-8') as f:
                                f.write(res[0]['solution']['asset']['content'])
                        except Exception as e:
                            report(e, 1)
                    elif conf[2] == 'to':
                        try:
                            res = get_data(eid=variables['e'], pid=variables['p'], codecnt=int(conf[1]))
                        except ValueError:
                            report('Invalid request: type(lastcnt) should be int.', 1)
                        else:
                            try:
                                with open('./tmp.txt', 'w', encoding='utf-8') as f:
                                    f.write(res[0]['solution']['asset']['content'])
                            except Exception as e:
                                report(e, 1)
                    else:
                        report('Invalid request.', 1)
                elif len(conf) == 4:
                    if conf[2] == 'to':
                        try:
                            res = get_data(eid=variables['e'], pid=variables['p'], codecnt=int(conf[1]))
                        except ValueError:
                            report('Invalid request: type(codecnt) should be int.', 1)
                        else:
                            try:
                                with open(conf[3], 'w', encoding='utf-8') as f:
                                    f.write(res[0]['solution']['asset']['content'])
                            except Exception as e:
                                report(e, 1)
                    else:
                        report('Invalid request.', 1)
                else:
                    report('Invalid request.', 1)
            elif conf[0] in ['submit']:
                if len(conf) == 1:
                    if variables['e']:
                        res = submit(eid=variables['e'], pid=variables['p'], lang=variables['l'],
                                     solutioncode=variables['sc'])
                    else:
                        report("No eid specified.", 1)
                else:
                    report('Invalid request.', 1)
            elif conf[0] in ['gp', 'getp', 'getpack']:  # getpack [N] [before|after PID]
                if len(conf) == 1:
                    res = get_pack()
                    if not res:
                        report("No result.", 1)
                    else:
                        self.show_msg(json.dumps(res['nodes']))
                elif len(conf) == 2:
                    try:
                        res = get_pack(lastcnt=int(conf[1]))
                    except ValueError:
                        report('Invalid request: type(lastcnt) should be int.', 1)
                    else:
                        if not res:
                            report("No result.", 1)
                        else:
                            self.show_msg(json.dumps(res['nodes']))
                elif len(conf) == 3:
                    if conf[1] in ['bf', 'before']:
                        res = get_pack(before=conf[2])
                        if not res:
                            report("No result.", 1)
                        else:
                            self.show_msg(json.dumps(res['nodes']))
                    elif conf[1] in ['af', 'after']:
                        res = get_pack(after=conf[2])
                        if not res:
                            report("No result.", 1)
                        else:
                            self.show_msg(json.dumps(res['nodes']))
                    else:
                        report('Invalid request.', 1)
                elif len(conf) == 4:
                    if conf[2] in ['bf', 'before']:
                        try:
                            res = get_pack(before=conf[3], lastcnt=int(conf[1]))
                        except ValueError:
                            report('Invalid request: type(lastcnt) should be int.', 1)
                        else:
                            if not res:
                                report("No result.", 1)
                            else:
                                self.show_msg(json.dumps(res['nodes']))
                    if conf[2] in ['af', 'after']:
                        try:
                            res = get_pack(after=conf[3], lastcnt=int(conf[1]))
                        except ValueError:
                            report('Invalid request: type(lastcnt) should be int.', 1)
                        else:
                            if not res:
                                report("No result.", 1)
                            else:
                                self.show_msg(json.dumps(res['nodes']))
                    else:
                        report('Invalid request.', 1)
                else:
                    report('Invalid request.', 1)
            elif conf[0] in ['gr', 'getr', 'getres', 'getreport', 'getreports']:
                if len(conf) <= 2:
                    if variables['e']:
                        if len(conf) == 1:
                            res = get_data(eid=variables['e'], pid=variables['p'])
                        elif len(conf) == 2:
                            try:
                                res = get_data(eid=variables['e'], pid=variables['p'], codecnt=int(conf[1]))
                            except ValueError:
                                if conf[1].lower() == 'all':
                                    self.show_msg(json.dumps(get_data(eid=variables['e'], pid=variables['p'])))
                                else:
                                    report('Invalid request: type(codecnt) should be int.', 1)
                                return
                        else:
                            pass
                        res = {x['key']: x['value'] for x in res[0]['submission']['reports']}
                        try:
                            score = res['score'].split('/')
                        except:
                            self.show_msg(json.dumps(res))
                        else:
                            if score[0] == score[1]:
                                self.show_msg(json.dumps({
                                    'score': res['score'],
                                    'time elapsed': res['time elapsed'],
                                    'memory consumed': res['memory consumed']
                                }))
                            else:
                                self.show_msg(json.dumps(res))
                    else:
                        report("No eid specified.", 1)
                else:
                    report('Invalid request.', 1)
            elif conf[0] in ['sp', 'showp', 'showpack']:
                if len(conf) == 1:
                    if variables['p']:
                        res = show_pack(variables['p'])
                        self.show_msg(json.dumps(res))
                    else:
                        report("No pid specified.", 1)
                else:
                    report('Invalid request.', 1)
            elif conf[0] in ['startp', 'startpack']:
                if len(conf) == 1:
                    if variables['p']:
                        res = start_pack(variables['p'])
                        self.show_msg(json.dumps(res))
                    else:
                        report("No pid specified.", 1)
                else:
                    report('Invalid request.', 1)
            else:
                report('Invalid request.', 1)


def requests(conf: dict):
    res = Requests(conf)
    return res.queryres
