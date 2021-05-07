from .report import report
from .utils import passwd_hash, cookie_encrypt, cookie_decrypt
from .cachectrl import variables as cache_var, cache_username_passwd_cookie as cache
from requests import post
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
    'referer': 'https://code.bdaa.pro/exercise/ck6su6crv001947mgwgyw1vpl/coding',
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

def client_login(username, password, cookie = None):
    if not username and not cookie:
        report('No username or cookie specified.', 3)

    if username and not cookie and not password:
        import getpass
        try: password = getpass.getpass('Enter password:')
        except KeyboardInterrupt: exit()

    if username and password:
        if cookie:
            report("Using the input cookie.")
            coding_base_headers['cookie'] = cookie
            if logined():
                report('Login succeeded.')
                if cache_var['cacheOn']:
                    if username in cache_var['logindic']:
                        report('We have cached your cookie. Do you want to cover it? [Y/n]', end = '')
                        choice = input()
                        if choice == 'n' or choice == 'N': pass
                        elif choice == 'y' or choice == 'Y':
                            cache(username, password, cookie)
                        else:
                            report('Received bad parameter, executing the default operation.', 1)
                            cache(username, password, cookie)
                    else: cache(username, password, cookie)
            else:
                report('Invalid cookie input.', 1)
                if cache_var['cacheOn'] and username in cache_var['logindic'] and cache_var['logindic'][username]['passwd'] == passwd_hash(password):
                    coding_base_headers['cookie'] = cookie_decrypt(cache_var['logindic'][username]['cookie'], password)
                    report("Using cached cookie.")
                    if logined(): report('Login succeeded.')
                    else:
                        report('Invalid cached cookie.', 1)
                        login(username, password)
                else: login(username, password)
        else: # no cookie input
            if cache_var['cacheOn'] and username in cache_var['logindic'] and cache_var['logindic'][username]['passwd'] == passwd_hash(password):
                coding_base_headers['cookie'] = cookie_decrypt(cache_var['logindic'][username]['cookie'], password)
                report("Using cached cookie.")
                if logined(): report("Login succeeded.")
                else:
                    report('Invalid cached cookie.', 1)
                    login(username, password)
            else: login(username, password)
    elif cookie:
        report("Using the input cookie.")
        coding_base_headers['cookie'] = cookie
        if logined(): report('Login succeeded.')
        else: report('Invalid cookie input.', 3)

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
        __typename
    }
}''',
    })
    headers['content-length'] = str(len(data))
    res = json.loads(post(url = url, headers = headers, data = data.encode('utf-8'), timeout = 5).text)
    if 'errors' in res: return False
    else:
        try: return res['data']['me']['displayName']
        except: return True

def login(username, passwd):
    report('Try login.')
    _login(username, passwd)
    if not logined():
        report('Login failed.', 3)
        return False
    else:
        report('Login succeeded.')
        if cache_var['cacheOn']: cache(username, passwd, coding_base_headers['cookie'])
        return True

def submit(eid, pid, lang, solutioncode):
    if pid: return _submit_from_pack(eid, pid, lang, solutioncode)
    else: return _submit_not_from_pack(eid, lang, solutioncode)

def get_data(eid, pid, codecnt: int = 1):
    if pid: return _get_data_from_pack(eid, pid, codecnt)
    else: return _get_data_not_from_pack(eid, codecnt)

def get_exercise(eid, pid, lang, feedback = None):
    if pid: return _get_exercise_from_pack(eid, pid, lang, feedback)
    else: return _get_exercise_not_from_pack(eid, lang, feedback)

def get_pack(lastcnt: int = 8):
    headers = coding_base_headers.copy()
    data = json.dumps({
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
    })
    headers['content-length'] = str(len(data))
    res = post(url = url, headers = headers, data = data.encode('utf-8'), timeout = 5)
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
    headers['content-length'] = str(len(data))
    res = post(url = url, headers = headers, data = data.encode('utf-8'), timeout = 5)
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
            __typename
        }
        __typename
    }
}'''})
    
    headers['content-length'] = str(len(data))
    res = post(url = url, headers = headers, data = data.encode('utf-8'), timeout = 5)
    from re import search
    try:
        coding_base_headers['cookie'] = search(r'token=(.*?);', res.headers['Set-Cookie']).group().replace(';', '')
        return res
    except:
        return False

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
        __typename
    }
}'''})
    headers['content-length'] = str(len(data))
    return post(url = url, headers = headers, data = data.encode('utf-8'), timeout = 5)

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
        __typename
    }
}'''})
    headers['content-length'] = str(len(data))
    return post(url = url, headers = headers, data = data.encode('utf-8'), timeout = 5)

def _get_data_not_from_pack(eid, codecnt: int = 1):
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
    headers['content-length'] = str(len(data))
    res = post(url = url, headers = headers, data = data.encode('utf-8'), timeout = 5)
    return json.loads(res.text)['data']['node']['viewerStatus']['exerciseStatuses']['nodes']

def _get_data_from_pack(eid, pid, codecnt: int = 1):
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
    headers['content-length'] = str(len(data))
    res = post(url = url, headers = headers, data = data.encode('utf-8'), timeout = 5)
    return json.loads(res.text)['data']['node']['codingExercise']['viewerStatus']['exerciseStatuses']['nodes']

def _get_exercise_not_from_pack(eid, lang, feedback = None):
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
    headers['content-length'] = str(len(data))
    res = post(url = url, headers = headers, data = data.encode('utf-8'), timeout = 5)
    if feedback == 'Response': return res
    if feedback == 'json' or feedback == 'str': return res.text
    if feedback == 'dict': return json.loads(res.text)
    res = json.loads(res.text)['data']['exercise']
    print('title:', res['title'])
    print('tags:', res['tags'])
    print('description-content:', res['description']['content'].replace("\n\n", '\n'))
    print('inputDescription-content:', res['inputDescription']['content'])
    print('outputDescription-content:', res['outputDescription']['content'])
    print('')
    cnt_sampleData = 0
    for x in res['sampleData']:
        print('sampleData#{}:'.format(cnt_sampleData))
        cnt_sampleData += 1
        print('input:', x['input']['content'])
        print('output:', x['output']['content'])
        try: print('explanation:', x['explanation']['content'])
        except: pass
        print('')
    print('supportedLanguages:', res['supportedLanguages'])
    print('note:', res['note'])

def _get_exercise_from_pack(eid, pid, lang, feedback = None):
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
    headers['content-length'] = str(len(data))
    res = post(url = url, headers = headers, data = data.encode('utf-8'), timeout = 5)
    if feedback == 'Response': return res
    if feedback == 'json' or feedback == 'str': return res.text
    if feedback == 'dict': return json.loads(res.text)
    res = json.loads(res.text)['data']['pack']['codingExercise']
    print('title:', res['title'])
    print('tags:', res['tags'])
    print('description-content:', res['description']['content'].replace("\n\n", '\n'))
    print('inputDescription-content:', res['inputDescription']['content'])
    print('outputDescription-content:', res['outputDescription']['content'])
    print('')
    cnt_sampleData = 0
    for x in res['sampleData']:
        print('sampleData#{}:'.format(cnt_sampleData))
        cnt_sampleData += 1
        print('input:', x['input']['content'])
        print('output:', x['output']['content'])
        try: print('explanation:', x['explanation']['content'])
        except: pass
        print('')
    print('supportedLanguages:', res['supportedLanguages'])
    print('note:', res['note'])
