from Crypto import Random
from Crypto.Cipher import AES
from Crypto.Cipher import DES
from cryptography.fernet import Fernet
import os
import os.path
from os import listdir
from os.path import isfile, join
import time

class Encryptor:
    def __init__(self, key):
        self.key = key

    def pad(self, s):
        return s + b"\0" * (AES.block_size - len(s) % AES.block_size)

    def encrypt(self, message, key, key_size=256):
        message = self.pad(message)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        return iv + cipher.encrypt(message)

    def encrypt_file(self, file_name):
        with open(file_name, 'rb') as fo:
            plaintext = fo.read()
        enc = self.encrypt(plaintext, self.key)
        with open(file_name + ".enc", 'wb') as fo:
            fo.write(enc)

    def decrypt(self, ciphertext, key):
        iv = ciphertext[:AES.block_size]
        cipher = AES.new(key, AES.MODE_CBC, iv)
        plaintext = cipher.decrypt(ciphertext[AES.block_size:])
        return plaintext.rstrip(b"\0")

    def decrypt_file(self, file_name):
        with open(file_name, 'rb') as fo:
            ciphertext = fo.read()
        dec = self.decrypt(ciphertext, self.key)
        with open(file_name[:-4], 'wb') as fo:
            fo.write(dec)
        return file_name[:-4]

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# ====================FERNET ALGORITHM===================================================
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

    def fernet_encrypt(self, message, key):
        f = Fernet(self.key)
        return f.encrypt(message)

    def fernet_encrypt_file(self, file_name):
        with open(file_name, 'rb') as fo:
            plaintext = fo.read()
        enc = self.fernet_encrypt(plaintext, self.key)
        with open(file_name + ".enc", 'wb') as fo:
            fo.write(enc)

    def fernet_decrypt(self, message, key):
        f = Fernet(self.key)
        return f.decrypt(message)

    def fernet_decrypt_file(self, file_name):
        with open(file_name, 'rb') as fo:
            enctext = fo.read()
        enc = self.fernet_decrypt(enctext, self.key)
        with open(file_name[:-4], 'wb') as fo:
            fo.write(enc)

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# ====================DES ALGORITHM===================================================
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

    def des_pad(self, s):
        return s + b"\0" * (8 - len(s) % 8)

    def des_encrypt(self, message, key):
        cipher = DES.new(self.key, DES.MODE_ECB)
        return cipher.encrypt(self.des_pad(message))

    def des_decrypt(self, message, key):
        cipher = DES.new(self.key, DES.MODE_ECB)
        return cipher.decrypt(message).rstrip(b"\0")


    def getAllFiles(self, path):
        dirs = []
        for dirName, subdirList, fileList in os.walk(path):
            for fname in fileList:
                if (fname != 'script.py' and fname != 'data.txt.enc'):
                    dirs.append(dirName + "\\" + fname)
        return dirs

    def encrypt_all_files(self, path):
        dirs = self.getAllFiles(path)
        for file_name in dirs:
            self.encrypt_file(file_name)

    def decrypt_all_files(self, path):
        dirs = self.getAllFiles(path)
        for file_name in dirs:
            self.decrypt_file(file_name)