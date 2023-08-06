#!/usr/bin/env python

from __future__ import unicode_literals

import unittest
import os
import logging
import hmac
import hashlib
import codecs

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

from crypto_cookie.encoding import Encoder
from crypto_cookie.encryption import Encryption
from crypto_cookie.auth_tkt import SecureCookie

log = logging.getLogger(__name__)


class EncryptionTestCase(unittest.TestCase):
                
    def test01_encrypt_and_decrypt(self):
        backend = default_backend()
        key = os.urandom(32)
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
        encryptor = cipher.encryptor()
        ct = encryptor.update(b"a secret message") + encryptor.finalize()
        decryptor = cipher.decryptor()
        log.info("test01_encrypt_and_decrypt: %r", 
                 decryptor.update(ct) + decryptor.finalize())
 
    def test02_encrypt_and_decrypt(self):
        backend = default_backend()
        key = os.urandom(32)
        iv = os.urandom(16)

        encryption_cipher = Cipher(algorithms.AES(key), modes.CBC(iv), 
                                   backend=backend)
        encryptor = encryption_cipher.encryptor()
        
        msg = b"a secret message"
        ct = encryptor.update(msg) + encryptor.finalize()

        decryption_cipher = Cipher(algorithms.AES(key), modes.CBC(iv), 
                                   backend=backend)
        decryptor = decryption_cipher.decryptor()
        log.info("test02_encrypt_and_decrypt: %r", 
                 decryptor.update(ct) + decryptor.finalize())
        
    def test03_encryption_class(self):
        msg = '4712cf0cf2f59ecd8b454e5ad1b213ea559fb98dpjkersha!'
        key = os.urandom(32)
        
        cipher_text, iv = Encryption().encrypt(msg, key)
        
        decr_msg = Encryption().decrypt(cipher_text, key, iv)
    
        self.assertEqual(msg, decr_msg, 'Ecnrypted and decrypted messages are '
                         'not the same')
            
        log.info("test03_encryption_class: %r", decr_msg)
    
                 
class SignatureTestCase(unittest.TestCase):

    def test01_hmac_digest(self):
        key = os.urandom(32)
        
        signature = hmac.new(key, b"a secret message", hashlib.sha256)
        hex_digest = signature.hexdigest()
        
        digest = signature.digest()
        
        encoded_digest = codecs.encode(digest, 'hex').decode()
        self.assertEqual(encoded_digest, hex_digest,
                         "Hex digests aren't equal")
        
        log.info("Digest is %r", digest)


class EncoderTestCase(unittest.TestCase):        
    def test01_encode_and_decode_msg(self):
        key = os.urandom(32)
        encoded_msg = Encoder().encode_msg(b'a secret message', key)
        
        log.info('encoded message: %r', encoded_msg)
        
        msg = Encoder().decode_msg(encoded_msg, key)
        
        log.info('decoded message: %r', msg)

    def test02_encode_and_decode_msg_with_base64_encoding(self):
        key = os.urandom(32)
        encoded_msg = Encoder(encoding='base64').encode_msg(b'a secret message', 
                                                            key)
        
        log.info('encoded message: %r', encoded_msg)
        
        msg = Encoder(encoding='base64').decode_msg(encoded_msg, key)
        
        log.info('decoded message: %r', msg)
        

class SecureCookieTestCase(unittest.TestCase):
    def test01_create_cookie(self):
        secret = os.urandom(32)
        
        cookie = SecureCookie(secret, 'pjk', '127.0.0.1')
        cookie_val = cookie.cookie_value()
        
        log.info('Cookie value: %r', cookie_val)
        
    def test02_check_cookie(self):
        secret = os.urandom(32)
        
        cookie = SecureCookie(secret, 'pjk', '127.0.0.1')
        cookie_val = cookie.cookie_value()

        session = {
            'authkit.cookie.user': None,
            'authkit.cookie.user_data': None
        }
        
        ticket = SecureCookie.parse_ticket(secret, cookie_val, '127.0.0.1', 
                                           session)
        
        self.assertEqual('pjk', ticket[1], 'Error parsing user id')
        
        log.info('ticket: %r', ticket)
    
    def test03_cookie_with_data(self):
        secret = os.urandom(32)
        
        cookie = SecureCookie(secret, 'pjk', '127.0.0.1',
                              tokens=('token1', 'token2'),
                              user_data='user_data')
        cookie_val = cookie.cookie_value()
        
        _, _, tokens, user_data = SecureCookie.parse_ticket(secret, cookie_val,
                                                            None, None)
        
        self.assertEqual(['token1', 'token2'], tokens,
                         'Failed to match tokens')
        self.assertEqual('user_data', user_data,
                         'Failed to match user_data')
        
        log.info('Cookie value: %r', cookie_val)
    
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
