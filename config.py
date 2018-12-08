import  os


DEBUG_MODE = True
MIN_TCP_PORT_NUM, MAX_TCP_PORT_NUM = (1, 65535)  # range of values for valid port numbers
MESSAGE_COUNT_MIN, MESSAGE_COUNT_MAX = (5, 8)  # number of messages to send, min and max
MESSAGE_DELAY_MIN, MESSAGE_DELAY_MAX = (2, 4)  # delay between messages to send in seconds, min and max

PROXY_DEFAULT_HOST = 'localhost'  # default to server on this host
PROXY_DEFAULT_PORT = 11000  # default to port 10000 on this host
SERVER_DEFAULT_HOST = 'localhost'  # default to server on this host
SERVER_DEFAULT_PORT = 9999  # default to port 10000 on this host
MAX_CLIENT_CONN_ATTEMPT = 5
MAX_CLIENT_COUNT = 5

def bytes_in_representation(value):
    return (value.bit_length() + 7) // 8


BYTES_PER_SHORT = bytes_in_representation(2 ** 16 - 1)


################################# for testing ######################
BASE_URL = 'http://jsonplaceholder.typicode.com'
SKIP_TAGS = os.getenv('SKIP_TAGS', '').split()