from .report import report
from .utils import passwd_hash, cookie_encrypt, cookie_decrypt
from .cachectrl import variables as cache_var, cache_username_passwd_cookie as cache
import json

url = 'https://code.bdaa.pro/graphql/'
coding_base_headers = {
    'accept': '*/*',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'cache-control': 'no-cache',
    'content-type': 'application/json',
    'origin': 'https://code.bdaa.pro',
    'pragma': 'no-cache',
    'referer': 'https://code.bdaa.pro',
    'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="90", "Microsoft Edge";v="90"',
    'sec-ch-ua-mobile': '?0',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36 Edg/90.0.818.46',
}

login_base_headers = {
    'accept': '*/*',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'content-type': 'application/json',
    'origin': 'https://code.bdaa.pro',
    'referer': 'https://code.bdaa.pro/login',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36 Edg/90.0.818.46',
}
def post(url, headers, data, timeout = 5):
    headers['content-len'] = str(len(data))
    if type(data) == str: data = data.encode('utf-8')
    if type(data) != bytes:
        report('Datatype error.', 1)
        return False
    import requests
    try: res = requests.post(url = url, headers = headers, data = data, timeout = timeout)
    except requests.exceptions.ConnectTimeout:
        report('Connect timeout.', 1)
        return False
    except requests.exceptions.ConnectionError:
        report('Connection error.', 1)
        return False
    except Exception as e:
        report(e, 1)
        return False
    else: return res


def client_login(username, password = None, cookie = None):
    if username and not cookie and not password:
        import getpass
        try: password = getpass.getpass('Enter password:')
        except KeyboardInterrupt: exit()
        if not password:
            report('Empty password. Do you want to change your password? [y/N]', end = '')
            choice = input()
            if choice == 'n' or choice == 'N': exit()
            elif choice == 'y' or choice == 'Y':
                password = change_password()
                if not password:
                    report("Empty password.", 3)
            else: exit()

    if username and password:
        if cookie:
            report("Using the input cookie.")
            coding_base_headers['cookie'] = cookie
            displayName = logined()
            if displayName:
                report('Login succeeded.({})'.format(displayName))
                if cache_var['cacheOn']:
                    if username in cache_var['logindic']:
                        report('We have cached your cookie. Do you want to cover it? [Y/n]', end = '')
                        choice = input()
                        if choice == 'n' or choice == 'N': pass
                        elif choice == 'y' or choice == 'Y': cache(username, password, cookie)
                        else:
                            report('Received bad parameter, executing the default operation.', 1)
                            cache(username, password, cookie)
                    else: cache(username, password, cookie)
            else:
                report('Invalid cookie input.', 1)
                if cache_var['cacheOn'] and username in cache_var['logindic'] and cache_var['logindic'][username]['passwd'] == passwd_hash(password):
                    coding_base_headers['cookie'] = cookie_decrypt(cache_var['logindic'][username]['cookie'], password)
                    report("Using cached cookie.")
                    displayName = logined()
                    if displayName: report('Login succeeded.({})'.format(displayName))
                    else:
                        report('Invalid cached cookie.', 1)
                        login(username, password)
                else: login(username, password)
        else: # no cookie input
            if cache_var['cacheOn'] and username in cache_var['logindic'] and cache_var['logindic'][username]['passwd'] == passwd_hash(password):
                coding_base_headers['cookie'] = cookie_decrypt(cache_var['logindic'][username]['cookie'], password)
                report("Using cached cookie.")
                displayName = logined()
                if displayName: report("Login succeeded.({})".format(displayName))
                else:
                    report('Invalid cached cookie.', 1)
                    login(username, password)
            else: login(username, password)
    elif cookie:
        report("Using the input cookie.")
        coding_base_headers['cookie'] = cookie
        displayName = logined()
        if displayName: report('Login succeeded.({})'.format(displayName))
        else: report('Invalid cookie input.', 3)
    else: report('No username or cookie specified.', 3)

def logined():
    headers = coding_base_headers.copy()
    data = json.dumps({
        "operationName": None,
        "variables": {},
        "query": r'''
{
    me {
        id
        login
        displayName
        avatarUrl
        defaultEmail
        verified
    }
}''',
    })
    res = post(url = url, headers = headers, data = data)
    if not res: return False
    res = json.loads(res.text)
    if 'errors' in res: return False
    else: return res['data']['me']['displayName']

