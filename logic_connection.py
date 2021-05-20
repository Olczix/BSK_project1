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
