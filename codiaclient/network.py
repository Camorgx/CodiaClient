from .report import report
from .utils import graphql_query_encode as qryenc, passwd_hash, cookie_encrypt, cookie_decrypt
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
    data = qryenc('''{"operationName":null,"variables":{ },"query":"{
  me {
    id
    login
    displayName
    avatarUrl
    defaultEmail
    verified
    __typename
  }
}"}''').format()
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

# def __get_data(eid, pid, codecnt: int = 1):
#     if pid: return ___get_data_from_pack(eid, pid, codecnt)
#     else: return ___get_data_not_from_pack(eid, codecnt)

def get_exercise(eid, pid, lang, feedback = None):
    if pid: return _get_exercise_from_pack(eid, pid, lang, feedback)
    else: return _get_exercise_not_from_pack(eid, lang, feedback)

def get_pack(lastcnt: int = 8):
    headers = coding_base_headers.copy()
    data = qryenc('''{"operationName":"publicExercisePacks","variables":{ },"query":"query publicExercisePacks($before: String) {
    publicExercisePacks(last: {}, before: $before) {
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
}"}''').format(lastcnt)
    headers['content-length'] = str(len(data))
    res = post(url = url, headers = headers, data = data.encode('utf-8'), timeout = 5)
    return json.loads(res.text)['data']['publicExercisePacks']['nodes']

def show_pack(pid):
    headers = coding_base_headers.copy()
    data_pid = pid
    data = qryenc('''{"operationName":"pack","variables":{"pid":"{}"},"query":"query pack($pid: ID!) {
    node(id: $pid) {
        id
        ... on ExercisePack {
            name
            description {
                content
            }
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
}"}''').format(data_pid)
    headers['content-length'] = str(len(data))
    res = post(url = url, headers = headers, data = data.encode('utf-8'), timeout = 5)
    return json.loads(res.text)['data']['node']

def _login(username, passwd):
    headers = login_base_headers.copy()
    data = qryenc('''{"operationName":"login","variables":{"username":"{}","password":"{}"},"query":"mutation login($username: String!, $password: String!) {
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
}"}''').format(username, passwd)
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
    data_eid = eid
    data_lang = lang
    data_pid = pid
    data_solution = solutioncode.replace('\\',r'\\').replace('\t', r'\t').replace('\n',r'\n').replace('\"',r'\"')
    data = qryenc('''{"operationName":null,"variables":{"eid":"{}","pid":"{}","lang":"{}","sol":"{}","a":{"editStat":[]}},"query":"mutation ($eid: ID!, $pid: ID, $lang: Language!, $sol: String!, $a: JSONObject) {
    submit(eid: $eid, pid: $pid, solution: {lang: $lang, asset: {content: $sol}}, additionalInfo: $a) {
        token
        __typename
    }
}"}''').format(data_eid, data_pid, data_lang, data_solution)
    headers['content-length'] = str(len(data))
    return post(url = url, headers = headers, data = data.encode('utf-8'), timeout = 5)

def _submit_not_from_pack(eid, lang, solutioncode):
    headers = coding_base_headers.copy()
    data_eid = eid
    data_lang = lang
    data_solution = solutioncode.replace('\\',r'\\').replace('\t', r'\t').replace('\n',r'\n').replace('\"',r'\"')
    data = qryenc('''{"operationName":null,"variables":{"eid":"{}","lang":"{}","sol":"{}","a":{"editStat":[]}},"query":"mutation ($eid: ID!, $pid: ID, $lang: Language!, $sol: String!, $a: JSONObject) {
    submit(eid: $eid, pid: $pid, solution: {lang: $lang, asset: {content: $sol}}, additionalInfo: $a) {
        token
        __typename
    }
}"}''').format(data_eid, data_lang, data_solution)
    headers['content-length'] = str(len(data))
    return post(url = url, headers = headers, data = data.encode('utf-8'), timeout = 5)

def _get_data_not_from_pack(eid, codecnt: int = 1):
    headers = coding_base_headers.copy()
    data_eid = eid
    data = qryenc('''{"operationName":"codingExercise","variables":{"eid":"{}"},"query":"query codingExercise($eid: ID!) {
    node(id: $eid) {
        ... on CodingExercise {
            viewerStatus {
                exerciseStatuses(last: {}) {
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
                                asset {
                                    content
                                }
                            } 
                        }
                    }
                }
            }
        }
    }
}"}''').format(data_eid, codecnt)
    headers['content-length'] = str(len(data))
    res = post(url = url, headers = headers, data = data.encode('utf-8'), timeout = 5)
    return json.loads(res.text)['data']['node']['viewerStatus']['exerciseStatuses']['nodes']

