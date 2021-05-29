from typing import Text
from kivy.core import text
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.progressbar import ProgressBar
from kivy.properties import ObjectProperty
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.clock import Clock
from time import sleep
import backend
import enum


TIME_INTERVAL = 0.5

# Possible pop ups types/modes
class PopUpMode(enum.Enum):
    ERROR_INVALID_INFORMATION = 0
    ERROR_SESSION_KEY = 1
    SUCCESS_LOG_IN = 2
    SUCCESS_SIGN_IN = 3
    SUCCESS = 4
    SUCCESS_SESSION_KEY = 5
    ERROR_UNKNOWN_USER = 6
    ERROR_USER_EXISTS = 7
    CHOSEN_FILE_CONFIRMATION = 8
    NO_ENCRYPTION_MODE_SELECTED = 9
    NO_FILE_SELECTED = 10
    SUCCESS_MESSAGE_SEND = 11
    SUCCESS_FILE_SEND = 12
    NO_SESSION_KEY_GENERATED = 13
    ERROR_INCORRECT_IP_ADDRESS_FORMAT = 14
    SUCCESS_CONNECTTION = 15

# Classes implementing particular errors/infos
class errorInvalidInformation(FloatLayout): 
    pass

class errorSessionKey(FloatLayout): 
    pass

class successLogIn(FloatLayout): 
    pass

class successSignIn(FloatLayout): 
    pass

class success(FloatLayout):
    pass

class errorUnknownUser(FloatLayout):
    pass

class successSessionKey(FloatLayout):
    pass

class errorUserExists(FloatLayout):
    pass

class chosenFileConfirmation(FloatLayout):
    pass

class noEncryptionModeSelected(FloatLayout):
    pass

class noFileSelected(FloatLayout):
    pass

class successMessageSend(FloatLayout):
    pass

class successFileSend(FloatLayout):
    pass

class noSessionKeyGenerated(FloatLayout):
    pass

class errorIncorrectIpAddressFormat(FloatLayout):
    pass

class successConnection(FloatLayout):
    pass

# Class responsible for displaying progress bar while sending large files
class ProgressBarFileSender(Widget):
    progress_bar = ObjectProperty()
     
    def __init__(self, f, encryption_mode):
        self.file = f
        self.encryption_mode = encryption_mode

        # send FILE_TRANSFER_CONFIGURATION message
        backend.send_file_transfer_config(encryption_mode=self.encryption_mode,
                                          file=self.file)

        self.iterator = 0
        self.percentage_interval = 100/self.file.no_of_packets
        self.progress_bar = ProgressBar()
        self.popup = Popup(
            title ='Sending ...',
            content = self.progress_bar
        )
        self.pop()
 
    def pop(self):
        self.progress_bar.value = 1
        self.popup.open()
        self.puopen(self.popup)
 
    def next(self, dt):
        # send each file chunk using our custom communication protocol
        if self.iterator < self.file.no_of_chunks:
            backend.send_file_chunk(chunk=self.file.chunks[self.iterator], file=self.file, chunk_number=self.iterator)
            print(f'chunk id = {self.iterator + 1} out of {self.file.no_of_chunks}')
            self.iterator += 1
            self.progress_bar.value += self.percentage_interval
        else:
            self.popup.dismiss()

    def puopen(self, instance):
        Clock.schedule_interval(self.next, TIME_INTERVAL)


# Class responsible for displaying newly arrived message
class NewMessage(Widget):
    def __init__(self, msg, address):
        self.address = address

        # New message popup setup = label with message + button to response
        label = Label(text=msg, size_hint=(0.99, 0.8))
        btn = Button(text="Send response now!", size_hint=(0.3, 0.15))
        btn.bind(on_press=self.send_response_now)
        box = BoxLayout(orientation='vertical', spacing=5)
        box.add_widget(label)
        box.add_widget(btn)

        self.new_message = Popup(
            title = f'New message from {self.address} has arrived!',
            size_hint = (0.8, 0.8),
            content=box
        )
        self.new_message.open()

    
    def send_response_now(self, event):
        # Response popup setup = tex input + button to send response
        self.text_input = TextInput(size_hint=(0.90, 0.8))
        btn = Button(text="Send!", size_hint=(0.3, 0.15))
        btn.bind(on_press=self.send_msg)
        box = BoxLayout(orientation='vertical', spacing=5)
        box.add_widget(self.text_input)
        box.add_widget(btn)

        self.new_message.dismiss()
        self.send_response = Popup(
            title = f'Sending response to {self.address}... (default ECB encoding)',
            size_hint = (0.8, 0.8),
            content=box
        )
        self.send_response.open()
    
    def send_msg(self, event):
        backend.send_message(message=self.text_input.text, encryption_mode='CBC')
        self.send_response.dismiss()
        popUp(PopUpMode.SUCCESS_MESSAGE_SEND)
    

