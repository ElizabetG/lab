
import sys
HOST_NAME = sys.argv[1]
PORT_NUMBER = int(sys.argv[2])

import socket
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST_NAME, PORT_NUMBER))
client.send(sys.argv[3].encode('UTF-8'))
from_server = client.recv(4096)
client.close()
print (from_server)
