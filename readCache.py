import zlib
import json
from base64 import b64encode,b64decode
from codiaclient.report import report
variables = {'cache_on': True}
def cache_load(file = './codiaclient.cache'):
    if not variables['cache_on']:
        report("Invalid reference of function 'cache_load'.", 1)
        return False
    try:
        with open(file, 'rb') as f: dic_ziped = f.read()
        dic_b64 = zlib.decompress(dic_ziped)
        dic_str = b64decode(dic_b64).decode('utf-8')
        config = json.loads(dic_str)
        if 'logindic' in config: variables['logindic'] = config['logindic']
    except (zlib.error, UnicodeDecodeError, json.decoder.JSONDecodeError):
        report('Cache load failed.', 1)
    except FileNotFoundError:
        pass
cache_load()
print(json.dumps(variables, indent = 2))
input('Press any key to continue...')