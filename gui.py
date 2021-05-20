from logic_connection import Logic_Connection
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.progressbar import ProgressBar
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from pop_ups import PopUpMode, popUp
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from kivy.lang import Builder
from kivy.app import App
import network_connection
import backend
import config
import time
import os


# Class responsible for handling loging in
class loginScreen(Screen):
    login = ObjectProperty(None)
    password = ObjectProperty(None)

    def login_btn_clicked(self):
        action_result = backend.validate_login(login=self.login.text, password=self.password.text)

        if action_result == PopUpMode.SUCCESS_LOG_IN:
            screen_manager.current = 'session_initialization_screen'
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
            screen_manager.current = 'session_initialization_screen'
            popUp(PopUpMode.SUCCESS_SIGN_IN)
        else:
            popUp(action_result)
            self.login.text = ''
            self.password.text = ''
            self.repeat_password.text = ''

# Class responsible for handling users choice: send message, send file, generate session key
class menuScreen(Screen):
    pass

# Class responsible for handling messages sending
class messageSenderScreen(Screen):
    message = ObjectProperty(None)
    encryption_mode = ObjectProperty(None)

    def set_block_encoding_choice(self, instance, value, block_encoding_choice):
        if value == True:
            self.encryption_mode = block_encoding_choice

    def send_message(self):
        # add validation if encryption_mode is empty/None
        action_result = backend.send_message(message=self.message.text,
                                             encryption_mode=self.encryption_mode)
        self.message.text = ""
        popUp(action_result)

# Class responsible for handling files sending
class fileSenderScreen(Screen):
    file_path = None
    encryption_mode = ObjectProperty(None)

    def set_block_encoding_choice(self, instance, value, block_encoding_choice):
        if value == True:
            self.encryption_mode = block_encoding_choice

    def run_file_chooser_app(self):
        self.file_path = backend.get_chosen_file_path()

    def send_file(self):
        if backend.validate_file_sending(path=self.file_path,
                                         mode=self.encryption_mode):
            backend.init_file_sender(path=self.file_path,
                                     encryption_mode=self.encryption_mode)

# Class responsible for handling logic connection initialization
class sessionInitializationScreen(Screen):
    ip_address = ObjectProperty(None)

    def save_ip_addres(self):
        if backend.validate_ip_address(self.ip_address.text):
            screen_manager.current = 'session_key_generator_screen'

# Class responsible for handling session key generation
class sessionKeyGeneratorScreen(Screen):
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
screen_manager.add_widget(menuScreen(name='menu_screen'))
screen_manager.add_widget(signupScreen(name='signup_screen'))
screen_manager.add_widget(messageSenderScreen(name='message_sender_screen'))
screen_manager.add_widget(fileSenderScreen(name='file_sender_screen'))
screen_manager.add_widget(sessionKeyGeneratorScreen(name='session_key_generator_screen'))
screen_manager.add_widget(sessionInitializationScreen(name='session_initialization_screen'))

# Class responsible for handling application start up
class CryptoApplicationMain(App): 
    def build(self):
        return screen_manager
