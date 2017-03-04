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

{
  "player": (x,y),
  "mines": []
}
class Player:
  def __init__(self, HOST, PORT, LOGIN):
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.sock.connect((HOST, PORT))
    print('LOGIN')
    self.sock.send((LOGIN+'\n').encode())
    print('success');
  def getRawArr(self):
    self.sock.send('STATUS\n'.encode())
    data = self.sock.recv(4096)
    arr = repr(data).split(' ')
    retval = dict()
    retval["playerpos"] = (float(arr[1]), float(arr[2]))
    retval["playervel"] = (float(arr[3]), float(arr[4]))
    
    int(arr[6]) #number of mines
    (float(arr[8+3*i]), float(arr[9+3*i]))
    retval["mines"] = minearray
  def getPositionVelocity(self):
    arr = self.getRawArr()
    return (float(arr[1]), float(arr[2]), float(arr[3]), float(arr[4]))
  def getNearestMine(self):
    arr = self.getRawArr()
    return (float(
  def waypoint(self, x, y): #fly through this point exactly. blocks until done.
    ##while not passed through:
    pass

try:
  p = Player(HOST, PORT, LOGIN)
  while True:
    print(p.getPositionVelocity())
    time.sleep(1)
catch
finally