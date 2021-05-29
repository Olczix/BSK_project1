from plyer import filechooser
import crypto_stuff
import pandas as pd
from pathlib import Path
import logic_connection
import network_connection
import pyautogui
import pop_ups
import config
import users
import getmac
import time
import re
import os
import file_manager


# Getting 'database' of users
users_data_path = 'users.csv'
if not os.path.exists(users_data_path): 
    df = pd.DataFrame(columns=['Login', 'Password'])
    df.to_csv(users_data_path, index=False)
file_manager.create_dir(config.RECEIVED_FILE_DIR)
users_frame = pd.read_csv(users_data_path, usecols=['Login','Password'])
users_list = list(users_frame['Login'])
pwds_list = list(users_frame['Password'])
current_user = None
connection = None


# Validate login and check if user is in database
def validate_login(login, password):
    hash_password = crypto_stuff.hash_password_for_key(str.encode(password,'latin_1'))
    password = crypto_stuff.hash_password_for_init_vector(str.encode(password,'latin_1'))
    for i in range(len(users_frame['Login'])):
        if users_list[i] == login and pwds_list[i] == hash_password.decode('latin_1'):
            
            global current_user
            current_user = users.Current_User(login, hash_password, password)

            init_listening_thread()

            return pop_ups.PopUpMode.SUCCESS_LOG_IN
    return pop_ups.PopUpMode.ERROR_INVALID_INFORMATION


# Validate new user login and passwords correctness
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

            init_listening_thread()

            new_user.to_csv(users_data_path, mode = 'a', header = False, index = False)
            return pop_ups.PopUpMode.SUCCESS_SIGN_IN
        else:
            return pop_ups.PopUpMode.ERROR_USER_EXISTS
    else:
        return pop_ups.PopUpMode.ERROR_INVALID_INFORMATION


# Validate client IP address format
def validate_ip_address(ip_address):
    if len(ip_address.split(".")) == 4:
        config.ADDRESS = ip_address
        return True
    else:
        pop_ups.popUp(pop_ups.PopUpMode.ERROR_INCORRECT_IP_ADDRESS_FORMAT)
        return False


# Handle message sending
def send_message(message, encryption_mode):
    if current_user.get_session_key() is None:
        return pop_ups.PopUpMode.NO_SESSION_KEY_GENERATED
    else:
        global connection
        if connection is None:
            connection = logic_connection.Logic_Connection(config.ADDRESS)
            connection.send_my_public_key()
        elif connection.communication_allowed:
            connection.encrypt_and_send_message(encryption_mode, message.encode('utf-8'))
        
        return pop_ups.PopUpMode.SUCCESS_MESSAGE_SEND


# Handle session key generation
def generate_session_key():
    bytes_list = []
    session_key = None
    session_key_len = 32
    session_key_generation_time = 1
    mac_address = getmac.get_mac_address()
    mac_address_groups = re.findall('[0-9a-f][0-9a-f]', mac_address)
    counter = 0
    for _ in range(session_key_len):
        time.sleep(session_key_generation_time / session_key_len)
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
        # Initialize connection
        global connection
        if connection is None:
            connection = logic_connection.Logic_Connection(config.ADDRESS)
            connection.send_my_public_key()
        return pop_ups.PopUpMode.SUCCESS_SESSION_KEY
    else:
        return pop_ups.PopUpMode.ERROR_SESSION_KEY


# Show chosen file path
def get_chosen_file_path():
    path = filechooser.open_file(title="Select file to send ...")
    if path is not None:
        pop_ups.popUp(mode=pop_ups.PopUpMode.CHOSEN_FILE_CONFIRMATION,
                      extra_info=f'CHOSEN FILE:\n{path[0]}')
    return path[0]


# Handle file sending validation
def validate_file_sending(path, mode):
    if not mode:
        pop_ups.popUp(pop_ups.PopUpMode.NO_ENCRYPTION_MODE_SELECTED)
        return False
    elif not path:
        pop_ups.popUp(pop_ups.PopUpMode.NO_FILE_SELECTED)
        return False
    return True    


# Class representing a file object
class File():
    def __init__(self, path, is_to_save=False):
        self.path = path
        self.file_content = None
        self.file_type = self.path.split('.')[-1]
        self.file_size_in_bytes = Path(self.path).stat().st_size
        self.no_of_packets = self.file_size_in_bytes/config.PACKAGE_SIZE
        self.chunks = None
        self.no_of_chunks = None
        self.encryption_mode = None
        self.init_vector = None

        if is_to_save == False:
            self.read_binary_content()
            self.divide_file_into_chunks()

    def set_init_vector(self, init_vector):
        self.init_vector = init_vector

    def set_encryption_mode(self, encryption_mode):
        self.encryption_mode = encryption_mode

    def get_init_vector(self):
        return self.init_vector

    def get_encryption_mode(self):
        return self.encryption_mode

    def set_chunks_number(self,number_of_chunks):
        self.no_of_chunks = number_of_chunks

    def read_binary_content(self):
        with open(self.path, 'rb') as f:
            self.file_content = f.read()

    def add_binary_content(self, content):
        with open(self.path, 'ab') as f:
            f.write(content)

    def divide_file_into_chunks(self):
        # big files handling + there is a need to cut it in smaller pieces
        if self.file_size_in_bytes > config.PACKAGE_SIZE:
            self.chunks = [self.file_content[i:i+config.PACKAGE_SIZE]
                           for i in range(0, self.file_size_in_bytes, config.PACKAGE_SIZE)]
        else: # small file - only one chunk
            self.chunks = [self.file_content]

        self.no_of_chunks = len(self.chunks)