def login(username, passwd):
    report('Try login.')
    res = _login(username, passwd)
    if not res:
        report('Login failed.', 3)
        return False
    else:
        report('Login succeeded.({})'.format(res['displayName']))
        if cache_var['cacheOn']: cache(username, passwd, coding_base_headers['cookie'])
        return True

def change_password():
    headers = login_base_headers.copy()
    identifier, res = _acquire_verification()
    if (not res) or res['status'] != "SUCCESS":
        report("Unknown error.", 3)
        return None
    elif res['status'] == "SUCCESS":
        report("Code sent successfully.")
    else: return False
    import getpass
    try: vercode = getpass.getpass('Enter received code:')
    except KeyboardInterrupt: exit()
    if not vercode or len(vercode) != 6:
        report('Invalid code.', 3)
        return None
    else:
        try: password = getpass.getpass('Enter your new password:')
        except KeyboardInterrupt: exit()
        if not password or len(password) <= 6: report('Invalid password.', 3)
        else:
            data = {
                "operationName": "verify",
                "variables": {
                    "identifier": identifier,
                    "code": vercode
                },
                "query": r'''
mutation verify($identifier: String!, $code: String!) {
    verify(identifier: $identifier, credential: $code) {
        verifyToken
    }
}'''
            }
            data = json.dumps(data)
            res = post(url = url, headers = headers, data = data)
            if not res: return False
            res_data = json.loads(res.text)
            if 'errors' in res_data:
                report("change_password: " + res_data['errors'][0]['message'] + '.', 2)
                return False
            verifyToken = res_data['data']['verify']['verifyToken']
            data = {
                "operationName": "passwordChange",
                "variables": {
                    "newPassword": password,
                    "newPasswordConfirm": password,
                    "verifyToken": verifyToken
                },
                "query": r'''
mutation passwordChange($newPassword: String!, $verifyToken: String) {
    passwordChange(newPassword: $newPassword, verifyToken: $verifyToken) {
        id
    }
}'''
            }
            data = json.dumps(data)
            res = post(url = url, headers = headers, data = data)
            if not res: return False
            res_data = json.loads(res.text)
            if 'errors' in res_data:
                report("change_password: " + res_data['errors'][0]['message'] + '.', 2)
                return False
    return password


def _acquire_verification():
    headers = login_base_headers.copy()
    identifier = input("Enter your email/phone:")
    try: int(identifier)
    except: id_type = "EMAIL"
    else: id_type = "PHONE"
    data = {
        "operationName": "acquireVerification",
        "variables": {
            "identifier": identifier,
            "type": id_type
        },
        "query": r'''
mutation acquireVerification($identifier: String!, $type: VerificationType!) {
  acquireVerification(identifier: $identifier, type: $type) {
    status
    message
  }
}'''
    }
    data = json.dumps(data)
    res = post(url = url, headers = headers, data = data)
    if not res: return None, False
    return identifier, json.loads(res.text)['data']['acquireVerification']

def submit(eid, pid, lang, solutioncode):
    if pid: return _submit_from_pack(eid, pid, lang, solutioncode)
    else: return _submit_not_from_pack(eid, lang, solutioncode)

def get_data(eid, pid, codecnt = None):
    if pid: return _get_data_from_pack(eid, pid, codecnt)
    else: return _get_data_not_from_pack(eid, codecnt)

def get_exercise(eid, pid, lang, feedback = 'dict'):
    if pid: return _get_exercise_from_pack(eid, pid, lang, feedback)
    else: return _get_exercise_not_from_pack(eid, lang, feedback)

def get_pack(before = None, lastcnt = None):
    if lastcnt == None: lastcnt = 8
    if type(lastcnt) == str:
        try: lastcnt = int(lastcnt)
        except: pass
    if type(lastcnt) != int:
        report('Unknown error.', 1)
        return False
    headers = coding_base_headers.copy()
    data = {
        "operationName": "publicExercisePacks",
        "variables": {
            'lastcnt': lastcnt
        },
        "query": r'''
query publicExercisePacks($lastcnt: Int!, $before: String) {
    publicExercisePacks(last: $lastcnt, before: $before) {
        nodes {
            id
            name
            start
            due
            exclusive
            protected
            codingExercises {
                viewerPassedCount
                totalCount
            }
        }
    }
}'''
    }
    if before: data['variables']['before'] = before
    data = json.dumps(data)
    res = post(url = url, headers = headers, data = data)
    if not res: return False
    return json.loads(res.text)['data']['publicExercisePacks']['nodes']

