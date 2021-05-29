from .report import report
from .utils import passwd_hash, cookie_encrypt

import zlib
from base64 import b64encode, b64decode
import json

variables = {
    'cacheOn': True,
    'logindic': {}
}

def cache_username_passwd_cookie(userdic, passwd, cookie, file = './codiaclient.cache'):
    if not variables['cacheOn']:
        report("Invalid reference of function 'cache_username_passwd_cookie'.", 1)
        return False
    report("Caching cookie.")
    username = userdic['login']
    useremail = userdic['defaultEmail']
    variables['logindic'][username] = {'username': username, 'email': useremail, 'passwd': passwd_hash(passwd), 'cookie': cookie_encrypt(cookie, passwd)}
    variables['logindic'][useremail] = {'username': username, 'email': useremail, 'passwd': passwd_hash(passwd), 'cookie': cookie_encrypt(cookie, passwd)}
    try:
        dic_str = json.dumps({'logindic': variables['logindic']})
        dic_b64 = b64encode(dic_str.encode('utf-8'))
        dic_ziped = zlib.compress(dic_b64)
        with open(file, 'wb') as f: f.write(dic_ziped)
        report("Cache complete.")
    except:
        report('Cache failed.', 1)
        raise

def cache_load(file = './codiaclient.cache'):
    if not variables['cacheOn']:
        report("Invalid reference of function 'cache_load'.", 1)
        return False
    try:
        with open(file, 'rb') as f: dic_ziped = f.read()
        dic_b64 = zlib.decompress(dic_ziped)
        dic_str = b64decode(dic_b64).decode('utf-8')
        config = json.loads(dic_str)
        if 'logindic' in config: variables['logindic'] = config['logindic']
    except (zlib.error, UnicodeDecodeError, json.decoder.JSONDecodeError):
        report('Cache loading failed.', 1)
    except FileNotFoundError:
        pass
