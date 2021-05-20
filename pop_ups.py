from kivy.uix.floatlayout import FloatLayout
from kivy.uix.progressbar import ProgressBar
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.uix.widget import Widget
import enum, time
import threading
import backend

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

# Class responsible for displaying progress bar while sending large files
class ProgressBarFileSender(Widget):
    progress_bar = ObjectProperty()
     
    def __init__(self, f, cryptor):
        self.file = f
        self.cryptor = cryptor
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
        if self.iterator < self.file.no_of_chunks:
            backend.send_file_chunk(chunk=self.file.chunks[self.iterator],
                            cryptor=self.cryptor)
            print(f'chunk id = {self.iterator}')
            self.iterator += 1
            self.progress_bar.value += self.percentage_interval
        else:
            self.popup.dismiss()

    def puopen(self, instance):
        Clock.schedule_interval(self.next, 1)


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
    
    window = Popup(title = info, content = show,
                   size_hint = (0.5, 0.4)) 
    window.open()
