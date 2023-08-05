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
import time
# -------------------------------------------------------------------
# Note: when using a proxy server, the socket class is overlayed with
# pysocks class.  Keep around a local copy so that local socket
# connections don't use the proxy
# -------------------------------------------------------------------
non_proxy_socket = None

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
                 log=None, local_socket=None, reconnect=False):
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
        self.reconnect = reconnect

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
        self.lconnect = 0

    def _connect_local(self):
        ret = False
        try:
            # check for proxy.  If not proxy, this
            # is None.
            if non_proxy_socket:
                self.lsock = non_proxy_socket(socket.AF_INET,
                                       socket.SOCK_STREAM)
            else:
                self.lsock = socket.socket(socket.AF_INET,
                                       socket.SOCK_STREAM)
                self.lsock.setblocking(0)
                print("local socket {}".format(self.lsock))

                # disable nagle
                self.lsock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)
            self.lsock.connect((self.sock_host,
                                self.sock_port))
        except socket.error:
            self.running = False
            ret = True
            print("%s - Failed to open local socket",
                     self.log_name)
        return ret

    def _loop(self):
        """
        Main loop that pipes all data from one socket to the next. The websocket
        connection is established first so this is also where the local socket
        connection will be started when a specific string is received from the
        Cloud
        """
        print ("_loop: wsock {}".format(self.wsock)) 
        while True:
            socket_list = [self.lsock]

            # need a select loop here for the local socket
            read_sockets, write_sockets, _es = select.select(socket_list, [], [], 1)
            if len(read_sockets):
                print("_loop: local socket has data")
                data = self.lsock.recv(4096)
                if data:
                    print ("_loop: sending local data to ws")
                    self.wsock.send(str(data).encode('utf-8'))
            else:
                print("_loop: waiting for data")
            time.sleep(1)

    def _on_open(self, ws):
        print("_on_open: Connecting to local port")
        self.thread = threading.Thread(target=self._loop)
        self.thread.start()
        


    def _on_message(self, ws, data):
        print("_on_message: Received ws message {}".format(len(data)))
        print ("_on_message: wsock {}".format(self.wsock)) 

        if data:
            if data == CONNECT_MSG:
                # If the local socket has not been established yet,
                # and we have received the connection string, start
                # local socket.
                self._connect_local()
                self.lconnect = 1;
                print( "%s - Local socket successfully opened",
                         self.log_name)
            else:
                # send to local socket
                print("sending data to local socket {}".format(self.lsock))
                self.lsock.send(str(data).encode('utf-8'))
                self._loop()

        
    def _on_error(self, ws, exception):
        print("_on_error: {}".format(str(exception)))

    def _on_close(self,  ws):
        print("_on_close: closing sockets")
        


    def start(self):
        """
        Establish the websocket connection and start the main loop
        """

        if not self.running:
            self.running = True

            sslopt = {}
            if not self.secure:
                sslopt["cert_reqs"] = ssl.CERT_NONE

            self.wsock = websocket.WebSocketApp( 
                    self.wsock_host, on_message=self._on_message,
                    on_error=self._on_error,
                    on_close=self._on_close)
            print ("wsock {}".format(self.wsock)) 
            # Connect websocket to Cloud
            threading.Thread(target=self.wsock.run_forever).start()

        else:
            raise RuntimeError("{} - Already running!".format(self.log_name))

    def stop(self):
        """
        Stop piping data between the two connections and stop the loop thread
        """

        self.log(logging.INFO, "%s - Stopping", self.log_name)
        self.running = False
        self.reconnect = False
        if self.thread:
            self.thread.join()
            self.thread = None


relays = []

def create_relay(url, host, port, secure=True, log_func=None, local_socket=None,
                 reconnect=False):
    global relays, non_proxy_socket

    non_proxy_socket = local_socket
    newrelay = Relay(url, host, port, secure=secure, log=log_func, reconnect=reconnect)
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

