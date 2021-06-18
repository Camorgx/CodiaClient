from .report import report
from .utils import passwd_hash, cookie_encrypt, cookie_decrypt
from .cachectrl import variables as cache_var, cache_for_login as cache
import json
variables = {
    'register': False,
    'me': {
        'username': None,
        'nickname': None,
        'email': None,
        'verified': None,
    },
}
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
    headers['content-length'] = str(len(data))
    if type(data) == str: data = data.encode('utf-8')
    if type(data) != bytes:
        report('post: Variable `data` type error. (should be `str` or `bytes`, not `{}`)'.format(type(data)), 1)
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

def client_login(args = None, username = None, password = None, cookie = None):
    if args:
        username = args.username
        password = args.passwd
        cookie = args.cookie
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
                if not password: report("Empty password.", 3)
            else: exit()

    if variables['register']:
        register(username, password)

    if username and password:
        if cookie:
            report("Using the input cookie.")
            coding_base_headers['cookie'] = cookie
            displayName = logined()
            if displayName: report('Login succeeded.({})'.format(displayName))
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
                if displayName: report('Login succeeded.({})'.format(displayName))
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

def logined(reportUnverified: bool = True):
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
    res_data = json.loads(res.text)
    if 'errors' in res_data: return False
    else:
        if reportUnverified and not res_data['data']['me']['verified']:
            report("The user has not verified.", 1)
        if not res_data['data']['me']['displayName']:
            res_data['data']['me']['displayName'] = "UNDEFINED"
        variables['me']['username'] = res_data['data']['me']['login']
        variables['me']['nickname'] = res_data['data']['me']['displayName']
        variables['me']['email'] = res_data['data']['me']['defaultEmail']
        variables['me']['verified'] = res_data['data']['me']['verified']
        return res_data['data']['me']['displayName']

def login(username, passwd):
    report('Try login.')
    res = _login(username, passwd)
    if not res:
        report('Login failed.', 3)
        return False
    else:
        report('Login succeeded.({})'.format(res['displayName']))
        return True

def register(username, passwd, email = None):
    headers = login_base_headers.copy()
    if not email: email = input("Input your email:")
    data = {
        "operationName": "signup",
        "variables": {
            "login": username,
            "password": passwd,
            "email": email,
            "displayName": username
        },
        "query": r'''
mutation signup($login: String!, $password: String!, $email: String!) {
  signup(login: $login, password: $password, email: $email) {
    user {
      id
      login
      displayName
      defaultEmail
      avatarUrl
      verified
    }
  }
}'''
    }
    data = json.dumps(data)
    res = post(url = url, headers = headers, data = data)
    if not res: return False
    res_data = json.loads(res.text)
    if 'errors' in res_data:
        report("register: " + res_data['errors'][0]['message'] + '.', 2)
        return False
    return res_data['data']['signup']

def change_password(vercode = None, passwd = None, passwordconfirm = None):
    import getpass
    headers = login_base_headers.copy()
    if not vercode:
        identifier, res = _acquire_verification()
        if not res:
            report("Verification acquiring error.", 3)
            return False
        elif res['status'] == "SUCCESS": report("Code sent successfully.")
        elif res['status'] == "SKIP": pass
        else:
            if 'message' in res: report('change_password: Acquiring status error. ({})'.format(res['message']), 3)
            else: report("change_password: Acquiring status error.", 3)
            return False
        try: vercode = getpass.getpass('Enter received code:')
        except KeyboardInterrupt: exit()
    if not vercode or len(vercode) != 6:
        report('Invalid code.', 3)
        return False
    else:
        if not passwd:
            try: passwd = getpass.getpass('Input your new password:')
            except KeyboardInterrupt: exit()
        if not passwd or len(passwd) < 6:
            report('Invalid password.', 3)
            return False
        else:
            if not passwordconfirm:
                passwordconfirm = getpass.getpass('Confirm your new password:')
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
                    "newPassword": passwd,
                    "newPasswordConfirm": passwordconfirm,
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
    return passwd

def _acquire_verification(identifier = None):
    headers = login_base_headers.copy()
    if not identifier: identifier = input("Input your email/phone:")
    if len(identifier.split()) == 2:
        identifier = identifier.split()
        report("Code sending skipped.(email/phone:{})".format(identifier[0]))
        return identifier[0], {"status": identifier[1].upper()}
    try: int(identifier)
    except:
        if '@' in identifier:
            id_type = "EMAIL"
        else:
            report("Identifier error.", 3)
            return identifier, False
    else:
        id_type = "PHONE"
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
    res_data = json.loads(res.text)
    if 'errors' in res_data:
        report("_acquire_verification: " + res_data['errors'][0]['message'] + '.', 2)
        return None, False
    return identifier, res_data['data']['acquireVerification']

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
        report('get_pack: Variable `lastcnt` type error. (should be `int`, not `{}`)'.format(type(lastcnt)), 1)
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
            viewerStatus {
                ongoing
            }
        }
    }
}'''})
    res = post(url = url, headers = headers, data = data)
    if not res: return False
    return json.loads(res.text)['data']['node']

def start_pack(pid):
    if show_pack(pid)['viewerStatus']['ongoing']:
        report("This pack is already ongoing.", 1)
        return None
    headers = coding_base_headers.copy()
    data = json.dumps({
        "operationName": "startSession",
        "variables": {
            "pid": pid
        },
        "query": r'''
