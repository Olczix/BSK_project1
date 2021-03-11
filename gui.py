from kivy.app import App 
from kivy.properties import ObjectProperty, StringProperty
from kivy.lang import Builder
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen 
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from pop_ups import PopUpMode, popUp
import connection
import block_ciphers
import pandas as pd
import time
import pyautogui
import getmac
import re
import os


# Class responsible for handling loging in
class loginScreen(Screen):
    login = ObjectProperty(None)
    password = ObjectProperty(None)

    def validate(self):
        check = False
        for i in range(len(users['Login'])): 
            if users_list[i] == self.login.text and pwds_list[i] == self.password.text:
                currently_logged_user = users_list[i]
                screen_manager.current = 'chooser_screen'
                popUp(PopUpMode.SUCCESS_LOG_IN)
                check = True

        if not check:
            popUp(PopUpMode.ERROR_UNKNOWN_USER)
            self.login.text = ""
            self.password.text = ""


# Class responsible for handling signing up and validating entered user's credentials
class signupScreen(Screen):
    login = ObjectProperty(None)
    password = ObjectProperty(None)
    repeat_password = ObjectProperty(None)

    def create_account_pbtn(self):
        new_user = pd.DataFrame([[self.login.text, self.password.text]], columns = ['Login', 'Password'])
        if self.login.text != "" and self.password.text == self.repeat_password.text:
            if self.login.text not in users_list:
                new_user.to_csv(users_data_path, mode = 'a', header = False, index = False) 
                screen_manager.current = 'chooser_screen'
                popUp(PopUpMode.SUCCESS_SIGN_IN)
            else:
                popUp(PopUpMode.ERROR_USER_EXISTS)
                self.login.text = ''
                self.password.text = ''
                self.repeat_password.text = ''
        else:
            popUp(PopUpMode.ERROR_INVALID_INFORMATION)


# Class responsible for handling users choice: send message, send file, generate session key
class chooserSenderScreen(Screen): 
    pass


# Class responsible for handling messages sending
class messageSenderScreen(Screen):
    message = ObjectProperty(None)
    init_vector = ObjectProperty(None)
    encryption_mode = ObjectProperty(None)

    def set_block_encoding_choice(self, instance, value, block_encoding_choice):
        if value == True:
            self.encryption_mode = block_encoding_choice

    def send(self):
        key = os.urandom(32) # session key
        valid_init_vector = self.init_vector.text.rjust(16,'0') \
            if len(self.init_vector.text) < 16 else self.init_vector.text[0:16]
        e = block_ciphers.createCipherClass('AES', self.encryption_mode, key, 
                                             valid_init_vector.encode('utf-8'))
        encrypted_message = e.encrypt_text(self.message.text.encode('utf-8'))
        connection.Connection().send(encrypted_message)
        self.message.text = ""
        self.init_vector.text = ""


# Class responsible for handling files sending
class fileSenderScreen(Screen):
    message = ObjectProperty(None)


# Class responsible for handling session key generation
class sessionKeyGeneratorScreen(Screen):
    key_int = 0 
    key_str = '' # 32B = 128b = 32 chars
    time_left = StringProperty('TIME LEFT: --:--')

    # not working (maybe finish later)
    def update_time_on_label(self, time_end):
        text = f'TIME LEFT: {round(time_end - time.time(), 2)}'
        self.manager.get_screen('session_key_generator_screen').time_left = text

    def handle_session_key_generation(self):
        mac_address = getmac.get_mac_address()
        mac_address_groups = re.findall('[0-9a-f][0-9a-f]', mac_address)
        t_end = time.time() + 5
        counter = 0
        while time.time() < t_end:
            time.sleep(0.01)
            position = pyautogui.position()
            x = position.x if int(position.x) > 0 else -position.x
            y = position.y if int(position.y) > 0 else -position.y
            group = int(mac_address_groups[counter%6], base=16)
            self.key_int += (x + y) * group * group * int(time.time())
            counter += 1
            # self.update_time_on_label(t_end)
            
        self.key_str = str(self.key_int ** 2)[0:32]
        print(self.key_str.encode('utf-8'))

        if self.key_int is not None:
            popUp(PopUpMode.SUCCESS_SESSION_KEY)
        else:
            popUp(PopUpMode.ERROR_SESSION_KEY)


# Getting 'database' of users
users_data_path = 'users.csv'
users = pd.read_csv(users_data_path, usecols=['Login','Password'])
users_list = list(users['Login'])
pwds_list = list(users['Password'])
currently_logged_user = None


# Setting application layout
kv = Builder.load_file('ApplicationLayout.kv')


# Class responsible for managing all screeens
class screenManager(ScreenManager): 
    pass

# Creating screen manager for managing all screens of application
screen_manager = ScreenManager()
screen_manager.add_widget(loginScreen(name='login_screen'))
screen_manager.add_widget(chooserSenderScreen(name='chooser_screen'))
screen_manager.add_widget(signupScreen(name='signup_screen'))
screen_manager.add_widget(messageSenderScreen(name='message_sender_screen'))
screen_manager.add_widget(fileSenderScreen(name='file_sender_screen'))
screen_manager.add_widget(sessionKeyGeneratorScreen(name='session_key_generator_screen'))

# Class responsible for handling application start up
class CryptoApplicationMain(App): 
    def build(self):
        connection.ListenningThread().start()
        return screen_manager
