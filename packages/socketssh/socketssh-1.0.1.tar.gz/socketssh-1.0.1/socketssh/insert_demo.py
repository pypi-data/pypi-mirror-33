from socketssh import server

server_object = server()

server_object.rabbit_connect('192.168.199.246', '5672', 'admin', '123456', 'code')

server_object.rabbit_insert("touch /root/demo")
