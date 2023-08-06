from socketssh import server

server_object = server()

server_object.socket_connect(9999, 1024)

server_object.rabbit_connect('127.0.0.1', 5672, 'admin', '123456', 'code')

server_object.socket_start()
