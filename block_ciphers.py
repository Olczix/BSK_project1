import os
import cryptography
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat import backends

def createCipherClass(algorithm, mode, key, init_vector=None):
    if algorithm == 'AES':
        if mode == 'ECB':
            mode = modes.ECB()
        if mode == 'CBC':
            mode = modes.CBC(init_vector)
        if mode == 'CFB':
            mode = modes.CFB(init_vector)
        if mode == 'OFB':
            mode = modes.OFB(init_vector)
        return Cipher_AES(key, mode)

class Cipher_AES:
    def __init__(self, key, mode):
        cipher = Cipher(algorithms.AES(key), mode, backends.default_backend())
        self.encryptor = cipher.encryptor()
        self.decryptor = cipher.decryptor()
        self.padder = padding.ANSIX923(algorithms.AES.block_size).padder()
        self.unpadder = padding.ANSIX923(algorithms.AES.block_size).unpadder()
        
    def encrypt_text(self, message):
        message = self.padder.update(message) + self.padder.finalize()
        return self.encryptor.update(message) + self.encryptor.finalize()
        
    def decrypt_text(self, encrypted_message):
        encrypted_message = self.decryptor.update(encrypted_message) + self.decryptor.finalize()
        return self.unpadder.update(encrypted_message) + self.unpadder.finalize()
        
    def encrypt_file(self, path):
        with open(path, 'rb') as file: 
            message = file.read() 
        
        encrypted_message = self.encrypt_text(message)
        
        with open(path, 'wb') as encrypted_file: 
            encrypted_file.write(encrypted_message) 
        
    def decrypt_file(self, path):
        with open(path, 'rb') as encrypted_file: 
            encrypted_message = encrypted_file.read() 
  
        decrypted_message = self.decrypt_text(encrypted_message)

        with open(path, 'wb') as decrypted_file: 
            decrypted_file.write(decrypted_message)

if __name__ == '__main__':
    key = os.urandom(32)
    init_vector = os.urandom(16)
    e = createCipherClass('AES', 'OFB', key, init_vector)
