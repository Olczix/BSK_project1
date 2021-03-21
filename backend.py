import block_ciphers
import pandas as pd
import connection
import pyautogui
import pop_ups
import getmac
import time
import re
import os


class User():
    def __init__(self):
        self.login = None
        self.password = None
        self.session_key = None
        self.used_init_vector = None

    def get_login(self):
        return self.login

    def get_password(self):
        return self.password

    def get_session_key(self):
        return self.session_key

    def get_used_init_vector(self):
        return self.used_init_vector

    def set_login(self, login):
        self.login = login

    def set_password(self, password):
        self.password = password

    def set_session_key(self, key):
        self.session_key = key

    def set_used_init_vector(self, init_vector):
        self.used_init_vector = init_vector


def validate_login(login, password):
    for i in range(len(users['Login'])):
        if users_list[i] == login and pwds_list[i] == password:
            current_user.set_login(users_list[i])
            current_user.set_password(pwds_list[i])
            return pop_ups.PopUpMode.SUCCESS_LOG_IN
    return pop_ups.PopUpMode.ERROR_INVALID_INFORMATION


def validate_account_creation(login, password, repeat_password):
    new_user = pd.DataFrame([[login, password]], columns = ['Login', 'Password'])
    if login != "" and password == repeat_password:
        if login not in users_list:
            new_user.to_csv(users_data_path, mode = 'a', header = False, index = False)
            return pop_ups.PopUpMode.SUCCESS_SIGN_IN
        else:
            return pop_ups.PopUpMode.ERROR_USER_EXISTS
    else:
        return pop_ups.PopUpMode.ERROR_INVALID_INFORMATION


def send_message(message, encryption_mode):
    init_vector = os.urandom(16) if encryption_mode != 'ECB' else None
    current_user.set_used_init_vector(init_vector=init_vector)
    e = block_ciphers.createCipherClass(algorithm='AES', mode=encryption_mode,
                                        key=current_user.get_session_key(),
                                        init_vector=init_vector)
    encrypted_message = e.encrypt_text(message.encode('utf-8'))
    connection.Connection().send(encrypted_message)


def generate_session_key():
    bytes_list = []
    session_key = None
    session_key_len = 32
    mac_address = getmac.get_mac_address()
    mac_address_groups = re.findall('[0-9a-f][0-9a-f]', mac_address)
    counter = 0
    for _ in range(session_key_len):
        time.sleep(5 / session_key_len)
        position = pyautogui.position()
        x = position.x if int(position.x) > 0 else -position.x
        y = position.y if int(position.y) > 0 else -position.y
        group = int(mac_address_groups[counter%6], base=16)
        byte = ((x + y + group) * int(time.time())) % 256
        bytes_list.append(byte)
        counter += 1

    session_key = bytes(bytes_list)
    print(session_key)
    current_user.set_session_key(session_key)

    if session_key is not None:
        return pop_ups.PopUpMode.SUCCESS_SESSION_KEY
    else:
        return pop_ups.PopUpMode.ERROR_SESSION_KEY


# Getting 'database' of users
users_data_path = 'users.csv'
users = pd.read_csv(users_data_path, usecols=['Login','Password'])
users_list = list(users['Login'])
pwds_list = list(users['Password'])
current_user = User()