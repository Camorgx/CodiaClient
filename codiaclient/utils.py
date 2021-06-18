from .report import report

class AliasesDict(dict):
    aliaseslist = {}
    def __init__(self, dict, aliaseslist = {}):
        self.aliaseslist = aliaseslist
        super().__init__(dict)
    def __getitem__(self, attr):
        if attr in self.aliaseslist: return super().__getitem__(self.aliaseslist[attr])
        else: return super().__getitem__(attr)
    def __setitem__(self, key, value):
        if key in self.aliaseslist: return super().__setitem__(self.aliaseslist[key], value)
        else: return super().__setitem__(key, value)

def passwd_hash(passwd):
    try:
        from hashlib import new
        if type(passwd) == int: passwd = str(passwd)
        if type(passwd) == str: passwd = passwd.encode()
        return new('sha256', passwd).hexdigest()
    except ImportError: raise
    except:
        report("Password hashing failed, which may cause the plaintext to be cached.", 1)
        return passwd

import base64
from Crypto.Cipher import AES

def add_to_16(value):
    while len(value) % 16 != 0: value += '\x00'
    return str.encode(value)

def cookie_encrypt(cookie, passwd):
    return str(base64.encodebytes(AES.new(add_to_16(passwd), AES.MODE_ECB).encrypt(add_to_16(cookie))), encoding = 'utf-8')

def cookie_decrypt(_cookie, passwd):
    return str(AES.new(add_to_16(passwd), AES.MODE_ECB).decrypt(base64.decodebytes(_cookie.encode(encoding = 'utf-8'))), encoding = 'utf-8').replace('\x00', '')
