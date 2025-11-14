import json

def readMap(mapFilename):
    with open(mapFilename + ".json") as f:
        mapData = json.load(f)
    with open(mapFilename + "_meta.json") as f:
        meta = json.load(f)
    return mapData, meta

def getCircleAngle(circleVector):
    circleVects = [[-1,0],
                [-1,1],
                [0,1],
                [1,1],
                [1,0],
                [1,-1],
                [0,-1],
                [-1,-1]]
    circleAngles = [0,45,90,135,180,225,270,315]
    return circleAngles[circleVects.index(circleVector)]

class Pathfinder:
    def __init__(self, mapData, meta):
        self.mapData = mapData
        self.startPos = meta["startPos"]
        self.endPos = meta["finishPos"]
        self.rows = meta["rows"]
        self.cols = meta["cols"]
        self.boat = self.startPos

    def getDirSpeed(self,y,x): #dir, speed
        windDir = self.mapData["windDir"][y][x]
        windSpeed = self.mapData["windSpeed"][y][x]
        return windDir, windSpeed

    def checkValidMove(self,vector):
        valid = True
        p1Dir = getCircleAngle(vector)
        p2Dir = self.getDirSpeed(self.boat[0]+vector[0],self.boat[1]+vector[1])[0]
        print(p1Dir, p2Dir)
        return valid

    def getPossibleMoves(self,y,x):
        return

def main():
    mapData, meta = readMap("map_1_Training") #readMap(input("Map filename: "))
    pathfinder = Pathfinder(mapData, meta)
    print(pathfinder.checkValidMove([-1,0]))

if __name__ == "__main__":
    main()


    