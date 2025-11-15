import json
import math

def readMap(mapFilename):
    with open(mapFilename + ".json") as f:
        mapData = json.load(f)
    with open(mapFilename + "_meta.json") as f:
        meta = json.load(f)
    return mapData, meta

def getCircleAngle(v):
    dy, dx = v
    angle = math.degrees(math.atan2(dx, -dy))
    return angle % 360

def polarFactor(rel_deg):
    if rel_deg >= 30 and rel_deg < 60:
        f = 1.0
    elif rel_deg >= 60 and rel_deg < 90:
        f = 0.95
    elif rel_deg >= 90 and rel_deg < 135:
        f = 0.85
    elif rel_deg >= 135 and rel_deg <= 180:
        f = 0.70
    else:
        f = 0
    return f

def relative_wind_angle(boat_dir, wind_dir):
    diff = (wind_dir - boat_dir) % 360
    return abs(diff - 180)

compassDirs = {0 : "N",
               45 : "NE",
               135 : "SE",
               180 : "S",
               225 : "SW",
               315 : "NW"}

class Node:
    def __init__(self, y, x, parent, vector):
        self.y = y
        self.x = x
        self.parent = parent
        self.vector = vector

    def __eq__(self, other):
        return isinstance(other, Node) and self.y == other.y and self.x == other.x

    def __hash__(self):
        return hash((self.y, self.x))

class Pathfinder:
    def __init__(self, mapData, meta):
        self.mapData = mapData
        self.startPos = meta["startPos"]
        self.endPos = meta["finishPos"]
        self.rows = meta["rows"]
        self.cols = meta["cols"]
        self.boatPos = self.startPos
        self.boatDir = None

    def getLocalWind(self,y,x):
        W = self.getDirSpeed(y,x)[0]
        w_to = self.getDirSpeed(y,x)[1]
        w_from = (w_to + 180) % 360
        return W, w_to, w_from

    def getSpeedFactor(self,y,x,boat_dir_deg):
        speed_factor = polarFactor(relative_wind_angle(self.getDirSpeed(y,x)[0],boat_dir_deg))
        return speed_factor

    def getDirSpeed(self,y,x):
        windDir = self.mapData["windDir"][y-1][x-1]
        windSpeed = self.mapData["windSpeed"][y-1][x-1]
        return windDir, windSpeed

    def checkValidMove(self, node, vector):
        ny = node.y + vector[0]
        nx = node.x + vector[1]
        new_dir = getCircleAngle(vector)
        if node.vector is None:
            return True
        wind_dir = self.getDirSpeed(ny, nx)[0]
        return relative_wind_angle(new_dir, wind_dir) >= 30

    def getPossibleMoves(self, node):
        boat_y, boat_x = node.y, node.x
        vectors = [[-1,0],[-1,1],[1,1],[1,0],[1,-1],[-1,-1]]
        possible = []
        for vector in vectors:
            ny, nx = boat_y + vector[0], boat_x + vector[1]
            if 0 < ny < self.rows+1 and 0 < nx < self.cols+1:
                if self.checkValidMove(node, vector):
                    possible.append(vector)
        return possible
    
    def applyMove(self, vector):
        self.boatDir = getCircleAngle(vector)
        self.boatPos = [self.boatPos[0] + vector[0],
                        self.boatPos[1] + vector[1]]
        
    def search(self):
        frontier = []
        explored = []
        current = Node(self.startPos[0], self.startPos[1], None, None)
        while not (current.y == self.endPos[0] and current.x == self.endPos[1]):
            explored.append(current)
            self.boatPos = [current.y, current.x]
            vectors = self.getPossibleMoves(current)
            for vector in vectors:
                new = Node(self.boatPos[0]+vector[0], self.boatPos[1]+vector[1], current, vector)
                if not (new in explored or new in frontier):
                    frontier.append(new)

            if len(frontier) == 0:
                return None
            
            current = frontier.pop(0)
        print("found route")
        path = []
        while current.parent is not None:
            path.append(current.vector)
            current = current.parent
        #path.append(current.vector)

        route = ""
        for item in reversed(path):
            route = route + compassDirs[int(getCircleAngle(item))]
            route = route + "\n"
        route = route[:len(route)-1]
        
        file = open("route.txt","w")
        file.write(route)

def main(): 
    mapData, meta = readMap("map_2_Main") #readMap(input("Map filename: "))
    pathfinder = Pathfinder(mapData, meta)
    pathfinder.search()

if __name__ == "__main__":
    main()