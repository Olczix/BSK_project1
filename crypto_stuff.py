import cryptography
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat import backends
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
import file_manager
import os

PRIVATE_KEY_BEGIN = b'-----BEGIN PRIVATE KEY-----\n'
PRIVATE_KEY_END = b'-----END PRIVATE KEY-----\n'
PRIVATE_KEY_DIR_NAME = 'private_key'
PUBLIC_KEY_DIR_NAME = 'public_key'
PRIVATE_KEY_FILE_NAME = 'private_key.pem'
PUBLIC_KEY_FILE_NAME = 'public_key.pem'

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

def hash_password_for_key(password):
    digest = hashes.Hash(hashes.SHA256(), backends.default_backend())
    digest.update(password) 
    return digest.finalize()

def hash_password_for_init_vector(password):
    digest = hashes.Hash(hashes.SHAKE128(16), backends.default_backend())
    digest.update(password) 
    return digest.finalize()

class Cipher_AES:
    def __init__(self, key, mode):
        self.cipher = Cipher(algorithms.AES(key), mode, backends.default_backend())
        
    def encrypt_text(self, message):
        encryptor = self.cipher.encryptor()
        padder = padding.ANSIX923(algorithms.AES.block_size).padder()
        message = padder.update(message) + padder.finalize()
        return encryptor.update(message) + encryptor.finalize()
        
    def decrypt_text(self, encrypted_message):
        decryptor = self.cipher.decryptor()
        unpadder = padding.ANSIX923(algorithms.AES.block_size).unpadder()
        encrypted_message = decryptor.update(encrypted_message) + decryptor.finalize()
        return unpadder.update(encrypted_message) + unpadder.finalize()
        
    def encrypt_file(self, path):
        message = file_manager.read_file(path)
        
        encrypted_message = self.encrypt_text(message)
        
        file_manager.write_to_file(path,encrypted_message)
        
    def decrypt_file(self, path):
        encrypted_message = file_manager.read_file(path)
  
        decrypted_message = self.decrypt_text(encrypted_message)

        file_manager.write_to_file(path,decrypted_message)


class Key_Manager:
    def __init__(self,key, init_vector):
        self.aes_cbc_cipher = createCipherClass('AES', 'CBC', key, init_vector)
    
    def generate_RSA_key_pair(self,key_size,key_path):

        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
            backend=backends.default_backend())

        public_key = private_key.public_key()

        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption())

        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo)

        self.save_key_to_file(private_pem, key_path, PRIVATE_KEY_DIR_NAME, PRIVATE_KEY_FILE_NAME)
        self.save_key_to_file(public_pem, key_path, PUBLIC_KEY_DIR_NAME, PUBLIC_KEY_FILE_NAME)

    def save_key_to_file(self, pem, key_path, dir_name, file_name):
        key_dir = os.path.join(key_path,dir_name)
        key_file = os.path.join(key_dir, file_name)
        file_manager.create_dir(key_dir)
        file_manager.write_to_file(key_file, pem)
        self.aes_cbc_cipher.encrypt_file(key_file)


