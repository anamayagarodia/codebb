import socket
import sys
import time

HOST, PORT = "codebb.cloudapp.net", 17429
LOGIN = "duckduckgoose goosegooseduck"
#HOST, PORT = "10.20.42.146", 17429
#LOGIN = "b b"

"""
STATUS
ACCELERATE ANGLE THRUST
BRAKE
BOMB X Y [TIMER=100]
SCAN X Y
SCOREBOARD
CONFIGURATIONS
"""

#def waypoint():
  

try:
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  sock.connect((HOST, PORT))
  
  print('> [LOGIN]')
  sock.send((LOGIN+'\n').encode())
  while True:
    print('> STATUS');
    sock.send('STATUS\n'.encode())
    data = sock.recv(4096)
    print(repr(data))
except:
  print("error", sys.exc_info()[0])
  raise
