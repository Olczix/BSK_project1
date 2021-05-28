import users
import backend
import network_connection
import threading
import config
import os


# Class responsible for managing logic connection between two clients
class Logic_Connection:

    def __init__(self, ip_address):
        self.lock = threading.Lock()
        self.sender = network_connection.NetworkConnection(ip_address)
        self.communication_allowed = False
        receivers_public_key = None

    def set_receivers_public_key(self,receivers_public_key):
        self.lock.acquire()
        self.receivers_public_key = receivers_public_key
        self.lock.release()

    def send_my_public_key(self):
        self.lock.acquire()
        my_public_key = backend.current_user.get_my_public_key()
        message = config.PUBLIC_KEY_TYPE + my_public_key
        self.sender.send(message)
        self.lock.release()

    def set_session_key(self, encrypted_session_key):
        self.lock.acquire()
        backend.current_user.set_encrypted_session_key(encrypted_session_key)
        self.lock.release()

    def allow_communication(self):
        self.lock.acquire()
        self.communication_allowed = True
        self.lock.release()

    def send_encrypted_session_key(self):
        self.lock.acquire()
        message = config.SESSION_KEY_TYPE + backend.current_user.get_encrypted_session_key(self.receivers_public_key)
        self.sender.send(message)
        self.lock.release()

    def decrypt_message(self, mode, encrypted_message, init_vector):
        self.lock.acquire()
        decrypted_message = backend.current_user.decrypt_message(mode, encrypted_message, init_vector)
        self.lock.release()
        return decrypted_message
        
    def encrypt_and_send_message(self, mode, message):
        self.lock.acquire()
        if mode != 'ECB':
            init_vector = os.urandom(16)
            encrypted_message = backend.current_user.encrypt_message(mode,message, init_vector)
            mode = mode.encode('utf-8')
            whole_message = config.JUST_TALK_TYPE + mode + init_vector + encrypted_message
        else:
            encrypted_message = backend.current_user.encrypt_message(mode,message, None)
            mode = mode.encode('utf-8')
            whole_message = config.JUST_TALK_TYPE + mode + encrypted_message
        self.sender.send(whole_message)
        self.lock.release()

    def send_file_transfer_config(self,mode, file):
        self.lock.acquire()

        mode = mode.encode('utf-8')
        extension = file.file_type.encode('utf-8')
        extension_len = str(len(extension)).encode('utf-8')
        number_of_chunks = str(file.no_of_chunks).encode('utf-8')
        message = extension_len + extension + number_of_chunks
        
        if mode != b'ECB':
            init_vector = os.urandom(16)
            file.set_init_vector(init_vector)
            encrypted_message = backend.current_user.encrypt_message(mode,message, init_vector)
            whole_message = config.FILE_TRANSFER_CONFIGURATION + mode + init_vector + encrypted_message
        else:
            encrypted_message = backend.current_user.encrypt_message(mode,message, None)
            whole_message = config.FILE_TRANSFER_CONFIGURATION + mode + encrypted_message
        self.sender.send(whole_message)
        
        self.lock.release()

    def send_file_chunk(self, mode, init_vector, chunk, chunk_number):
        self.lock.acquire()

        # length of chunk_number ready to be sent
        chunk_number_length = str(len(str(chunk_number))).encode('utf-8')

        # chunk number ready to be sent
        chunk_number_to_send = str(chunk_number).encode('utf-8')

        message = chunk_number_length + chunk_number_to_send + chunk
        encrypted_message = backend.current_user.encrypt_message(mode,message, init_vector)

        whole_message = config.FILE_CHUNK + encrypted_message

        self.sender.send(whole_message)

        self.lock.release()
