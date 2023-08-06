#!/usr/bin/env python

# python 3
import os
import sys
import json
import socket
import datetime
import time

SPLUNK_TOKEN = os.getenv(
    'SPLUNK_TOKEN',
    None)


def format_record(
        token=None):
    """format_record

    :param token: existing splunk token
    """
    use_token = token
    if not use_token:
        use_token = SPLUNK_TOKEN
    if not use_token:
        print('missing token or env var for SPLUNK_TOKEN')
        return None
    log_dict = {
        'name': 'payments',
        'message': 'testing messages with json fields show up in splunk',
        'tags': [
            'ecomm',
            'payments',
            'subscriptions'
        ],
        'env': 'dev',
        'dc': 'openshift',
        'levelname': 'INFO',
        'time': time.time(),
        'date': datetime.datetime.utcnow().strftime(
            '%Y-%m-%d %H:%M:%S')
    }
    log_msg = ('token={}, body={}').format(
        SPLUNK_TOKEN,
        json.dumps(log_dict))
    return log_msg
# end of format_record


def run_main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('splunkenterprise', 1514))
    log_msg = format_record()
    is_py2 = sys.version[0] == '2'
    if is_py2:
        s.send(log_msg)
    else:
        s.send(log_msg.encode())
# end of run_main


if __name__ == 'main':
    run_main()
