print("This AStar module is NOT good, it was a simple port of an old lua version")

import math
import time
from .heap import Heap


def getNodeDist(nodeA, nodeB):
	dstX = abs(nodeA["x"] - nodeB["x"])
	dstY = abs(nodeA["y"] - nodeB["y"])

	if dstX > dstY:
		return 14*dstY + 10* (dstX-dstY)
	return 14*dstX + 10 * (dstY-dstX)


def clamp(inputVal, minVal, maxVal):
    return max(min(inputVal, maxVal), minVal)


def getWorldPoints(fixture, points=None, connectFirstPoint=True):
    def __rotate(origin, point, angle):
        # Copy From Physics Module!
        ox, oy = origin
        px, py = point

        qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
        qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
        return qx, qy

    # Copy From Physics Module!
    if points is None:
        points = fixture.shape.vertices
    newPoints = []
    for point in points:
        newPoints.append(__rotate((fixture.body.position.x, fixture.body.position.y), (point[0] + fixture.body.position.x, point[1] + fixture.body.position.y), fixture.body.angle))
    if connectFirstPoint is True:
        newPoints.append((newPoints[0][0], newPoints[0][1]))
    return newPoints


def isInside(minX,minY,maxX,maxY,inputX,inputY):
    if inputX >= minX and inputX <= maxX and inputY >= minY and inputY <= maxY:
        return True
    else:
        return False


def CompareTo(a, b):
    if a > b: return 1
    if a == b: return 0
    if a < b: return -1


