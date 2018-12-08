import argparse
import config as conf
import socket


def port_parser(string, **kwargs):
    """ parse and validate port for receiving client connections """
    try:
        portnum = int(string)
        if portnum < conf.MIN_TCP_PORT_NUM:
            print('?? TCP port value (%d) too low; changing to %d' % (portnum, conf.MIN_TCP_PORT_NUM))
        else:
            if portnum > conf.MAX_TCP_PORT_NUM:
                print('?? TCP port value (%d) too high; changing to %d' % (portnum, conf.MAX_TCP_PORT_NUM))
        return max(min(portnum, conf.MAX_TCP_PORT_NUM), conf.MIN_TCP_PORT_NUM)
    except:
        syndrome = 'invalid port count: %s\ncount must be a positive integer in range %d - %d' % (
            string, conf.MIN_TCP_PORT_NUM, conf.MAX_TCP_PORT_NUM)
        raise argparse.ArgumentTypeError(syndrome)


def IPv4_addr_parser(string):
    """ validate an IPv4-style address """
    octets = string.split(".")
    try:
        assert len(octets) == 4 and all([0 <= int(value) <= 255 for value in octets])
        return string
    except:
        raise argparse.ArgumentTypeError('invalid IP address (%s): must be of the form num.num.num.num' % string)


def hostname_parser(string):
    """ validate a DNS-style hostname """
    try:
        hostaddr = socket.gethostbyname(string)
        return (string, hostaddr)
    except OSError as err:
        raise argparse.ArgumentTypeError('invalid hostname (%s): %s' % (string, str(err) or ''))


class ConnectionError(Exception):
    pass
