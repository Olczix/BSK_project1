import os
import cryptography
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat import backends

def createCipherClass(algorithm, mode, key, init_vector=None):
    if algorithm == 'AES':
        if mode == 'ECB':
            return Cipher_AES_EBC(key)
        if mode == 'CBC':
            return Cipher_AES_CBC(key, init_vector)
        if mode == 'CFB':
            return Cipher_AES_CFB(key,init_vector)
        if mode == 'OFB':
            return Cipher_AES_OFB(key,init_vector)

class Cipher_AES:
    def __init__(self, cipher):
        self.encryptor = cipher.encryptor()
        self.decryptor = cipher.decryptor()
        self.secret_message = ""
        
    def encrypt(self, message):
        self.secret_message = self.encryptor.update(message) + self.encryptor.finalize()
        
    def decrypt(self):
        self.secret_message = self.decryptor.update(self.secret_message) + self.decryptor.finalize()

class Cipher_AES_EBC(Cipher_AES):
    def __init__(self, key):
        cipher = Cipher(algorithms.AES(key), modes.ECB(), backends.default_backend())
        self.padder = padding.PKCS7(algorithms.AES.block_size).padder()
        self.unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
        super().__init__(cipher)
        
    def encrypt(self, message):
        padded_message = self.padder.update(message) + self.padder.finalize()
        super().encrypt(padded_message)
        
    def decrypt(self):
        super().decrypt()
        self.secret_message = self.unpadder.update(self.secret_message) + self.unpadder.finalize()

class Cipher_AES_CBC(Cipher_AES):
    def __init__(self, key, init_vector):
        cipher = Cipher(algorithms.AES(key), modes.CBC(init_vector), backends.default_backend())
        self.padder = padding.PKCS7(algorithms.AES.block_size).padder()
        self.unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
        super().__init__(cipher)      
        
    def encrypt(self, message):
        padded_message = self.padder.update(message) + self.padder.finalize()
        super().encrypt(padded_message)
        
    def decrypt(self):
        super().decrypt()
        self.secret_message = self.unpadder.update(self.secret_message) + self.unpadder.finalize()

class Cipher_AES_CFB(Cipher_AES):
    def __init__(self, key, init_vector):
        cipher = Cipher(algorithms.AES(key), modes.CFB(init_vector), backends.default_backend())
        super().__init__(cipher)
        
    def encrypt(self, message):
        super().encrypt(message)
        
    def decrypt(self):
        super().decrypt()

class Cipher_AES_OFB(Cipher_AES):
    def __init__(self, key, init_vector):
        cipher = Cipher(algorithms.AES(key), modes.OFB(init_vector), backends.default_backend())
        super().__init__(cipher)
        
    def encrypt(self, message):
        super().encrypt(message)
        
    def decrypt(self):
        super().decrypt()

if __name__ == '__main__':
    key = os.urandom(32)
    init_vector = os.urandom(16)
    e = createCipherClass('AES', 'ECB', key, init_vector)
    e.encrypt(b'Ala ma kota samolota')
    e.decrypt()
    