def show_pack(pid):
    headers = coding_base_headers.copy()
    data = json.dumps({
        "operationName": "pack",
        "variables": {
            "pid": pid
        },
        "query": r'''
query pack($pid: ID!) {
    node(id: $pid) {
        id
        ... on ExercisePack {
            name
            description { content }
            time
            start
            due
            codingExercises {
                totalCount
                viewerPassedCount
                nodes {
                    id
                    title
                }
            }
        }
    }
}'''})
    res = post(url = url, headers = headers, data = data)
    if not res: return False
    return json.loads(res.text)['data']['node']

def _login(username, passwd):
    headers = login_base_headers.copy()
    data = json.dumps({
        "operationName": "login",
        "variables": {
            "username": username,
            "password": passwd
        },
        "query": r'''
mutation login($username: String!, $password: String!) {
    login(login: $username, password: $password) {
        user {
            id
            login
            displayName
            avatarUrl
            defaultEmail
            verified
        }
    }
}'''})
    
    res = post(url = url, headers = headers, data = data)
    if not res: return False
    res_data = json.loads(res.text)
    if 'errors' in res_data:
        report("_login: " + res_data['errors'][0]['message'] + '.', 2)
        return False
    else:
        from re import search
        try: coding_base_headers['cookie'] = search(r'token=(.*?);', res.headers['Set-Cookie']).group().replace(';', '')
        except:
            report('Unknown login error.', 1)
            return False
    return res_data['data']['login']['user']

def _submit_from_pack(eid, pid, lang, solutioncode):
    headers = coding_base_headers.copy()
    data = json.dumps({
        "operationName": None,
        "variables": {
            "eid": eid,
            "pid": pid,
            "lang": lang,
            "sol": solutioncode,
            "a": {
                "editStat": []
            }
        },
        "query": r'''
mutation ($eid: ID!, $pid: ID, $lang: Language!, $sol: String!, $a: JSONObject) {
    submit(eid: $eid, pid: $pid, solution: {lang: $lang, asset: {content: $sol} }, additionalInfo: $a) {
        token
    }
}'''})
    return post(url = url, headers = headers, data = data)

def _submit_not_from_pack(eid, lang, solutioncode):
    headers = coding_base_headers.copy()
    data = json.dumps({
        "operationName":None,
        "variables": {
            "eid": eid,
            "lang": lang,
            "sol": solutioncode,
            "a": {
                "editStat": []
            }
        },
        "query": r'''
mutation ($eid: ID!, $pid: ID, $lang: Language!, $sol: String!, $a: JSONObject) {
    submit(eid: $eid, pid: $pid, solution: {lang: $lang, asset: {content: $sol} }, additionalInfo: $a) {
        token
    }
}'''})
    return post(url = url, headers = headers, data = data)

def _get_data_not_from_pack(eid, codecnt = None):
    if codecnt == None: codecnt = 1
    if type(codecnt) == str:
        try: codecnt = int(codecnt)
        except: pass
    if type(codecnt) != int:
        report('Unknown error.', 1)
        return False
    headers = coding_base_headers.copy()
    data = json.dumps({
        "operationName": "codingExercise",
        "variables": {
            "eid": eid,
            "codecnt": codecnt
        },
        "query": '''
query codingExercise($eid: ID!, $codecnt: Int!) {
    node(id: $eid) {
        ... on CodingExercise {
            viewerStatus {
                exerciseStatuses(last: $codecnt) {
                    nodes {
                        ... on CodingExerciseStatus {
                            id
                            scoreRate
                            submission {
                                id
                                reports {
                                    key
                                    value
                                }
                            }
                            solution {
                                lang 
                                asset { content }
                            } 
                        }
                    }
                }
            }
        }
    }
}'''})
    res = post(url = url, headers = headers, data = data)
    if not res: return False
    return json.loads(res.text)['data']['node']['viewerStatus']['exerciseStatuses']['nodes']

