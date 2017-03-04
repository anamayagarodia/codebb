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
def distance(pos1, pos2 = (0,0)):
  return math.sqrt(squaredDistance(pos1, pos2))
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
def norm(vec):
  return scale(1/distance(vec), vec)

class Player:
  def __init__(self, HOST, PORT, USERNAME, PASSWORD):
    self.visited = set()
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
  def processData(self, response, isStatus = True):
    arr = response.split(' ')
    print(arr)
    
    self.rawData = arr
    
    processed = dict()
    if isStatus:
      processed["pos"] = (float(arr[1]), float(arr[2]))
      processed["vel"] = (float(arr[3]), float(arr[4]))
    else:
      processed["pos"] = self.data["pos"]
      processed["vel"] = self.data["vel"]
    processed["ourmines"] = list()
    processed["mines"] = list()
    processed["players"] = list()
    processed["bombs"] = list()
    
    if isStatus:
      counter = 7
    else:
      counter = 3
    nummines = int(arr[counter])
    for i in range(nummines): #x, y, owner (ONLY IF NOT OURS)
      next = (float(arr[counter + 2 + 3*i]), float(arr[counter + 3 + 3*i]), arr[counter + 1 + 3*i])
      if arr[counter + 1 + 3*i] != self.USERNAME:
        processed["mines"].append(next)
      else:
        processed["ourmines"].append(next)
      self.visited.add(next)
    
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
    
    return processed
  def refreshData(self):
    response = self.sendCommand('STATUS')
    self.data = self.processData(response)
  def setAccel(self, angle, magnitude):
    self.sendCommand("ACCELERATE " + str(angle) + " " + str(magnitude))
  
  def setBomb(self, pos, delay):
    #requires delay: >=20 in frames where 1 frame = 25milsecond
    self.sendCommand("BOMB " + str(pos[0]) + " " + str(pos[1]) + " " + str(delay))

  def scanXY(self, pos):
    response = self.sendCommand("SCAN " + str(pos[0]) + " " + str(pos[1]))
    if response.find("ERROR") == -1:
      return self.processData(response, False)
    else:
      return None
  
  def isOurMine(self, minepos):
    for mine in self.data["ourmines"]:
      if minepos[0] == mine[0] and minepos[1] == mine[1]:
        return True
    return False
  
  def shortestVectorTo(self, target):
    vec = sub(target, self.data["pos"])
    minLen = squaredDistance(vec)
    minVec = vec
    
    vec = sub(target, sub(self.data["pos"],(10000,0)))
    if squaredDistance(vec) < minLen:
      minLen = squaredDistance(vec)
      minVec = vec
    
    vec = sub(target, sub(self.data["pos"],(0,10000)))
    if squaredDistance(vec) < minLen:
      minLen = squaredDistance(vec)
      minVec = vec
    
    vec = sub(target, sub(self.data["pos"],(10000,10000)))
    if squaredDistance(vec) < minLen:
      minLen = squaredDistance(vec)
      minVec = vec
    
    return minVec
  
  def waypoint(self, target): # fly through this point exactly. blocks until done.
    vecTo = self.shortestVectorTo(target)
    print("Waypointing to ", target, " which is at angle ", angle(vecTo), " from me")
    while squaredDistance(vecTo) > 25 and not self.isOurMine(target):
      self.refreshData()
      vecTo = self.shortestVectorTo(target)
      vel = self.data["vel"]
      self.setAccel(angle(add(neg(perp(vecTo, vel)), scale(1/distance(vecTo),vecTo))), 1)
    self.visited.add(target)
  
  def bombAccel(self):
    vel = self.data["vel"]
    
    if(distance(vel) == 0):
      self.setAccel(0.3, 1)
    else:
      self.setAccel(angle(vel), 1)
      
      bombdist = scale(50/math.sqrt(squaredDistance(vel)),vel)
      if math.sqrt(squaredDistance(vel)) <= 9.75:
        self.setBomb(add(self.data["pos"], bombdist), 20)
      
      scanCoords = add(scale(200, norm(self.data["vel"])), self.data["pos"])
      scanResults = self.scanXY(scanCoords)
      if scanResults != None and len(scanResults["mines"]) > 0:
        self.waypoint(scanResults["mines"][0])

# So memory.
  # We are going to explore the map in an optimal way (with motion and with scans).
    # The goal is to find 75% of the existing mines.
  # Once this occurs, we switch to a strategy of circulation
    # Waypointing each mine in sequence, something something TSP.

# allow waypointing to other things on the way? not seeing anything while waypointing - have a queue
# remember past points and check them at some point - after we hit a set number of "seen" bombs in the set (sortedset based on distance from current?)
# if waypoint keep going
# bomb it if people are nearby (or leave a parting bomb)
# sidescan
# predictive bomb positioning - for ourselves and for others
# stop dropping bombs at terminal velocity
#('Error', "invalid literal for float(): 3750'")

try:
  with Player(HOST, PORT, USERNAME, PASSWORD) as p:
    p.setAccel(0.3, 1)
    time.sleep(1)
    while True:
      p.refreshData()
      print(math.sqrt(squaredDistance(p.data["vel"])))
      if len(p.data["mines"]) > 0:
        p.waypoint(p.data["mines"][0])
      else:
        p.bombAccel()
except Exception as e:
  print("Error", str(e))

