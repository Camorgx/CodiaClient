from .report import report
from .utils import passwd_hash, cookie_encrypt

variables = {
    'cacheOn': True,
    'logindic': {}
}

def cache_username_passwd_cookie(username, passwd, cookie, file = './cache.passwd.conf'):
    if not variables['cacheOn']:
        report("Invalid reference of function 'cache_username_passwd_cookie'.", 1)
        return False
    report("Caching cookie.")
    variables['logindic'][username] = {'passwd': passwd_hash(passwd), 'cookie': cookie_encrypt(cookie, passwd)}
    try:
        import toml
        with open(file, 'w', encoding = 'utf-8') as f: toml.dump({'logindic': variables['logindic']}, f)
        report("Cache complete.")
    except: report('Cache failed.', 1)

def cache_load(file = './cache.passwd.conf'):
    try:
        import toml
        with open(file, encoding = 'utf-8') as f: config = toml.load(f)
        if 'logindic' in config: variables['logindic'] = config['logindic']
    except ImportError as e:
        report(e, 1)
        variables['cacheOn'] = False
    except:
        pass
