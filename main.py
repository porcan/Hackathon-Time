import json

def readMap(mapFilename):
    with open(mapFilename + ".json") as f:
        mapData = json.load(f)
    with open(mapFilename + "_meta.json") as f:
        meta = json.load(f)
    return mapData, meta

class Pathfinder:
    def __init__(self, mapData, meta):
        self.mapData = mapData
        self.startPos = meta["startPos"]
        self.endPos = meta["finishPos"]
        self.rows = meta["rows"]
        self.cols = meta["cols"]

    def getDirSpeed(self,y,x): #dir, speed
        windDir = self.mapData["windDir"][y][x]
        windSpeed = self.mapData["windSpeed"][y][x]
        return windDir, windSpeed

    def checkValidMove(self,y,x,vector):
        p1Data = self.getDirSpeed(y,x)
        p2Data = self.getDirSpeed(y+vector[0],x+vector[1])
        print(p1Data, p2Data)
        return

    def getPossibleMoves(self,y,x):
        return

def main():
    mapData, meta = readMap(input("Map filename: "))
    pathfinder = Pathfinder(mapData, meta)
    print(pathfinder.getDirSpeed(29,2))

if __name__ == "__main__":
    main()

    
    