import  os


RUNNING = ''
DEBUG_MODE = True
LOG = "haha"
MIN_TCP_PORT_NUM, MAX_TCP_PORT_NUM = (1, 65535)  # range of values for valid port numbers
MESSAGE_COUNT_MIN, MESSAGE_COUNT_MAX = (5, 8)  # number of messages to send, min and max
MESSAGE_DELAY_MIN, MESSAGE_DELAY_MAX = (2, 4)  # delay between messages to send in seconds, min and max

PROXY_2_CLIENT_IP = 'localhost'  # recieve request from clients
PROXY_2_CLIENT_PORT = 9999
PROXY_COMM_IP = 'localhost'  # listen for shutdown and primary register command
PROXY_COMM_PORT = 9997  #


PRIMARY_SERVER_2_PROXY_IP = 'localhost'  # default to server on this host
PRIMARY_SERVER_2_PROXY_PORT = 9998  # default to port 10000 on this host
PRIMARY_SERVER_SHUTDOWN_IP = 'localhost'  # default to server on this host
PRIMARY_SERVER_SHUTDOWN_PORT = 9996  # default to port 10000 on this host
PRIMARY_SERVER_HEARTBEAT_IP = 'localhost'  # default to server on this host
PRIMARY_SERVER_HEARTBEAT_PORT = 9995  # default to port 10000 on this host
PRIMARY_SERVER_UPDATE_IP = 'localhost'  # default to server on this host
PRIMARY_SERVER_UPDATE_PORT = 9990  # default to port 10000 on this host

# python
# "C:/dev/ha_server/higha.py"
# server - tpfile
# "sample_tuple_file.db.json" - tpsap
# "('localhost', 9994)" - shutdown
# "('localhost', 9993)" - heartbeat
# "('localhost', 9992)" - backup
# "('localhost', 9998)" - bk_shutdown
# "('localhost', 9994)" - proxy
# "('localhost', 9995)" - -is_primary
# "('localhost', 9997)" - primary_id
# "false"

BACKUP_SERVER_2_PROXY_IP = 'localhost'  # default to server on this host
BACKUP_SERVER_2_PROXY_PORT = 9994  # default to port 10000 on this host
BACKUP_SERVER_SHUTDOWN_IP = 'localhost'  # default to server on this host
BACKUP_SERVER_SHUTDOWN_PORT = 9993  # default to port 10000 on this host
BACKUP_SERVER_HEARTBEAT_IP = 'localhost'  # default to server on this host
BACKUP_SERVER_HEARTBEAT_PORT = 9992  # default to port 10000 on this host
BACKUP_SERVER_UPDATE_IP = 'localhost'  # default to server on this host
BACKUP_SERVER_UPDATE_PORT = 9991  # default to port 10000 on this host

HEARTBEAT_WAIT_TIME = 5
BEAT_PERIOD = 2

TUPLE_SPACE_JSON = "sample_tuple_file.db.json"

MAX_CLIENT_CONN_ATTEMPT = 5
MAX_CLIENT_COUNT = 5

def bytes_in_representation(value):
    return (value.bit_length() + 7) // 8


BYTES_PER_SHORT = bytes_in_representation(2 ** 16 - 1)


################################# for testing ######################
BASE_URL = 'http://jsonplaceholder.typicode.com'
SKIP_TAGS = os.getenv('SKIP_TAGS', '').split()