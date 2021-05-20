import crypto_stuff
import os


# Class responsible for handling user object management
class Current_User:
    def __init__(self, login, hash_password_for_key, hash_password_for_init_vector, creation=False):
        self.login = login
        self.key_path = 'user_' + login
        self.rsa_agent = crypto_stuff.RSA_Agent(self.key_path, hash_password_for_key, hash_password_for_init_vector)
        self.known_users = []
        if creation: self.rsa_agent.generate_RSA_key_pair()

    def set_used_init_vector(self, init_vector):
        self.used_init_vector = init_vector

    def get_used_init_vector(self, init_vector):
        return self.used_init_vector

    def set_session_key(self, session_key):
        self.session_key = session_key

    def set_encrypted_session_key(self, encrypted_session_key):
        self.session_key = self.rsa_agent.decrypt_session_key(encrypted_session_key)

    def get_session_key(self):
        return self.session_key

    def get_encrypted_session_key(self, public_key_bytes):
        return self.rsa_agent.encrypt_session_key(public_key_bytes,self.session_key)

    def get_my_public_key(self):
        return self.rsa_agent.get_public_key_bytes(self.key_path)

    def decrypt_message(self, mode, encrypted_message, init_vector):
        return crypto_stuff.createAESCipherClass(mode, self.session_key, init_vector).decrypt_text(encrypted_message)

    def encrypt_message(self, mode, message, init_vector):
        return crypto_stuff.createAESCipherClass(mode, self.session_key, init_vector).encrypt_text(message)