'''
    Copyright (c) 2016-2017 Wind River Systems, Inc.
    
    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at:
    http://www.apache.org/licenses/LICENSE-2.0
    
    Unless required by applicable law or agreed to in writing, software  distributed
    under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES
    OR CONDITIONS OF ANY KIND, either express or implied.
'''

"""
This module contains the Relay class which is a secure way to pipe data to a
local socket connection. This is useful for Telnet which is not secure by
default.
"""

import logging
import random
import select
import socket
import ssl
import threading

# yocto supports websockets, not websocket, so check for that
try:
    import websocket
except ImportError:
    import websockets as websocket

CONNECT_MSG = "CONNECTED-129812"

class Relay(object):
    """
    Class for establishing a secure pipe between a cloud based websocket and a
    local socket. This is useful for things like Telnet which are not secure to
    use remotely.
    """

    def __init__(self, wsock_host, sock_host, sock_port, secure=True,
                 log=None):
        """
        Initialize a relay object for piping data between a websocket and a
        local socket
        """

        self.wsock_host = wsock_host
        self.sock_host = sock_host
        self.sock_port = sock_port
        self.secure = secure
        self.log = log
        self.log_name = "Relay:{}:{}({:0>5})".format(self.sock_host,
                                                    self.sock_port,
                                                    random.randint(0,99999))

        if self.log is None:
            self.logger = logging.getLogger(self.log_name)
            log_handler = logging.StreamHandler()
            #log_formatter = logging.Formatter(constants.LOG_FORMAT, datefmt=constants.LOG_TIME_FORMAT)
            #log_handler.setFormatter(log_formatter)
            self.logger.addHandler(log_handler)
            self.logger.setLevel(logging.DEBUG)
            self.log = self.logger.log

        self.running = False
        self.thread = None
        self.lsock = None
        self.wsock = None

    def _loop(self):
        """
        Main loop that pipes all data from one socket to the next. The websocket
        connection is established first so this is also where the local socket
        connection will be started when a specific string is received from the
        Cloud
        """
        lconnect = 0;
        while self.running is True:
            # Continuously receive data from each socket and send it through the
            # other
            socket_list = [self.wsock]
            if self.lsock:
                socket_list.append(self.lsock)
            read_sockets, _ws, _es = select.select(socket_list, [], [], 1)
            for sock in read_sockets:
                if sock == self.wsock:
                    try:
                        op, data_in = sock.recv_data()
                    except websocket.WebSocketConnectionClosedException:
                        self.running = False
                        break
                    if data_in:
                        if self.lsock:
                            self.lsock.send(data_in)
                        elif lconnect == 0 and data_in.decode('ascii') == CONNECT_MSG:
                            # If the local socket has not been established yet,
                            # and we have received the connection string, start
                            # local socket.
                            try:
                                self.lsock = socket.socket(socket.AF_INET,
                                                           socket.SOCK_STREAM)
                                self.lsock.connect((self.sock_host,
                                                    self.sock_port))
                            except socket.error:
                                self.running = False
                                self.log(logging.ERROR,
                                         "%s - Failed to open local socket",
                                         self.log_name)
                                break

                            lconnect = 1;
                            self.log(logging.INFO,
                                    "%s - Local socket successfully opened",
                                     self.log_name)
                    else:
                        self.log(logging.INFO,
                                 "%s - Received NULL from websocket, Stopping",
                                 self.log_name)
                        self.running = False
                        break
                elif self.lsock and sock == self.lsock:
                    data_in = sock.recv(4096)
                    if data_in:
                        self.wsock.send_binary(data_in)
                    else:
                        self.log(logging.INFO,
                                 "%s - Received NULL from socket, Stopping",
                                 self.log_name)
                        self.running = False
                        break
        if self.lsock:
            self.lsock.close()
            self.lsock = None
        self.wsock.close()
        self.wsock = None
        self.log(logging.INFO, "%s - Sockets Closed", self.log_name)

    def start(self):
        """
        Establish the websocket connection and start the main loop
        """

        if not self.running:
            self.running = True

            sslopt = {}
            if not self.secure:
                sslopt["cert_reqs"] = ssl.CERT_NONE

            # Connect websocket to Cloud
            self.wsock = websocket.WebSocket(sslopt=sslopt)
            try:
                self.wsock.connect(self.wsock_host)
            except ssl.SSLError as error:
                self.running = False
                self.wsock.close()
                self.wsock = None
                self.log(logging.ERROR, "%s - Failed to open Websocket",
                         self.log_name)
                raise error

            self.log(logging.INFO, "%s - Websocket Opened", self.log_name)

            self.thread = threading.Thread(target=self._loop)
            self.thread.start()

        else:
            raise RuntimeError("{} - Already running!".format(self.log_name))

    def stop(self):
        """
        Stop piping data between the two connections and stop the loop thread
        """

        self.log(logging.INFO, "%s - Stopping", self.log_name)
        self.running = False
        if self.thread:
            self.thread.join()
            self.thread = None


relays = []

def create_relay(url, host, port, secure=True, log_func=None, reconnect=False,local_socket=None):
    global relays

    newrelay = Relay(url, host, port, secure=secure, log=log_func)
    newrelay.start()
    relays.append(newrelay)

def stop_relays():
    global relays

    threads = []
    while relays:
        relay = relays.pop()
        thread = threading.Thread(target=relay.stop)
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

