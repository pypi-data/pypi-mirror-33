import math
from Box2D import *

class Physics:
    def __init__(self, gameRef):
        self.game = gameRef


    def __rotate(self, origin, point, angle):
        """
        Rotate a point counterclockwise by a given angle around a given origin.

        The angle should be given in radians.
        """
        ox, oy = origin
        px, py = point

        qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
        qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
        return qx, qy


    def newWorld(self, xg=0, yg=0, sleep=True):
        """
        Creates a new world for physics so be applyed in

        make shure to use updateWorld(world, dt)

        world = newWorld()
        """
        return b2World(gravity=(xg, yg), doSleep=sleep)


    def newBody(self, world, x, y, type="dynamic"):
        if type == "static":
            return world.CreateStaticBody(position=(x, y), type=type)
        elif type == "dynamic":
            return world.CreateDynamicBody(position=(x, y), type=type)
        elif type == "kinematic":
            return world.CreateKinematicBody(position=(x, y), type=type)
        else:
            TypeError("Wrong type `newBody`: " + type)


    def newFixture(self, body, shape, density=1):
        return body.CreateFixture(shape=shape, density=density)


    def newRectangleShape(self, width, height):
        return b2PolygonShape(vertices=[(0, 0), (width, 0), (width, height), (0, height), (0, 0)])


    def newCircleShape(self, r):
        return b2CircleShape(radius=r)


    def newPolygonShape(self, verts):
        return b2PolygonShape(vertices=verts)


    def createObject(self, world, x, y, shapeData, pType="dynamic", density=1):
        """
        Returns a Dict
        Body
        Shape
        Fixture

        shapeData
        TUPLE(width, height) = rectangle shape
        INT radius = cirlce shape
        LIST = polygon (AKA list of vertices)
        """
        shape = None

        body = self.newBody(world, x, y, pType)

        if type(shapeData) is tuple:
            shape = self.newRectangleShape(shapeData[0], shapeData[1])
        elif type(shapeData) is int:
            shape = self.newCircleShape(shapeData)
        elif type(shapeData) is list:
            shape = self.newPolygonShape(vertices=shapeData)

        fixture = self.newFixture(body, shape, density)

        return {
            "body":body,
            "shape":shape,
            "fixture":fixture
        }


    def getPoints(self, fixture, connectFirstPoint=True):
        """
        Gets the points of an object starting at 0,0

        someListOfTuples = getPoints(someFixture, connectFirstPoint=False)
        """
        vertices = []

        for point in fixture.shape.vertices:
            vertices.append(self.__rotate((0, 0), (point[0], point[1]), fixture.body.angle))

        if connectFirstPoint is True:
            vertices.append((vertices[0][0], vertices[0][1]))
            return vertices
        else:
            return vertices


    def getWorldPoints(self, fixture, connectFirstPoint=True):
        """
        IF fixture is arg
        Gets the points of an object starting at body position fixture is attached to

        someListOfTuples = getWorldPoints(someFixture, connectFirstPoint=False)
        """
        # Also Used In extras.AStar
        points = fixture.shape.vertices
        newPoints = []
        for point in points:
            newPoints.append(self.__rotate((fixture.body.position.x, fixture.body.position.y), (point[0] + fixture.body.position.x, point[1] + fixture.body.position.y), fixture.body.angle))
        if connectFirstPoint is True:
            newPoints.append((newPoints[0][0], newPoints[0][1]))
        return newPoints


    def updateWorld(self, world, dt, velocityiterations=8, positioniterations=3):
        world.Step(dt, velocityiterations, positioniterations)
