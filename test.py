import socket
import sys
import time
import math


HOST, PORT = "codebb.cloudapp.net", 17429
USERNAME, PASSWORD = "duckduckgoose", "goosegooseduck"
#HOST, PORT = "localhost", 17429
#USERNAME, PASSWORD = "a", "a"

"""
STATUS
ACCELERATE ANGLE THRUST
BRAKE
BOMB X Y [TIMER=100]
SCAN X Y
SCOREBOARD
CONFIGURATIONS
"""

def squaredDistance(pos1, pos2 = (0,0)):
  return (pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2
def neg(pos):
  return (-pos[0], -pos[1])
def add(pos1, pos2):
  return (pos1[0] + pos2[0], pos1[1] + pos2[1])
def scale(k, pos):
  return (k*pos[0], k*pos[1])
def sub(pos1, pos2):
  return (pos1[0] - pos2[0], pos1[1] - pos2[1])
def dot(pos1, pos2):
  return pos1[0] * pos2[0] + pos1[1] * pos2[1]
def proj(a, b):
  factor = (dot(a,b) / squaredDistance(a))
  return (factor * a[0], factor * a[1])
def perp(a, b):
  return sub(b, proj(a, b))
def angle(pos):
  return math.atan2(pos[1], pos[0])

class Player:
  def __init__(self, HOST, PORT, USERNAME, PASSWORD):
    self.data = None
    self.rawData = None
    self.HOST = HOST
    self.PORT = PORT
    self.USERNAME = USERNAME
    self.PASSWORD = PASSWORD
  def __enter__(self):
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.sock.connect((self.HOST, self.PORT))
    self.sock.send((self.USERNAME + ' ' + self.PASSWORD+'\n').encode())
    print('hi')
    return self
  def __exit__(self, exc_type, exc_value, traceback):
    self.sock.close()
  def sendCommand(self, str):
    self.sock.send((str+'\n').encode())
    return repr(self.sock.recv(4096))
  def refreshData(self):
    data = self.sendCommand('STATUS')
    arr = data.split(' ')
    
    self.rawData = arr
    
    processed = dict()
    processed["pos"] = (float(arr[1]), float(arr[2]))
    processed["vel"] = (float(arr[3]), float(arr[4]))
    processed["ourmines"] = list()
    processed["mines"] = list()
    processed["players"] = list()
    processed["bombs"] = list()
    
    counter = 7
    nummines = int(arr[counter])
    for i in range(nummines): #x, y, owner (ONLY IF NOT OURS)
      if arr[counter + 1 + 3*i] != self.USERNAME:
        processed["mines"].append((float(arr[counter + 2 + 3*i]), float(arr[counter + 3 + 3*i]), arr[counter + 1 + 3*i]))
      else:
        processed["ourmines"].append((float(arr[counter + 2 + 3*i]), float(arr[counter + 3 + 3*i]), arr[counter + 1 + 3*i]))
    
    counter += 2 + 3 * nummines
    numplayers = int(arr[counter])
    for i in range(numplayers): #x, y, dx, dy
      processed["players"].append((float(arr[counter + 1 + 4*i]), float(arr[counter + 2 + 4*i]), float(arr[counter + 3 + 4*i]), float(arr[counter + 4 + 4*i])))
    
    counter += 2 + 4 * numplayers
    numbombs = int(arr[counter])
    for i in range(numbombs): #x, y
      processed["bombs"].append((float(arr[counter + 1 + 2*i]), float(arr[counter + 2 + 2*i])))
    
    processed["mines"].sort(key = lambda x: squaredDistance(x, processed["pos"]))
    processed["players"].sort(key = lambda x: squaredDistance(x, processed["pos"]))
    processed["bombs"].sort(key = lambda x: squaredDistance(x, processed["pos"]))
    
    self.data = processed
  def setAccel(self, angle, magnitude):
    self.sendCommand("ACCELERATE " + str(angle) + " " + str(magnitude))

  def setBomb(self, pos, delay):
    #requires delay: >=20 in frames where 1 frame = 25milsecond
    self.sendCommand("BOMB " + str(pos[0]) + " " + str(pos[1]) + " " + str(delay))
  
  def waypoint(self, target): #fly through this point exactly. blocks until done.
    print("Waypointing to ", target)
    while squaredDistance(self.data["pos"], target) > 25: # and squaredDistance(self.data["pos"], target) < 500**2:
      self.refreshData()
      diff = sub(target, self.data["pos"])
      vel = self.data["vel"]
      #self.setAccel(angle(sub(vel, scale(2, perp(diff, vel)))), min(1, math.sqrt(squaredDistance(diff))/50))
      self.setAccel(angle(add(neg(perp(diff, vel)), scale(1/math.sqrt(squaredDistance(diff)),diff))), 1)

  def Bomb(self):
    vel = p.data["vel"]
    bombdist = scale(50/math.sqrt(squaredDistance(vel)),vel)
    p.setAccel(angle(vel), 1)
    print('Aye I''m moving')
    p.setBomb(add(p.data["pos"], bombdist), 20)
    print('YARRRRR')

try:
  with Player(HOST, PORT, USERNAME, PASSWORD) as p:
    while True:
      p.refreshData()
      if len(p.data["mines"]) > 0:
        p.waypoint(p.data["mines"][0])
      else:
        p.Bomb()
except Exception as e:
  print("Error", str(e))
