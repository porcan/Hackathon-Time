import json

def readMap(mapFilename):
    with open(mapFilename + ".json") as f:
        mapData = json.load(f)
    with open(mapFilename + "_meta.json") as f:
        meta = json.load(f)
    return mapData, meta

def getCircleAngle(v):
    if v == [-1,0]:
        return 0
    elif v == [-1,1]:
        return 45
    elif v == [0,1]:
        return 90
    elif v == [1,1]:
        return 135
    elif v == [1,0]:
        return 180
    elif v == [1,-1]:
        return 225
    elif v == [0,-1]:
        return 270
    elif v == [-1,-1]:
        return 315

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
        if self.boatDir is not None:
            ang = relative_wind_angle(self.boatDir, getCircleAngle([p2y,p2x]))
        if not valid:
            print(ang)
            return not self.checkNoGo(p2y,p2x,self.boatDir)
        return True

    def getPossibleMoves(self,y,x):
        return

def main():
    mapData, meta = readMap("map_1_Training") #readMap(input("Map filename: "))
    pathfinder = Pathfinder(mapData, meta)
    print(pathfinder.getDirSpeed(29,2))
    print(pathfinder.getDirSpeed(18,2))
    print(pathfinder.checkValidMove([-1,1]))
    print(pathfinder.checkValidMove([-1,1]))

if __name__ == "__main__":
    main()