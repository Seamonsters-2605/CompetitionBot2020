import math, coordinates, drivetrain
from autoScheduler import Action
import seamonsters as sea

def driveToPoint(pathFollower, coord, speed, rotateAtTheEnd=False):
    drivetrain.mediumVelocityGear.applyGear(pathFollower.drive)

    if coord in coordinates.targetPoints:
        rotateAtTheEnd = True

    angle = None
    if rotateAtTheEnd:
        angle = coord.angle

    yield from sea.ensureTrue(
        pathFollower.driveToPointGenerator(coord.x, coord.y, angle, speed, 1, math.radians(5)), 25)

def createDriveToPointAction(pathFollower, coord, speed):
    return Action("Drive to " + coord.name,
        lambda: driveToPoint(pathFollower, coord, speed), "drive", coord)

def rotateInPlace(pathFollower, angle):
    coord = coordinates.FieldCoordinate("Rotated",
        pathFollower.robotX, pathFollower.robotY, angle)
    yield from driveToPoint(pathFollower, coord, 2, True)

def createRotateInPlaceAction(pathFollower, coord):
    return Action("Rotate to " + str(round(math.degrees(coord.angle))),
        lambda: rotateInPlace(pathFollower, coord.angle), "rotate", coord)

def waitOneSecond():
    yield from sea.wait(sea.ITERATIONS_PER_SECOND)

def endAuto(robot):
    yield
    robot.manualMode()

def createEndAction(robot):
    return Action("END", lambda: endAuto(robot), 0)

def setRobotPosition(pathFollower, coord):
    yield
    pathFollower.setPosition(coord.x, coord.y, coord.angle)

def createSetRobotPositionAction(pathFollower, coord):
    return Action("Set Starting Position", 
        lambda: setRobotPosition(pathFollower, coord), "set", coord)

# generic actions have a key that is the same as the index in the list
# so they can be recreated easily by the auto preset opener
def createGenericAutoActions(robot):
    return [
        createEndAction(robot),
        Action("Wait 1 sec", waitOneSecond, 1)
    ]