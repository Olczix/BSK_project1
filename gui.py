
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.screenmanager import ScreenManager, Screen 
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from pop_ups import PopUpMode, popUp
from kivy.uix.label import Label
from kivy.lang import Builder
from kivy.app import App
import network_connection
import backend
import time
import os


# Class responsible for handling loging in
class loginScreen(Screen):
    login = ObjectProperty(None)
    password = ObjectProperty(None)

    def login_btn_clicked(self):
        action_result = backend.validate_login(login=self.login.text, password=self.password.text)

        if action_result == PopUpMode.SUCCESS_LOG_IN:
            screen_manager.current = 'chooser_screen'
            popUp(PopUpMode.SUCCESS_LOG_IN)
        else:
            popUp(action_result)
            self.login.text = ""
            self.password.text = ""

# Class responsible for handling signing up and validating entered user's credentials
class signupScreen(Screen):
    login = ObjectProperty(None)
    password = ObjectProperty(None)
    repeat_password = ObjectProperty(None)

    def create_account_btn_clicked(self):
        action_result = backend.validate_account_creation(login=self.login.text,
                                                          password=self.password.text,
                                                          repeat_password=self.repeat_password.text)

        if action_result == PopUpMode.SUCCESS_SIGN_IN:
            screen_manager.current = 'chooser_screen'
            popUp(PopUpMode.SUCCESS_SIGN_IN)
        else:
            popUp(action_result)
            self.login.text = ''
            self.password.text = ''
            self.repeat_password.text = ''

# Class responsible for handling users choice: send message, send file, generate session key
class chooserSenderScreen(Screen): 
    pass

# Class responsible for handling messages sending
class messageSenderScreen(Screen):
    message = ObjectProperty(None)
    encryption_mode = ObjectProperty(None)

    def set_block_encoding_choice(self, instance, value, block_encoding_choice):
        if value == True:
            self.encryption_mode = block_encoding_choice

    def send(self):
        # add validation if encryption_mode is empty/None
        backend.send_message(message=self.message.text,
                             encryption_mode=self.encryption_mode)
        self.message.text = ""
        # add PopUp message about success or failure while sending message

# Class responsible for handling files sending
class fileSenderScreen(Screen):
    file_path = None
    encryption_mode = ObjectProperty(None)

    def set_block_encoding_choice(self, instance, value, block_encoding_choice):
        if value == True:
            self.encryption_mode = block_encoding_choice

    def run_file_chooser_app(self):
        self.file_path = backend.get_chosen_file_path()

    def send(self):
        if backend.validate_file_sending(path=self.file_path,
                                         mode=self.encryption_mode):
            backend.send_file(path=self.file_path, mode=self.encryption_mode)


# Class responsible for handling session key generation
class sessionKeyGeneratorScreen(Screen):
    time_left = StringProperty('TIME LEFT: --:--')

    # not working (maybe finish later)
    def update_time_on_label(self, time_end):
        text = f'TIME LEFT: {round(time_end - time.time(), 2)}'
        self.manager.get_screen('session_key_generator_screen').time_left = text

    def handle_session_key_generation(self):
        popUp(backend.generate_session_key())

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
        network_connection.ListenningThread().start()
        return screen_manager
