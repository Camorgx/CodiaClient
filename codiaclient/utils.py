from .report import report

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

def graphql_query_encode(str):
    return str.replace(r'{', r'{{').replace(r'}', r'}}').replace(r'{{}}', r'{}').replace('    ', '  ').replace('\n', r'\n')


import base64
from Crypto.Cipher import AES

def add_to_16(value):
    while len(value) % 16 != 0: value += '\x00'
    return str.encode(value)

def cookie_encrypt(cookie, passwd):
    return str(base64.encodebytes(AES.new(add_to_16(passwd), AES.MODE_ECB).encrypt(add_to_16(cookie))), encoding = 'utf-8')

def cookie_decrypt(_cookie, passwd):
    return str(AES.new(add_to_16(passwd), AES.MODE_ECB).decrypt(base64.decodebytes(_cookie.encode(encoding = 'utf-8'))), encoding = 'utf-8').replace('\x00', '')
