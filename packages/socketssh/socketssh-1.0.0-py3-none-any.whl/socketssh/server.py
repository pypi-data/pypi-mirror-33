# !/usr/bin/python
# coding=UTF-8 

"""socketssh服务端"""

__author__ = "Jiegl"

import socket
import pika
import threading


class Server:

    def __init__(self):

        # socket列表
        self.socket_list = []

        # socket监听端口
        self.socket_port = None

        # socket最大连接数
        self.socket_max = None

        # socket对象
        self.s = None

        # rabbit的地址
        self.rabbit_ip = None

        # rabbit的端口
        self.rabbit_port = None

        # rabbit的用户名
        self.rabbit_user = None

        # rabbit的密码
        self.rabbit_password = None

        # rabbit的队列名称
        self.rabbit_queue_value = None

        # rabbit初始化
        self.credentials = None

        # rabbit连接
        self.connection = None

        # rabbit实例
        self.channel = None

    def socket_connect(self, socket_max, socket_port):
        """
        :socket启动本地监听,等待客户端连接

        """
        # 启动一个socket对象
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # 监听9999端口
        self.socket_port = socket_port
        self.s.bind(('0.0.0.0', self.socket_port))

        # 调用listen()方法开始监听端口，传入的参数指定等待连接的最大数量：
        self.socket_max = socket_max
        self.s.listen(self.socket_max)

    def rabbit_connect(self, rabbit_ip, rabbit_port, rabbit_user, rabbit_password, rabbit_queue_value):
        """
        :rabbit连接,并且声明队列。

        """
        self.rabbit_ip = rabbit_ip
        self.rabbit_port = rabbit_port
        self.rabbit_user = rabbit_user
        self.rabbit_password = rabbit_password
        self.rabbit_queue_value = rabbit_queue_value
        self.credentials = pika.PlainCredentials(self.rabbit_user, self.rabbit_password)
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(self.rabbit_ip, self.rabbit_port, '/', self.credentials))
        self.channel = self.connection.channel()

        # 在两个程序中重复声明队列。
        self.channel.queue_declare(queue=self.rabbit_queue_value, durable=True)

    def rabbit_insert(self, code):
        # RabbitMQ消息不能直接发送到队列，它总是需要通过交换。
        self.channel.basic_publish(exchange='',
                                   routing_key=self.rabbit_queue_value,
                                   body=code,
                                   properties=pika.BasicProperties(
                                       delivery_mode=2,  # make message persistent
                                   )
                                   )
        print(" [x] Sent 'ok'")
        self.connection.close()

    def __callback(self, ch, method, properties, body):
        """
        :rabbit接受到数据后的处理函数

        """
        for sock in self.socket_list:
            sock["sock"].send(body.encode('utf-8'))
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def __send(self, sock, addr):
        """
        :多线程调用的函数,主要负责处理rabbitmq队列里面的数据

        """
        self.channel.basic_consume(self.__callback, queue=self.rabbit_queue_value, )
        self.channel.start_consuming()

    def socket_start(self):
        """
        :开启服务端代码,监听端口连接过来的线程，并且提取rabbitmq队列里面的信息，下发到客户端

        """
        while True:
            # 接受TCP连接并返回（sock,address）,其中sock是新的套接字对象，可以用来接收和发送数据。address是连接客户端的地址。
            sock, addr = self.s.accept()

            tmp = {"sock": sock, "addr": addr}
            self.socket_list.append(tmp)

            # 创建发送线程来处理TCP连接：
            send_threading = threading.Thread(target=self.__send, args=(sock, addr))
            send_threading.start()
