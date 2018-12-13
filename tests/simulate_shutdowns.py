from ha.commons.clients import ShortDownClient
import config as conf
from ha.commons.logger import get_module_logger

logger = get_module_logger(__name__)


def send_shutdown(host, port):
        shd = ShortDownClient(host, port)
        try:
            reply = shd.shortdown()
            reply = reply.data['payload']
        except ConnectionAbortedError as err:
            reply = "client is down"


def send_backup_shutdown():
    host, port = conf.BACKUP_SERVER_SHUTDOWN_IP, conf.BACKUP_SERVER_SHUTDOWN_PORT
    send_shutdown(host, port)


def send_primay_shutdown():
    host, port = conf.PRIMARY_SERVER_SHUTDOWN_IP, conf.PRIMARY_SERVER_SHUTDOWN_PORT
    send_shutdown(host, port)


def main():
    send_primay_shutdown()
    # send_backup_shutdown()



# Get-Process | where ProcessName -Match python
# Stop-Process -Name python
#  Get-Content -Path "haha.log" -Wait

if __name__ == '__main__':
    main()
