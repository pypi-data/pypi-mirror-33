# Filename: security.py

from base64 import encodebytes, decodebytes
from Crypto import Random
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from io import BytesIO


class CgSecurity():
    @staticmethod
    def MakeToken(sessionId, public_key):
        public_key = decodebytes(public_key)
        public_key = BytesIO(public_key).read()
        public_key = RSA.importKey(public_key, None)
        public_key = PKCS1_OAEP.new(public_key)

        sessionId = bytes(sessionId, 'utf-8')
        token = encodebytes(public_key.encrypt(sessionId))

        token = str(token, 'UTF-8')
        token = token.replace('\n', '')
        return token

    @staticmethod
    def OpenToken(token, private_key, passphrase=None):
        if len(token) != 172:
            print('Token Len =', len(token))
            raise ValueError('Invalid token')

        private_key = decodebytes(private_key)
        private_key = BytesIO(private_key).read()
        private_key = RSA.importKey(private_key, passphrase)
        private_key = PKCS1_OAEP.new(private_key)

        if not isinstance(token, bytes):
            token = bytes(token, 'utf-8')

        sessionId = private_key.decrypt(decodebytes(token))

        return str(sessionId, 'UTF-8')

    @staticmethod
    def SignToken(sessionId, private_key, passphrase=None):
        private_key = decodebytes(BytesIO(private_key).read())
        private_key = RSA.importKey(private_key, passphrase)
        return encodebytes(PKCS1_v1_5.new(private_key).sign(SHA256.new(sessionId)))

    @staticmethod
    def GenerateRSAKeys(bits=1024, passphrase=None, pkcs=1):
        rsa = RSA.generate(bits, Random.new().read)
        private = rsa.exportKey('PEM', passphrase, pkcs)
        public = rsa.publickey().exportKey('PEM', passphrase, pkcs)

        pri = encodebytes(private)
        pub = encodebytes(public)
        return (pri, pub)
