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

    def getRelAngle(self,y,x,boat_dir_deg):
        raw = abs(boat_dir_deg - self.getLocalWind(y,x)[2])
        rel_angle = min(raw, 360 - raw)
        return rel_angle

    def checkNoGo(self,y,x,boat_dir_deg):
        if self.getRelAngle(y,x,boat_dir_deg) < 30:
            return True
        else:
            return False

    def getSpeedFactor(self,y,x,boat_dir_deg):
        speed_factor = polarFactor(self.getRelAngle(y,x,boat_dir_deg))
        return speed_factor

    def getDirSpeed(self,y,x): #dir, speed
        windDir = self.mapData["windDir"][y-1][x-1]
        windSpeed = self.mapData["windSpeed"][y-1][x-1]
        return windDir, windSpeed

    def checkValidMove(self,vector):
        valid = False
        if self.boatDir is None:
            valid = True
        self.boatDir = getCircleAngle(vector)
        p2y = self.boatPos[0]+vector[0]
        p2x = self.boatPos[1]+vector[1]
        self.boatPos = [p2y, p2x]
        if valid:
            return True
        else:
            return relative_wind_angle(self.boatDir, self.getDirSpeed(p2y,p2x)[0]) >= 30

    def getPossibleMoves(self,y,x):
        return

def main():
    mapData, meta = readMap("map_1_Training") #readMap(input("Map filename: "))
    pathfinder = Pathfinder(mapData, meta)
    print(pathfinder.checkValidMove([-1,1]))
    print(pathfinder.checkValidMove([-1,1]))

if __name__ == "__main__":
    main()