mutation startSession($pid: ID!, $code: String) {
  startSession(exercisePackId: $pid, code: $code) {
    id
    codingExercises {
      passedCount
      totalCount
      edges {
        node { id }
        userStatus {
          attempted
          passed
        }
      }
    }
    pack {
      id
      description { content }
      codingExercises {
        nodes {
          id
          title
        }
      }
      viewerStatus {
        ongoing
        due
      }
    }
  }
}'''})
    res = post(url = url, headers = headers, data = data)
    if not res: return False
    return json.loads(res.text)['data']['startSession']

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
    if cache_var['cacheOn']: cache(res_data['data']['login']['user'], passwd, coding_base_headers['cookie'])
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
        report('_get_data_not_from_pack: Variable `codecnt` type error. (should be `int`, not `{}`)'.format(type(codecnt)), 1)
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
        report('_get_data_from_pack: Variable `codecnt` type error. (should be `int`, not `{}`)'.format(type(codecnt)), 1)
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
            codeSnippet(lang: $lang) {
                url
                content
            }
            viewerStatus {
                passedCount
                totalCount
            }
        }
    }
}'''})
    res = post(url = url, headers = headers, data = data)
    if not res: return False
    if feedback == 'Response': return res
    res_data = json.loads(res.text)['data']['exercise']
    res_dic = {}
    res_dic['title'] = res_data['title']
    res_dic['tags'] = res_data['tags']
    res_dic['description-content'] = res_data['description']['content'].replace("\n\n", '\n')
    res_dic['inputDescription-content'] = res_data['inputDescription']['content']
    res_dic['outputDescription-content'] = res_data['outputDescription']['content']
    res_dic['sampleData'] = []
    for x in res_data['sampleData']:
        toappend = {}
        if x['input'] != None: toappend['input'] = x['input']['content']
        else: toappend['input'] = None
        if x['output'] != None: toappend['output'] = x['output']['content']
        else: toappend['output'] = None
        if x['explanation'] != None: toappend['explanation'] = x['explanation']['content']
        else: toappend['explanation'] = None
        res_dic['sampleData'].append(toappend)
    res_dic['supportedLanguages'] = res_data['supportedLanguages']
    if res_data['note'] != None: res_dic['note'] = res_data['note']['content']
    else: res_dic['note'] = None
    if res_data['codeSnippet'] != None: res_dic['codeSnippet'] = res_data['codeSnippet']['content']
    else: res_dic['codeSnippet'] = None
    res_dic['viewerStatus'] = res_data['viewerStatus']
    if feedback == 'dict': return res_dic
    elif feedback == 'json' or feedback == 'str': return json.dumps(res_dic)
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
                codeSnippet(lang: $lang) {
                    url
                    content
                }
                viewerStatus {
                    passedCount
                    totalCount
                }
            }
        }
    }
}'''})
    res = post(url = url, headers = headers, data = data)
    if not res: return False
    if feedback == 'Response': return res
    res_data = json.loads(res.text)['data']['pack']['codingExercise']
    res_dic = {}
    res_dic['title'] = res_data['title']
    res_dic['tags'] = res_data['tags']
    res_dic['description-content'] = res_data['description']['content'].replace("\n\n", '\n')
    res_dic['inputDescription-content'] = res_data['inputDescription']['content']
    res_dic['outputDescription-content'] = res_data['outputDescription']['content']
    res_dic['sampleData'] = []
    for x in res_data['sampleData']:
        toappend = {}
        if x['input'] != None: toappend['input'] = x['input']['content']
        else: toappend['input'] = None
        if x['output'] != None: toappend['output'] = x['output']['content']
        else: toappend['output'] = None
        if x['explanation'] != None: toappend['explanation'] = x['explanation']['content']
        else: toappend['explanation'] = None
        res_dic['sampleData'].append(toappend)
    res_dic['supportedLanguages'] = res_data['supportedLanguages']
    if res_data['note'] != None: res_dic['note'] = res_data['note']['content']
    else: res_dic['note'] = None
    if res_data['codeSnippet'] != None: res_dic['codeSnippet'] = res_data['codeSnippet']['content']
    else: res_dic['codeSnippet'] = None
    res_dic['viewerStatus'] = res_data['viewerStatus']
    if feedback == 'dict': return res_dic
    elif feedback == 'json' or feedback == 'str': return json.dumps(res_dic)
    else: return None
