import cryptography
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.asymmetric.padding import OAEP, MGF1
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

def createAESCipherClass(mode, key, init_vector=None):
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
        # create encryptor object
        encryptor = self.cipher.encryptor()
        # create padding object, which adds some chars for text, which length is not multiple of block size (128)
        padder = padding.ANSIX923(algorithms.AES.block_size).padder()
        # adding padding to message
        message = padder.update(message) + padder.finalize()
        # return encrypted message
        return encryptor.update(message) + encryptor.finalize()
        
    def decrypt_text(self, encrypted_message):
        # create decryptor object
        decryptor = self.cipher.decryptor()
        # create unpadder object, which deletes padding
        unpadder = padding.ANSIX923(algorithms.AES.block_size).unpadder()
        # decrypt message
        encrypted_message = decryptor.update(encrypted_message) + decryptor.finalize()
        # remove padding
        return unpadder.update(encrypted_message) + unpadder.finalize()
        
    def encrypt_file(self, path):
        message = file_manager.read_file(path)
        encrypted_message = self.encrypt_text(message)
        file_manager.write_to_file(path,encrypted_message)
        
    def decrypt_file(self, path):
        encrypted_message = file_manager.read_file(path)
        decrypted_message = self.decrypt_text(encrypted_message)
        file_manager.write_to_file(path,decrypted_message)


class RSA_Agent:
    def __init__(self, key_path, key, init_vector):
        # path where keys' directories will be stored
        self.key_path = key_path
        # cipher for public and private key encryption and decryption
        self.aes_cbc_cipher = createAESCipherClass('CBC', key, init_vector)
    
    def generate_RSA_key_pair(self):
        # create private key object
        private_key = rsa.generate_private_key(
            public_exponent=65537, # don't worry about this number, it's from spec 
            key_size=2048,
            backend=backends.default_backend())
        # create public key object
        public_key = private_key.public_key()
        # create content of private key file
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption())
        # create content of public key file
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo)
        # save public and private keys to file and encrypt them
        self.save_key_to_file(private_pem, self.key_path, PRIVATE_KEY_DIR_NAME, PRIVATE_KEY_FILE_NAME)
        self.save_key_to_file(public_pem, self.key_path, PUBLIC_KEY_DIR_NAME, PUBLIC_KEY_FILE_NAME)

    def get_my_private_key_object(self):
        # get private key path
        key_file = os.path.join(self.key_path, PRIVATE_KEY_DIR_NAME, PRIVATE_KEY_FILE_NAME)
        # read  encrypted private key
        encrypted_key_pem = file_manager.read_file(key_file)
        # decrypt private key
        decrypted_key_pem = self.aes_cbc_cipher.decrypt_text(encrypted_key_pem)
        # create private key object
        private_key = serialization.load_pem_private_key(
        decrypted_key_pem,
        backend=backends.default_backend(),
        password=None)
        return private_key

    def get_my_public_key_object(self):
        # get public key path
        key_file = os.path.join(self.key_path, PUBLIC_KEY_DIR_NAME, PUBLIC_KEY_FILE_NAME)
        # read encrypted public key
        encrypted_key_pem = file_manager.read_file(key_file)
        # decrypt public key
        decrypted_key_pem = self.aes_cbc_cipher.decrypt_text(encrypted_key_pem)
        #create public key object
        public_key = serialization.load_pem_public_key(
        decrypted_key_pem,
        backend=backends.default_backend())
        return public_key

    def get_my_public_key_bytes(self):
        # get public key path
        key_file = os.path.join(self.key_path, PUBLIC_KEY_DIR_NAME, PUBLIC_KEY_FILE_NAME)
        # read encrypted file
        encrypted_key_pem = file_manager.read_file(key_file)
        # return decrypted public key
        return self.aes_cbc_cipher.decrypt_text(encrypted_key_pem)
       
    def save_key_to_file(self, pem, key_path, dir_name, file_name):
        # get key path
        key_dir = os.path.join(key_path,dir_name)
        key_file = os.path.join(key_dir, file_name)
        # create directory for key
        file_manager.create_dir(key_dir)
        # encrypt the key
        encrypted_pem = self.aes_cbc_cipher.encrypt_text(pem)
        # write to key file, create if doesn't exist
        file_manager.write_to_file(key_file, encrypted_pem)

    def encrypt_session_key(self, session_key):
        # tutaj pewnie bedzie klucz publiczny drugiej osoby, ale trzeba pomyslec o przechowywaniu uzytkownikow

        public_key = self.get_my_public_key_object()
        encrypted_session_key = public_key.encrypt(
        session_key,
        OAEP(
        mgf=MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None))
        return encrypted_session_key

    def decrypt_session_key(self, encrypted_session_key):
        private_key = self.get_my_private_key_object()
        decrypted_session_key = private_key.decrypt(
        encrypted_session_key,
        OAEP(
        mgf=MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None))
        return decrypted_session_key