def _get_data_from_pack(eid, pid, codecnt = None):
    if codecnt == None: codecnt = 1
    if type(codecnt) == str:
        try: codecnt = int(codecnt)
        except: pass
    if type(codecnt) != int:
        report('Unknown error.', 1)
        return False
    headers = coding_base_headers.copy()
    data = json.dumps({
        "operationName": "codingExercise",
        "variables": {
            "eid": eid,
            "pid": pid,
            "codecnt": codecnt
        },
        "query": '''
query codingExercise($eid: ID!, $pid: ID, $codecnt: Int!) {
    node(id: $pid) {
        ... on ExercisePack {
            id
            codingExercise(id: $eid) {
                id
                title
                tags
                viewerStatus {
                    passedCount
                    totalCount
                    exerciseStatuses(last: $codecnt) {
                        nodes {
                            ... on CodingExerciseStatus {
                                id
                                scoreRate
                                submission {
                                    id
                                    reports {
                                        key
                                        value
                                    }
                                }
                                solution {
                                    lang 
                                    asset { content }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}'''})
    res = post(url = url, headers = headers, data = data)
    if not res: return False
    return json.loads(res.text)['data']['node']['codingExercise']['viewerStatus']['exerciseStatuses']['nodes']

def _get_exercise_not_from_pack(eid, lang, feedback = 'dict'):
    headers = coding_base_headers.copy()
    data = json.dumps({
        "operationName": "codingExercise",
        "variables": {
            "eid": eid,
            "lang": lang
        },
        "query": '''
query codingExercise($eid: ID!, $lang: Language!) {
    exercise: node(id: $eid) {
        ... on CodingExercise {
            id
            title
            tags
            description { content }
            inputDescription { content }
            outputDescription { content }
            sampleData {
                id
                input { content }
                output { content }
                explanation { content }
            }
            supportedLanguages
            note(lang: $lang) {
                url
                content
            }
        }
    }
}'''})
    res = post(url = url, headers = headers, data = data)
    if not res: return False
    if feedback == 'Response': return res
    res = json.loads(res.text)['data']['exercise']
    ret = {}
    ret['title'] = res['title']
    ret['tags'] = res['tags']
    ret['description-content'] = res['description']['content'].replace("\n\n", '\n')
    ret['inputDescription-content'] = res['inputDescription']['content']
    ret['outputDescription-content'] = res['outputDescription']['content']
    ret['sampleData'] = []
    for x in res['sampleData']:
        toappend = {}
        if x['input'] != None: toappend['input'] = x['input']['content']
        else: toappend['input'] = None
        if x['output'] != None: toappend['output'] = x['output']['content']
        else: toappend['output'] = None
        if x['explanation'] != None: toappend['explanation'] = x['explanation']['content']
        else: toappend['explanation'] = None
        ret['sampleData'].append(toappend)
    ret['supportedLanguages'] = res['supportedLanguages']
    ret['note'] = res['note']
    if feedback == 'dict': return ret
    elif feedback == 'json' or feedback == 'str': return json.dumps(ret)
    else: return None

def _get_exercise_from_pack(eid, pid, lang, feedback = 'dict'):
    headers = coding_base_headers.copy()
    data = json.dumps({
        "operationName": "codingExercise",
        "variables": {
            "eid": eid,
            "pid": pid,
            "lang": lang
        },
        "query": '''
query codingExercise($eid: ID!, $pid: ID, $lang: Language!) {
    pack: node(id: $pid) {
        ... on ExercisePack {
            id
            codingExercise(id: $eid) {
                id
                title
                tags
                description { content }
                inputDescription { content }
                outputDescription { content }
                sampleData {
                    id
                    input { content }
                    output { content }
                    explanation { content }
                }
                supportedLanguages
                note(lang: $lang) {
                    url
                    content
                }
            }
        }
    }
}'''})
    res = post(url = url, headers = headers, data = data)
    if not res: return False
    if feedback == 'Response': return res
    res = json.loads(res.text)['data']['pack']['codingExercise']
    ret = {}
    ret['title'] = res['title']
    ret['tags'] = res['tags']
    ret['description-content'] = res['description']['content'].replace("\n\n", '\n')
    ret['inputDescription-content'] = res['inputDescription']['content']
    ret['outputDescription-content'] = res['outputDescription']['content']
    ret['sampleData'] = []
    for x in res['sampleData']:
        toappend = {}
        if x['input'] != None: toappend['input'] = x['input']['content']
        else: toappend['input'] = None
        if x['output'] != None: toappend['output'] = x['output']['content']
        else: toappend['output'] = None
        if x['explanation'] != None: toappend['explanation'] = x['explanation']['content']
        else: toappend['explanation'] = None
        ret['sampleData'].append(toappend)
    ret['supportedLanguages'] = res['supportedLanguages']
    ret['note'] = res['note']
    if feedback == 'dict': return ret
    elif feedback == 'json' or feedback == 'str': return json.dumps(ret)
    else: return None
