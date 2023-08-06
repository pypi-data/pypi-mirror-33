# coding: utf-8

import random
import base64
from Crypto.Cipher import AES

BS = AES.block_size


def pad(s):
    return s + (BS - len(s) % BS) * chr(BS - len(s) % BS)


def unpad(s):
    return s[0: -ord(s[-1])]


def encrypt(plain_text, key):
    cipher = AES.new(key)
    if not isinstance(plain_text, (basestring, int)):
        return plain_text
    if isinstance(plain_text, unicode):
        plain_text = plain_text.encode('utf-8')
    else:
        plain_text = str(plain_text)
    encrypted = cipher.encrypt(pad(plain_text))
    return base64.b64encode(encrypted)


def decrypt(cipher_text, key):
    cipher = AES.new(key)
    if not (cipher_text and isinstance(cipher_text, (basestring, int))):
        return cipher_text
    if isinstance(cipher_text, unicode):
        cipher_text = cipher_text.encode('utf-8')
    else:
        cipher_text = str(cipher_text)
    decrypted = base64.b64decode(cipher_text)
    result = unpad(cipher.decrypt(decrypted))
    return result


def generate_aes_key(length=32):
    seed = 'abcdefghigklmnopqrstuvwxyzABCDEFGHIGKLMNOPQRSTUVWXYZ=-+_)(*&^%$#@~!1234567890;\'":<>?/.,'  # noqa
    return ''.join(random.choice(seed) for _ in xrange(length))