# Initialization of file sender (with progress bar)
def init_file_sender(path, encryption_mode):
    f = File(path=path)
    f.set_encryption_mode(encryption_mode)
    # start sending chunks and displaying progress bar
    pop_ups.ProgressBarFileSender(f=f, encryption_mode=encryption_mode)


def send_file_transfer_config(encryption_mode, file):
    print('Send file transfer configuration message')
    connection.send_file_transfer_config(mode = encryption_mode,file = file)

    """
    Message  contains:
        - message type = config.FILE_TRANSFER_CONFIGURATION
        - encryption_mode
        - init_vector
        - extension length
        - file_extention
        - number of file chunks
    """


# Handle sending a file chunk (for bigger files)
def send_file_chunk(chunk, file, chunk_number):
    # Handle file chunk sending using our custom communication protocol
    # message contains:
    #   - message type = config.FILE_CHUNK
    #   - length of chunk number
    #   - number of sent chunk
    #   - actual file chunk body/content

    #file_chunk = chunk.decode("latin_1")
    mode = file.get_encryption_mode()
    if mode != 'ECB': init_vector = file.get_init_vector()
    else: init_vector = None

    connection.send_file_chunk(mode=mode, init_vector=init_vector, chunk=chunk, chunk_number=chunk_number)


# Initialize thread for listening incomming messages 
def init_listening_thread():
    network_connection.ListenningThread().start()


# File object containing file data and chunks we receive
file_to_save = None
file_number = 0

def init_received_file(file_name, extension, number_of_chunks, mode, init_vector=None):
    file = file_name + '.' + extension.decode('utf-8')
    path = os.path.join(config.RECEIVED_FILE_DIR, file)
    file_manager.write_to_file(path, b'')
    global file_to_save
    file_to_save = File(path, is_to_save=True)
    file_to_save.set_encryption_mode(mode)
    file_to_save.set_chunks_number(number_of_chunks)
    if mode != b'ECB':
        file_to_save.set_init_vector(init_vector)

# Decide what to do with received message
# This function is called when a new message arrives
def handle_received_message(message, ip_address):
    type = message[0:1]
    content = message[1:]
    global connection
    # we get public key and we didn't send our pulic key
    if type == config.PUBLIC_KEY_TYPE and connection is None:
        # logic connection object has to be created
        connection = logic_connection.Logic_Connection(ip_address)
        # we should send our public key
        connection.send_my_public_key()
        # store receivers public key
        connection.set_receivers_public_key(content)
    
    # we get public key, but we previously sent one
    elif type == config.PUBLIC_KEY_TYPE and connection is not None:
        # store receivers public key
        connection.set_receivers_public_key(content)
        # we send previously generated session key
        connection.send_encrypted_session_key()
        connection.allow_communication()
        print("Communication Allowed")

    # we received session key from another user
    # it is encrypted with our public key
    # connection object should be already created at this point
    if type == config.SESSION_KEY_TYPE:
        # we set session key and now communication is allowed
        connection.set_session_key(content)
        connection.allow_communication()
        print("Communication Allowed")

    # normal communication case
    if type == config.JUST_TALK_TYPE:
        mode = content[0:3]
        if mode != b'ECB':
            init_vector = content[3:19]
            encrypted_message_content = content[19:]
        else:
            init_vector = None
            encrypted_message_content = content[3:]
        mode = mode.decode('utf-8')
        if connection:
            decrypted_message_content = connection.decrypt_message(mode, encrypted_message_content, init_vector)
            # new message presenting
            pop_ups.NewMessage(msg=decrypted_message_content.decode("utf-8"), address=ip_address)

    if type == config.FILE_TRANSFER_CONFIGURATION:
        mode = content[0:3]
        if mode != b'ECB':
            init_vector = content[3:19]
            encrypted_message_content = content[19:]
        else:
            init_vector = None
            encrypted_message_content = content[3:]
        mode = mode.decode('utf-8')
        decrypted_message_content = connection.decrypt_message(mode, encrypted_message_content, init_vector)
        extension_len = int(decrypted_message_content[0:1])
        extension = decrypted_message_content[1:(1 + extension_len)]
        number_of_chunks = int(decrypted_message_content[(1 + extension_len):])
        global file_number
        file_number += 1
        #TODO handle receving file via gui
        #Consider asking user for file name - first argument
        init_received_file(ip_address + '_' + str(file_number),extension, number_of_chunks, mode, init_vector)

    if type == config.FILE_CHUNK:
        mode = file_to_save.get_encryption_mode()
        init_vector = file_to_save.get_init_vector()
        decrypted_message = connection.decrypt_message(mode, content, init_vector)
        chunk_number_length = int(decrypted_message[0:1])
        chunk_number = int(decrypted_message[1:(1+chunk_number_length)])
        chunk = decrypted_message[(1+chunk_number_length):]
        file_to_save.add_binary_content(chunk)

    # TODO: Handle file_transfer_configuration message type
    # if type == config.FILE_TRANSEF_CONFIGURATION:
    #   file_extention = None               # file extention
    # -> create empty file with given extention in current directory (ewentualnie zrobić nowy folder /IncommingFiles)
    #   file_to_save = File()               # tutaj trzeba podać ścieżkę do utworzonego wyżej pliku
    #   file_to_save.no_of_chunks = None    # tutaj ilość pakietów, którą odczytaliśmy z wiadomości
    #   file_to_save.file_type = None       # tutaj file extention
    # TODO: Add handling incoming files in GUI



    # TODO: Handle next file chunks transition - we need to add them all together
    # etc. in order to create a final file
    # -> number of chunks is passed with FILE_TRANSEF_CONFIGURATION message type
    # if type == config.FILE_CHUNK:
    #   file_to_save.chunks.append() #tutaj dodajemy odkodowany odebrany chunk
