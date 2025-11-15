import json
import time
import math

def readMap(mapFilename):
    with open(mapFilename + ".json") as f:
        mapData = json.load(f)
    with open(mapFilename + "_meta.json") as f:
        meta = json.load(f)
    return mapData, meta

def relativeAngle(boatDir, windDir):
    diff = (windDir - boatDir) % 360
    return abs(diff - 180)

def getCircleAngle(v):
    dy, dx = v
    angle = math.degrees(math.atan2(dx, -dy))
    return angle % 360

def windFrom(windDir):
    return (windDir + 180) % 360

compassDirs = {0   : "N",
               45  : "NE",
               135 : "SE",
               180 : "S",
               225 : "SW",
               315 : "NW"}

def costFunction(newHeading, boatHeading, windFrom):
   
    #newHeading is the new angle you want the boat to be heading at
    #boatHeading is the angle you want the boat to be heading at
    #windForm is the windDirectionAngle + 180 (mod 360)

    move = True
    localWindSpeed = 30
    boatSpeed = 0
    speedFactor = 0
    turnPenalty = 0
    changeInHeading = abs(newHeading - boatHeading)
    baseTime = 10 
    actualAngle = abs(boatHeading - windFrom)

    attackAngle = min(actualAngle, 360 - actualAngle)

    if actualAngle < 30:
        move = False
        return 100000000
    else:
        if 30 <= attackAngle < 60 :
            speedFactor = 1
        elif 60 <= attackAngle < 90 :
            speedFactor = 0.95
        elif 90 <= attackAngle < 135 :
            speedFactor = 0.85
        elif 135 <= attackAngle < 180 :
            speedFactor = 0.7
        else:
            speedFactor = 0
    
    boatSpeed = localWindSpeed * speedFactor

    changeInHeading = min(changeInHeading, 360 - changeInHeading)

    if changeInHeading == 0:
        timePenalty = 0
    if 0 < changeInHeading <= 10:
        timePenalty = 0.5
    if 10 < changeInHeading <= 20 :
        timePenalty = 1
    if 20 < changeInHeading <= 30:
        timePenalty = 1.5
    if 30 < changeInHeading <= 40:
        timePenalty = 2
    if 40 < changeInHeading <= 50:
        timePenalty = 2.5
    if 50 < changeInHeading < 60:
        timePenalty = 3
    if changeInHeading >= 60: 
        timePenalty = 4
    
    timeForEachMove = (baseTime/(boatSpeed + 0.00001)) + timePenalty
    return timeForEachMove

class Pathfinder:
    def __init__(self, mapData, meta):
        self.mapData = mapData
        self.meta    = meta
        self.maxY    = meta["rows"]
        self.maxX    = meta["cols"]
        self.start   = meta["startPos"]
        self.end     = meta["finishPos"]

    def windDir(self, y, x):
        return self.mapData["windDir"][y-1][x-1]
    
    def windSpeed(self, y, x):
        return self.mapSpeed["windSpeed"][y-1][x-1]

    def getValidMoves(self, y, x):
        vectors = [[-1,0],[-1,1],[1,1],[1,0],[1,-1],[-1,-1]]
        valid = []
        for vector in vectors:
            ny, nx = y + vector[0], x + vector[1]
            if (0 < ny <= self.maxY) and (0 < nx <= self.maxX):
                windDir = self.windDir(ny, nx)
                boatDir = getCircleAngle(vector)
                if relativeAngle(boatDir, windDir) >= 30:
                    valid.append(vector)
        return valid
    
    def search(self):
        current = self.start
        path = []
        prevBoatDir = 45
        while not current == self.end:
            moves = self.getValidMoves(current[0], current[1])
            if len(moves) == 0:
                moves = [[-1,0],[-1,1]]

            #find lowest cost move
            lowestCost = 1000000000000
            for move in moves:
                newWindFrom = windFrom(self.windDir(current[0] + move[0], current[1] + move[1]))
                cost = costFunction(getCircleAngle(move), prevBoatDir, newWindFrom)
                if cost < lowestCost:
                    lowestCost = cost
                    bestMove = move
                
            print(compassDirs[int(getCircleAngle(bestMove))])
            path.append(bestMove)
            prevBoatDir = getCircleAngle(bestMove)
            current[0] += bestMove[0]
            current[1] += bestMove[1]
        route = ""
        for item in path:
            route = route + compassDirs[int(getCircleAngle(item))]
            route = route + "\n"
        route = route[:len(route)-1]
        file = open("route.txt","w")
        file.write(route)

def main():
    mapData, meta = readMap("map_2_Main")
    pathfinder = Pathfinder(mapData, meta)
    print(pathfinder.search())

if __name__ == "__main__":
    main()