def _get_data_from_pack(eid, pid, codecnt: int = 1):
    headers = coding_base_headers.copy()
    data_eid = eid
    data_pid = pid
    data = '{{\"operationName\":\"codingExercise\",\"variables\":{{\"eid\":\"{}\",\"pid\":\"{}\"}},\"query\":\"query codingExercise($eid: ID!, $pid: ID) {{\\n node(id: $pid) {{\\n ... on ExercisePack {{\\n id\\n codingExercise(id: $eid) {{\\n id\\n title\\n tags\\n viewerStatus {{\\n passedCount\\n totalCount\\n exerciseStatuses(last: {}) {{\\n nodes {{\\n ... on CodingExerciseStatus {{\\n id\\n scoreRate\\n submission {{\\n id\\n reports {{\\n key\\n value\\n }}\\n}}\\n solution {{\\n lang \\n asset {{content}}}}\\n}}\\n}}\\n}}\\n}}\\n}}\\n viewerStatus {{\\n lastSession {{\\n id\\n codingExercises {{\\n edges {{\\n userStatus {{\\n passedCount\\n totalCount\\n }}\\n node {{\\n id\\n}}\\n}}\\n}}\\n}}\\n}}\\n}}\\n}}\\n}}\\n\"}}'.format(data_eid, data_pid, codecnt)
    headers['content-length'] = str(len(data))
    res = post(url = url, headers = headers, data = data.encode('utf-8'), timeout = 5)
    return json.loads(res.text)['data']['node']['codingExercise']['viewerStatus']['exerciseStatuses']['nodes']

# def ___get_data_not_from_pack(eid, codecnt: int = 1):
#     headers = coding_base_headers.copy()
#     data_eid = eid
#     data = qryenc('''{"operationName":"codingExercise","variables":{"eid":"{}"},"query":"query codingExercise($eid: ID!) {
#     node(id: $eid) {
#         ... on CodingExercise {
#             viewerStatus {
#                 passedCount
#                 totalCount
#                 exerciseStatuses(last: {}) {
#                     nodes {
#                         ... on CodingExerciseStatus {
#                             id
#                             scoreRate
#                             submission {
#                                 id
#                                 reports {
#                                     key
#                                     value
#                                 }
#                             }
#                             solution {
#                                 lang 
#                                 asset {
#                                     content
#                                 }
#                             } 
#                         }
#                     }
#                 }
#             }
#         }
#     }
# }"}''').format(data_eid, codecnt)
#     headers['content-length'] = str(len(data))
#     return post(url = url, headers = headers, data = data.encode('utf-8'), timeout = 5)

# def ___get_data_from_pack(eid, pid, codecnt: int = 1):
#     headers = coding_base_headers.copy()
#     data_eid = eid
#     data_pid = pid
#     data = qryenc('''{"operationName":"codingExercise","variables":{"eid":"{}","pid":"{}"},"query":"query codingExercise($eid: ID!, $pid: ID) {
#     node(id: $pid) {
#         ... on ExercisePack {
#             id
#             codingExercise(id: $eid) {
#                 id
#                 title
#                 tags
#                 viewerStatus {
#                     passedCount
#                     totalCount
#                     exerciseStatuses(last: {}) {
#                         nodes {
#                             ... on CodingExerciseStatus {
#                                 id
#                                 scoreRate
#                                 submission {
#                                     id
#                                     reports {
#                                         key
#                                         value
#                                     }
#                                 }
#                                 solution {
#                                     lang 
#                                     asset {content}
#                                 }
#                             }
#                         }
#                     }
#                 }
#             }
#             viewerStatus {
#                 lastSession {
#                     id
#                     codingExercises {
#                         edges {
#                             userStatus {
#                                 passedCount
#                                 totalCount
#                             }
#                             node {
#                                 id
#                             }
#                         }
#                     }
#                 }
#             }
#         }
#     } 
# }"}''').format(data_eid, data_pid, codecnt)
#     headers['content-length'] = str(len(data))
#     return post(url = url, headers = headers, data = data.encode('utf-8'), timeout = 5)