class AStar:
    def __init__(self, minX, minY, maxX, maxY, nodeSize=10):
        self.grid = []
        self.minX = minX
        self.minY = minY
        self.maxX = maxX
        self.maxY = maxY
        self.nodeSize = nodeSize
        self.gridWidth = self.maxX-self.minX
        self.gridHeight = self.maxY-self.minY
        self.gridSizeX = int(self.gridWidth/self.nodeSize)
        self.gridSizeY = int(self.gridHeight/self.nodeSize)
        self.gridImageSurface = None
        self.gridImage = None


    def getNeighbours(self, x1, y1):
        neighbours = []
        x = -2
        while x <= 0:
            x = x + 1
            y = -2
            while y <= 0:
                y = y + 1
                if x == 0 and y == 0:
                    pass
                else:
                    checkX = x1 + x
                    checkY = y1 + y

                    if checkX >= 0 and checkX < self.gridSizeX and checkY >= 0 and checkY < self.gridSizeY:
                        if self.grid[checkX] != None and self.grid[checkX][checkY] != None:
                            neighbours.append(self.grid[checkX][checkY])

        return neighbours


    def getWorldPos(self, x, y, offsetX=0.001, offsetY=0.001):
        if offsetX == 0.001:
            offsetX = self.minX
        if offsetY == 0.001:
            offsetY = self.minY
        return (x-1) * self.nodeSize + offsetX, (y-1) * self.nodeSize + offsetY


    def getGridPos(self, x, y):
        percentX = (x + (self.gridWidth/2)) / self.gridWidth - 1
        percentY = (y + (self.gridHeight/2)) / self.gridHeight - 1

        #percentX = clamp(percentX, 0, 1-0.0000000000000001)
        #percentY = clamp(percentY, 0, 1-0.0000000000000001)

        return int((self.gridSizeX) * percentX), int((self.gridSizeY) * percentY)


    def checkCollision(self, objects, x, y):
        wx, wy = self.getWorldPos(x,y)

        for obj in objects:
            if obj["walkable"] == False:
                xy1, xy2, xy3, xy4 = getWorldPoints(obj["fixture"], connectFirstPoint=False)
                x1, y1, x3, y3 = *xy1, *xy3

                if isInside(x1-self.nodeSize,y1-self.nodeSize,x3,y3,wx,wy):
                    return False

        return True


    def genGrid(self, objects):
        self.grid = []
        self.gridImageSurface = None
        self.gridImage = None

        for x in range(0,self.gridSizeX):
            self.grid.append([])
            for y in range(0,self.gridSizeY):
                self.grid[x].append({"walkable":self.checkCollision(objects,x,y), "x":x, "y":y, "gCost":0, "hCost":0})


    def updateGird(self, objects): #TODO Test
        for x in range(0,self.gridSizeX):
            for y in range(0,self.gridSizeY):
                self.grid[x][y]["walkable"] = self.checkCollision(objects,x,y)


    def drawGrid(self, gSelf, drawX=0, drawY=0):
        if self.gridImage is None:
            self.gridImageData = gSelf.graphics.newImageData(self.gridSizeX * self.nodeSize, self.gridSizeY * self.nodeSize)
            for x in range(0,self.gridSizeX):
                for y in range(0,self.gridSizeY):
                    if self.grid[x][y]["walkable"] is True:
                        self.gridImageData.rectangle(x * self.nodeSize - self.nodeSize, y * self.nodeSize - self.nodeSize, self.nodeSize, self.nodeSize, 0, 255, 0, 255, mode="line")
                    else:
                        self.gridImageData.rectangle(x * self.nodeSize - self.nodeSize, y * self.nodeSize - self.nodeSize, self.nodeSize, self.nodeSize, 255, 0, 0, 255, mode="line")
            self.gridImage = gSelf.graphics.newImage(self.gridImageData)
        else:
            gSelf.graphics.draw(self.gridImage, drawX, drawY)


    def heapCompFunc(self, a, b):
        fCostA = a["gCost"] + a["hCost"]
        fCostB = b["gCost"] + b["hCost"]

        # a["fCost"] < b["fCost"]
        # OR
        # a["fCost"] == b["fCost"]
        # AND
        # a["hCost"] < b["hCost"]

        #if fCostA < fCostB or fCostA == fCostB and a["hCost"] < b["hCost"]:
        #    return True
        #else:
        #    return False

        compare = CompareTo(fCostA, fCostB)
        if compare == 0:
            compare = CompareTo(a["hCost"], b["hCost"])

        return -compare


    def findPath(self, startPos, targetPos):
        snX, snY = self.getGridPos(startPos[0], startPos[1])
        startNode = self.grid[snX][snY]
        tnX, tnY = self.getGridPos(targetPos[0], targetPos[1])
        targetNode = self.grid[tnX][tnY]

        self.lastStartNode = startNode
        self.lastTargetNode = targetNode
        self.lastSearchedNodes = []
        self.lastExploredNodes = []

        closedNodes = []
        openNodesHeap = Heap(self.heapCompFunc)

        openNodesHeap.push(startNode)

        while len(openNodesHeap) > 0:
            time.sleep(0.01)
            currentNode = openNodesHeap.pop()

            closedNodes.append(currentNode)

            if currentNode is targetNode:
                return self.retraceNodePath(startNode, targetNode), None

            for v in self.getNeighbours(currentNode["x"], currentNode["y"]):
                self.lastExploredNodes.append(v)
                if v["walkable"] is False or v in closedNodes:
                    pass #Skip To Next Neighbour
                else:
                    newMovmentCostToNeighbour = currentNode["gCost"] + getNodeDist(currentNode, v)
                    if newMovmentCostToNeighbour < v["gCost"] or v not in openNodesHeap.heap:
                        v["gCost"] = newMovmentCostToNeighbour
                        v["hCost"] = getNodeDist(v, targetNode)
                        v["parent"] = currentNode

                        self.lastSearchedNodes.append(v)

                        if v not in openNodesHeap.heap:
                            openNodesHeap.push(v)

        return [], "Can Not Reach Target"


    def retraceNodePath(self, startNode, Node):
        path = []
        orderedPath = []
        currentNode = Node

        while currentNode is not startNode:
            path.append(currentNode)
            currentNode = currentNode["parent"]

        for v in reversed(path):
            orderedPath.append(v)

        return orderedPath
