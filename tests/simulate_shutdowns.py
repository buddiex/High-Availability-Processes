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


def main(simulate_type):
    if simulate_type == 'primary_shutdown':
        send_primay_shutdown()
    if simulate_type == 'backup_shutdown':
        send_backup_shutdown()
    # send_backup_shutdown()



# python .\higha.py server
# python .\higha.py simulate -type primary_shutdown
# python .\higha.py simulate -type backup_shutdown
# Get-Process | where ProcessName -Match python
# Stop-Process -Name python
# Get-Content -Path "haha.log" -Wait