def _get_exercise_not_from_pack(eid, lang, feedback = None):
    headers = coding_base_headers.copy()
    data_eid = eid
    data_lang = lang
    data = '{{\"operationName\":\"codingExercise\",\"variables\":{{\"eid\":\"{}\",\"lang\":\"{}\",\"fromPack\":false}},\"query\":\"query codingExercise($eid: ID!, $pid: ID, $fromPack: Boolean!, $lang: Language!) {{\\n  exercise: node(id: $eid) @skip(if: $fromPack) {{\\n    ... on CodingExercise {{\\n      id\\n      title\\n      tags\\n      description {{\\n        content\\n        __typename\\n      }}\\n      shortDesc\\n      inputDescription {{\\n        content\\n        __typename\\n      }}\\n      outputDescription {{\\n        content\\n        __typename\\n      }}\\n      sampleData {{\\n        id\\n        input {{\\n          content\\n          __typename\\n        }}\\n        output {{\\n          content\\n          __typename\\n        }}\\n        explanation {{\\n          content\\n          __typename\\n        }}\\n        __typename\\n      }}\\n      supportedLanguages\\n      note(lang: $lang) {{\\n        url\\n        content\\n        __typename\\n      }}\\n      codeSnippet(lang: $lang) {{\\n        url\\n        content\\n        __typename\\n      }}\\n      createdAt\\n      updatedAt\\n      owner {{\\n        id\\n        login\\n        displayName\\n        __typename\\n      }}\\n      __typename\\n    }}\\n    __typename\\n  }}\\n  pack: node(id: $pid) @include(if: $fromPack) {{\\n    ... on ExercisePack {{\\n      id\\n      codingExercise(id: $eid) {{\\n        id\\n        title\\n        tags\\n        description {{\\n          content\\n          __typename\\n        }}\\n        shortDesc\\n        inputDescription {{\\n          content\\n          __typename\\n        }}\\n        outputDescription {{\\n          content\\n          __typename\\n        }}\\n        sampleData {{\\n          id\\n          input {{\\n            content\\n            __typename\\n          }}\\n          output {{\\n            content\\n            __typename\\n          }}\\n          explanation {{\\n            content\\n            __typename\\n          }}\\n          __typename\\n        }}\\n        supportedLanguages\\n        note(lang: $lang) {{\\n          url\\n          content\\n          __typename\\n        }}\\n        codeSnippet(lang: $lang) {{\\n          url\\n          content\\n          __typename\\n        }}\\n        createdAt\\n        updatedAt\\n        owner {{\\n          id\\n          login\\n          displayName\\n          __typename\\n        }}\\n        __typename\\n      }}\\n      __typename\\n    }}\\n    __typename\\n  }}\\n}}\\n\"}}'.format(data_eid, data_lang)
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
    data_eid = eid
    data_pid = pid
    data_lang = lang
    data = '{{\"operationName\":\"codingExercise\",\"variables\":{{\"eid\":\"{}\",\"pid\":\"{}\",\"lang\":\"{}\",\"fromPack\":true}},\"query\":\"query codingExercise($eid: ID!, $pid: ID, $fromPack: Boolean!, $lang: Language!) {{\\n  exercise: node(id: $eid) @skip(if: $fromPack) {{\\n    ... on CodingExercise {{\\n      id\\n      title\\n      tags\\n      description {{\\n        content\\n        __typename\\n      }}\\n      shortDesc\\n      inputDescription {{\\n        content\\n        __typename\\n      }}\\n      outputDescription {{\\n        content\\n        __typename\\n      }}\\n      sampleData {{\\n        id\\n        input {{\\n          content\\n          __typename\\n        }}\\n        output {{\\n          content\\n          __typename\\n        }}\\n        explanation {{\\n          content\\n          __typename\\n        }}\\n        __typename\\n      }}\\n      supportedLanguages\\n      note(lang: $lang) {{\\n        url\\n        content\\n        __typename\\n      }}\\n      codeSnippet(lang: $lang) {{\\n        url\\n        content\\n        __typename\\n      }}\\n      createdAt\\n      updatedAt\\n      owner {{\\n        id\\n        login\\n        displayName\\n        __typename\\n      }}\\n      __typename\\n    }}\\n    __typename\\n  }}\\n  pack: node(id: $pid) @include(if: $fromPack) {{\\n    ... on ExercisePack {{\\n      id\\n      codingExercise(id: $eid) {{\\n        id\\n        title\\n        tags\\n        description {{\\n          content\\n          __typename\\n        }}\\n        shortDesc\\n        inputDescription {{\\n          content\\n          __typename\\n        }}\\n        outputDescription {{\\n          content\\n          __typename\\n        }}\\n        sampleData {{\\n          id\\n          input {{\\n            content\\n            __typename\\n          }}\\n          output {{\\n            content\\n            __typename\\n          }}\\n          explanation {{\\n            content\\n            __typename\\n          }}\\n          __typename\\n        }}\\n        supportedLanguages\\n        note(lang: $lang) {{\\n          url\\n          content\\n          __typename\\n        }}\\n        codeSnippet(lang: $lang) {{\\n          url\\n          content\\n          __typename\\n        }}\\n        createdAt\\n        updatedAt\\n        owner {{\\n          id\\n          login\\n          displayName\\n          __typename\\n        }}\\n        __typename\\n      }}\\n      __typename\\n    }}\\n    __typename\\n  }}\\n}}\\n\"}}'.format(data_eid, data_pid, data_lang)
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