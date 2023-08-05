from __future__ import unicode_literals

import socket
from time import time

from .conf import settings

_host_name = socket.gethostname()


def get_hostname():
    return settings.CARBON_HOSTNAME or _host_name


def row_format(hostame, metric, value, stamp):
    full_metric = "%s.%s" % (hostame, metric)
    if settings.CARBON_PREFIX:
        full_metric = "%s.%s" % (settings.CARBON_PREFIX, full_metric)

    return "%s %d %d" % (full_metric, value, stamp)


def send_buff(port, buff):
    msg = "\n".join(buff)
    msg += "\n"

    msg = msg.encode('utf-8')

    if settings.CARBON_TRANSPORT == 'udp':
        fd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        fd.sendto(msg, (settings.CARBON_HOST, port))
    else:
        fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        fd.connect((settings.CARBON_HOST, port))
        fd.send(msg)
    fd.close()


def send(metric, value, stamp=None, aggregator=False):
    stamp = stamp or time()

    buff = [row_format(get_hostname(), metric, value, stamp)]

    if settings.CARBON_SEND_ALL:
        buff.append(row_format('all',
                               metric, value,
                               stamp))
    if aggregator and settings.CARBON_AGGREGATOR_PORT:
        port = settings.CARBON_AGGREGATOR_PORT
    else:
        port = settings.CARBON_PORT
    send_buff(port, buff)


def send_time(metric, value, stamp=None):
    stamp = stamp or time()
    buff = list()
    buff.append(row_format(get_hostname(),
                           metric+'.time',
                           value,
                           stamp))

    if settings.CARBON_SEND_ALL:
        buff.append(row_format('all',
                               metric+'.time',
                               value,
                               stamp))

    if settings.CARBON_SEND_COUNT:
        buff.append(row_format(get_hostname(),
                               metric+'.count',
                               1,
                               stamp))

    if settings.CARBON_SEND_COUNT and settings.CARBON_SEND_ALL:
        buff.append(row_format('all',
                               metric+'.count',
                               1,
                               stamp))

    send_buff(settings.CARBON_AGGREGATOR_PORT or settings.CARBON_PORT,
              buff)
