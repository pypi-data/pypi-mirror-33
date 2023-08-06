# -*- coding: utf-8 -*-
from socketpool import ConnectionPool, Connector, TcpConnector
import socket
import select
import errno
import time
from time import sleep
import random
import json
import warnings
import os
import logging
import sys


class XLogerConnector(TcpConnector):
    def sendall(self, data, flags=0):
        return self._s.send(data, flags)

    pass


class XLogerClient(object):
    """

    """
    host = None
    port = None
    pool = None
    filter_backend = None

    @classmethod
    def config(cls, host="localhost", port=19100, factory=XLogerConnector, filter_backend='file:///tmp/xloger.filter'):
        cls.host = host
        cls.port = port
        cls.pool = ConnectionPool(factory=factory)
        cls.filter_backend = filter_backend

    @classmethod
    def start_filter_worker(cls, host, port, filter_backend='file:///tmp/xloger.filter', retry=0):
        logger = logging.getLogger("xloger_filter_worker")
        formatter = logging.Formatter(fmt='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        stdout_handler = logging.StreamHandler(stream=sys.stdout)
        stdout_handler.setFormatter(formatter)
        logger.addHandler(stdout_handler)
        logger.setLevel(logging.DEBUG)

        stderr = logging.getLogger("xloger_filter_worker_error")
        stderr_handler = logging.StreamHandler(stream=sys.stderr)
        stderr_handler.setFormatter(formatter)
        stderr.addHandler(stderr_handler)
        stderr.setLevel(logging.DEBUG)

        receiver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            receiver.connect((host, port))
        except socket.error as err:
            receiver.setblocking(0)
            receiver.close()
            stderr.warn("Connect to XLoger Server (%s:%s) Failed: [%s] %s" % (host, port, err[0], err[1]))
            sleep(3)
            cls.start_filter_worker(host, port, filter_backend, retry+1)
            return

        logger.info("XLoger Server (%s:%s) Connected." % (host, port))
        cls.filter_backend = filter_backend
        # non-blocking
        receiver.setblocking(0)
        data = dict(action="register", data=dict(duplex=True, reciever=True))
        receiver.send(json.dumps(data)+'\n')

        def reconnect():
            logger.info("Reconnecting XLoger Server (%s:%s)." % (host, port))
            cls.dispatch_filter(dict())
            receiver.close()
            sleep(3)
            cls.start_filter_worker(host, port, filter_backend)

        while True:
            try:
                line = receiver.makefile().readline()
            except socket.error as e:
                err = e.args[0]
                if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
                    sleep(1)
                    continue
                if err == errno.ECONNRESET:
                    reconnect()
                    break
                continue

            if line:
                cls.handle_package_data(line)
            else:
                try:
                    receiver.send(json.dumps(data)+'\n')
                except socket.error as e:
                    if e.errno == errno.ECONNRESET:
                        reconnect()
                        break

    @classmethod
    def send(cls, data):
        try:
            conn = cls.pool.get(host=cls.host, port=cls.port)
            conn.sendall(data)
        except Exception as e:
            print("XLoger push failed. %s" % e)

    @classmethod
    def push(cls, action='log',  data=''):
        data = dict(action=action, data=data)
        stream = json.dumps(data)+'\n'
        cls.send(stream)

    @classmethod
    def handle_package_data(cls, data):
        try:
            data = json.loads(data)
        except Exception as e:
            warnings.warn("Invalid data recieved.")
            return
        action, data = data.get("action", None), data.get("data", None)
        if not action or not isinstance(data, dict):
            warnings.warn("Invalid data recieved.")
            return
        cls.dispatch(action, data)

    @classmethod
    def dispatch(cls, action, data):
        action = getattr(cls, "dispatch_"+action, None)
        callable(action) and action(data)

    @classmethod
    def dispatch_filter(cls, filter):
        backend = cls.filter_backend
        if backend.startswith("file://"):
            try:
                filter_file_name = backend[7:]
                f = open(filter_file_name, "w+")
                f.write(json.dumps(filter))
                f.close()
            except Exception as e:
                warnings.warn("Failed to Write Xloger backend: %s" % e.message)

    @classmethod
    def filter(cls):
        backend = cls.filter_backend
        if backend.startswith("file://"):
            filter_file_name = backend[7:]
            try:
                f = open(filter_file_name, 'r+')
                data = f.read()
                if data:
                    return json.loads(data)
            except Exception as e:
                warnings.warn("Failed to read Xloger backend: %s" % e.message)
        return dict()




