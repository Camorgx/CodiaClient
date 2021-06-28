import json
import zlib
from base64 import b64encode, b64decode

from .report import report
from .utils import passwd_hash, cookie_encrypt

variables = {
    'cache_on': True,
    'logindic': {},
    'tmpPath': ""
}

from os import environ, path, makedirs
variables['tmpPath'] = path.join(environ['temp'] ,'codiaclient')
if not path.exists(variables['tmpPath']):
    makedirs(variables['tmpPath'])
variables['tmpPath'] = path.join(variables['tmpPath'], ".cache")

def cache_for_login(userdic, passwd, cookie=None, passwd_store_on=0):
    file = variables['tmpPath']
    if not variables['cache_on']:
        report("Invalid reference of function 'cache_username_passwd_cookie'.", 1)
        return False
    report("Caching cookie.")
    username = None
    useremail = None
    encrypted_cookie = None
    if 'login' in userdic: username = userdic['login']
    if 'defaultEmail' in userdic: useremail = userdic['defaultEmail']
    if 'cookie' in userdic and not cookie: cookie = userdic['cookie']
    if cookie: encrypted_cookie = cookie_encrypt(cookie, passwd)

    hashed_passwd = passwd_hash(passwd)
    if passwd_store_on == 2:
        stored_passwd = passwd
    else:
        stored_passwd = None
    variables['logindic'][username] = variables['logindic'][useremail] = {
        'username': username,
        'email': useremail,
        'passwd': stored_passwd,
        'hashed_passwd': hashed_passwd,
        'cookie': encrypted_cookie,
        'passwd_store_on': passwd_store_on
    }
    try:
        dic_str = json.dumps({'logindic': variables['logindic']})
        dic_b64 = b64encode(dic_str.encode('utf-8'))
        dic_ziped = zlib.compress(dic_b64)
        with open(file, 'wb') as f:
            f.write(dic_ziped)
        report("Cache complete.")
    except:
        report('Cache failed.', 1)
        raise


def update_cache_for_login(username, passwd, passwd_store_on=0):
    file = variables['tmpPath']
    userdic = variables['logindic'][username]
    username = userdic['username']
    useremail = userdic['email']
    encrypted_cookie = userdic['cookie']

    hashed_passwd = passwd_hash(passwd)
    if passwd_store_on == 2:
        stored_passwd = passwd
    else:
        stored_passwd = None
    variables['logindic'][username] = variables['logindic'][useremail] = {
        'username': username,
        'email': useremail,
        'passwd': stored_passwd,
        'hashed_passwd': hashed_passwd,
        'cookie': encrypted_cookie,
        'passwd_store_on': passwd_store_on
    }
    try:
        dic_str = json.dumps({'logindic': variables['logindic']})
        dic_b64 = b64encode(dic_str.encode('utf-8'))
        dic_ziped = zlib.compress(dic_b64)
        with open(file, 'wb') as f:
            f.write(dic_ziped)
        report("Cache complete.")
    except:
        report('Cache failed.', 1)
        raise


def cache_load():
    file = variables['tmpPath']
    if not variables['cache_on']:
        report("Invalid reference of function 'cache_load'.", 1)
        return False
    try:
        with open(file, 'rb') as f:
            dic_ziped = f.read()
        dic_b64 = zlib.decompress(dic_ziped)
        dic_str = b64decode(dic_b64).decode('utf-8')
        config = json.loads(dic_str)
        if 'logindic' in config: variables['logindic'] = config['logindic']
    except (zlib.error, UnicodeDecodeError, json.decoder.JSONDecodeError):
        report('Cache load failed.', 1)
    except FileNotFoundError:
        pass
