# Connection configuration
HOST = '192.168.31.243'     # our IP address
ADDRESS = None              # IP address typed by user
PORT = 64623                # mutual port


# Communication protocol
PUBLIC_KEY_TYPE = b'1'
SESSION_KEY_TYPE = b'2'
JUST_TALK_TYPE = b'3'
FILE_TRANSFER_CONFIGURATION = b'4'
FILE_CHUNK = b'5'
RECEIVED_FILE_DIR = ".//received_files"


# Size of package/file chunk
PACKAGE_SIZE = 1024