# Class responsible for informing user about receiving new file from another user
class NewFileArrival(Widget):
    def __init__(self, address, number, extention):

        all_chunks = backend.file_to_save.no_of_chunks
        current_chunk_number = number + 1
        label = Label(text=f'Receiving file packages: {current_chunk_number} out of {all_chunks}',
                      size_hint=(0.99, 0.4))
        box = BoxLayout(orientation='vertical', spacing=5)
        box.add_widget(label)
        new_file_arrival = Popup(
            title = f'File from {address} transfer progress ...',
            size_hint = (0.5, 0.2),
            pos_hint={'x': 0.5, 
                      'y': 0.0},
            content=box
        )
        new_file_arrival.open()
        sleep(TIME_INTERVAL)
        new_file_arrival.dismiss()

        if all_chunks == current_chunk_number:
            NameForNewFile(extention)


# Class responsible for asking user for naming a newly received file
class NameForNewFile(Widget):
    def __init__(self, extension):
        self.extension = extension
        
        # popup setup = label asking for typing name + text input + button to set name
        self.label = Label(text=f'Type a name for file (.{extension}):',
                      size_hint=(0.99, 0.4))
        self.text_input = TextInput(size_hint=(0.99, 0.4))
        self.btn = Button(text="Set file name", size_hint=(0.3, 0.15))
        self.btn.bind(on_press=self.set_file_name)
        box = BoxLayout(orientation='vertical', spacing=5)
        box.add_widget(self.label)
        box.add_widget(self.text_input)
        box.add_widget(self.btn)

        self.new_file_name = Popup(
            title = f'You can change name of file which has just arrived!',
            size_hint = (0.45, 0.35),
            content=box
        )
        self.new_file_name.open()
    
    # Set file name and save empty file with given name and extension
    def set_file_name(self, event):
        backend.change_file_name(self.text_input.text, extension=self.extension)     


# Definition of pop up content (title and text)
def popUp(mode, extra_info=None):
    show = None
    info = 'INFO INFO'
    if mode.value == 0:
        info = 'ERROR'
        show = errorInvalidInformation()
    elif mode.value == 1:
        info = 'ERROR'
        show = errorSessionKey()
    elif mode.value == 2:
        info = 'INFO'
        show = successLogIn()
    elif mode.value == 3:
        info = 'INFO'
        show = successSignIn()
    elif mode.value == 4:
        info = 'INFO'
        show = success()
    elif mode.value == 5:
        info = 'INFO'
        show = successSessionKey()
    elif mode.value == 6:
        info = 'ERROR'
        show = errorUnknownUser()
    elif mode.value == 7:
        info = 'ERROR'
        show = errorUserExists()
    elif mode.value == 8:
        info = 'ERROR' if extra_info is None else extra_info 
        show = chosenFileConfirmation()
    elif mode.value == 9:
        info = 'ERROR'
        show = noEncryptionModeSelected()
    elif mode.value == 10:
        info = 'ERROR'
        show = noFileSelected()
    elif mode.value == 11:
        info = 'INFO'
        show = successMessageSend()
    elif mode.value == 12:
        info = 'INFO'
        show = successFileSend()
    elif mode.value == 13:
        info = 'ERROR'
        show = noSessionKeyGenerated()
    elif mode.value == 14:
        info = 'ERROR'
        show = errorIncorrectIpAddressFormat()
    elif mode.value == 15:
        info = 'INFO'
        show = successConnection()
    
    window = Popup(title = info, content = show,
                   size_hint = (0.5, 0.4)) 
    window.open()
