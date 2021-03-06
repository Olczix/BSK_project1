from plyer import filechooser
import crypto_stuff
import pandas as pd
from pathlib import Path
import network_connection
import threading
import pyautogui
import pop_ups
import config
import users
import getmac
import time
import re
import os
from kivy.uix.progressbar import ProgressBar


def validate_login(login, password):
    hash_password = crypto_stuff.hash_password_for_key(str.encode(password,'latin_1'))
    password = crypto_stuff.hash_password_for_init_vector(str.encode(password,'latin_1'))
    for i in range(len(users_frame['Login'])):
        if users_list[i] == login and pwds_list[i] == hash_password.decode('latin_1'):
            global current_user
            current_user = users.Current_User(login, hash_password, password)
            return pop_ups.PopUpMode.SUCCESS_LOG_IN
    return pop_ups.PopUpMode.ERROR_INVALID_INFORMATION


def validate_account_creation(login, password, repeat_password):
    hash_password = crypto_stuff.hash_password_for_key(str.encode(password, 'latin_1'))
    hash_repeat_password = crypto_stuff.hash_password_for_key(str.encode(repeat_password, 'latin_1'))
    password = crypto_stuff.hash_password_for_init_vector(str.encode(password, 'latin_1'))
    repeat_password = crypto_stuff.hash_password_for_init_vector(str.encode(repeat_password, 'latin_1'))
    new_user = pd.DataFrame([[login, hash_password.decode('latin_1')]], columns = ['Login', 'Password'])
    if login != "" and hash_password == hash_repeat_password:
        if login not in users_list:
            global current_user
            current_user = users.Current_User(login, hash_password, password, creation=True)
            new_user.to_csv(users_data_path, mode = 'a', header = False, index = False)
            return pop_ups.PopUpMode.SUCCESS_SIGN_IN
        else:
            return pop_ups.PopUpMode.ERROR_USER_EXISTS
    else:
        return pop_ups.PopUpMode.ERROR_INVALID_INFORMATION


def send_message(message, encryption_mode):
    if current_user.get_session_key() is None:
        return pop_ups.PopUpMode.NO_SESSION_KEY_GENERATED
    else:
        init_vector = os.urandom(16) if encryption_mode != 'ECB' else None
        current_user.set_used_init_vector(init_vector=init_vector)
        e = crypto_stuff.createAESCipherClass(mode=encryption_mode,
                                            key=current_user.get_session_key(),
                                            init_vector=init_vector)
        encrypted_message = e.encrypt_text(message.encode('utf-8'))
        network_connection.NetworkConnection().send(encrypted_message)
        return pop_ups.PopUpMode.SUCCESS_MESSAGE_SEND

def generate_session_key():
    # Add progress bar:
    # pop_ups.ProgressBarKeyGeneration()

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
    current_user.set_session_key(session_key)

    if session_key is not None:
        return pop_ups.PopUpMode.SUCCESS_SESSION_KEY
    else:
        return pop_ups.PopUpMode.ERROR_SESSION_KEY




def get_chosen_file_path():
    path = filechooser.open_file(title="Select file to send ...")
    if path is not None:
        pop_ups.popUp(mode=pop_ups.PopUpMode.CHOSEN_FILE_CONFIRMATION,
                      extra_info=f'CHOSEN FILE:\n{path[0]}')
    return path[0]


def validate_file_sending(path, mode):
    if not mode:
        pop_ups.popUp(pop_ups.PopUpMode.NO_ENCRYPTION_MODE_SELECTED)
        return False
    elif not path:
        pop_ups.popUp(pop_ups.PopUpMode.NO_FILE_SELECTED)
        return False
    return True    


class File():
    def __init__(self, path):
        self.path = path
        self.file_content = None
        self.file_type = self.path.split('.')[-1]
        self.file_size_in_bytes = Path(self.path).stat().st_size
        self.no_of_packets = self.file_size_in_bytes/config.PACKAGE_SIZE
        self.chunks = None
        self.no_of_chunks = None

        self.read_binary_content()
        self.divide_file_into_chunks()

    def read_binary_content(self):
        with open(self.path, 'rb') as f:
            self.file_content = f.read()

    def divide_file_into_chunks(self):
        # big files handling + there is a need to cut it in smaller pieces
        if self.file_size_in_bytes > config.PACKAGE_SIZE:
            self.chunks = [self.file_content[i:i+config.PACKAGE_SIZE]
                           for i in range(0, self.file_size_in_bytes, config.PACKAGE_SIZE)]
        else: # small file - only one chunk
            self.chunks = [self.file_content]

        self.no_of_chunks = len(self.chunks)


def init_file_sender(path, encryption_mode):
    f = File(path=path)

    # prepare cryptor for message encyption
    init_vector = os.urandom(16) if encryption_mode != 'ECB' else None
    current_user.set_used_init_vector(init_vector=init_vector)
    e = crypto_stuff.createAESCipherClass(mode=encryption_mode,
                                          key=current_user.get_session_key(),
                                          init_vector=init_vector)

    # start sending chunks and displaying progress bar
    pop_ups.ProgressBarFileSender(f=f, cryptor=e)


def send_file_chunk(chunk, cryptor):
    chunk_string = chunk.decode("utf-8")
    encrypted_chunk = cryptor.encrypt_text(chunk_string.encode('utf-8'))
    network_connection.NetworkConnection().send(encrypted_chunk)


# Getting 'database' of users
users_data_path = 'users.csv'
if not os.path.exists(users_data_path): 
    df = pd.DataFrame(columns=['Login', 'Password'])
    df.to_csv(users_data_path, index=False)
users_frame = pd.read_csv(users_data_path, usecols=['Login','Password'])
users_list = list(users_frame['Login'])
pwds_list = list(users_frame['Password'])
current_user = None
