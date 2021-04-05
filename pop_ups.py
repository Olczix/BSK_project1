from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup 
import enum

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
    
    window = Popup(title = info, content = show,
                   size_hint = (None, None), size = (350, 150)) 
    window.open()
