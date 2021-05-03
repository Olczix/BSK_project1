import crypto_stuff
import os



class User:
    def __init__(self, login):
        self.login = login
        self.key_path = 'user_' + login    

class Current_User(User):
    def __init__(self, login, hash_password_for_key, hash_password_for_init_vector, creation=False):
        super().__init__(login)
        self.rsa_agent = crypto_stuff.RSA_Agent(self.key_path, hash_password_for_key, hash_password_for_init_vector)
        self.known_users = []
        if creation: self.rsa_agent.generate_RSA_key_pair()
        else:
            self.known_users = os.listdir(self.key_path)
            self.known_users.remove(crypto_stuff.PUBLIC_KEY_DIR_NAME)
            self.known_users.remove(crypto_stuff.PRIVATE_KEY_DIR_NAME)

    def set_used_init_vector(self, init_vector):
        self.used_init_vector = init_vector

    def get_used_init_vector(self, init_vector):
        return self.used_init_vector

    def set_session_key(self, session_key):
        self.session_key = session_key

    def get_session_key(self):
        return self.session_key

    def add_known_user(self, login, public_key):
        user_dir = 'user_' + login
        self.known_users.append(user_dir)
        self.rsa_agent.store_public_key(user_dir,public_key)