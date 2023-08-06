from socketssh import client

client_object = client()

client_object.socket_connect('192.168.199.246', 9999)

client_object.socket_start()
